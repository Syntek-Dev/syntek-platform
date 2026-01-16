"""Unit tests for GraphQL TOTP (2FA) mutations.

Tests cover:
- 2FA setup mutation (setup_2fa)
- 2FA confirmation mutation (confirm_2fa)
- 2FA device removal mutation (remove_2fa_device)
- Backup code regeneration mutation (regenerate_2fa_backup_codes)
- 2FA disable mutation (disable_2fa)
- 2FA status query (two_factor_status)
- 2FA devices query (two_factor_devices)

Implements test requirements for:
- C2: TOTP secret encryption using Fernet
- H13: Multiple TOTP devices with naming
- H14: Backup code hashing
- M3: Improved backup code format (XXXX-XXXX-XXXX)
- M6: TOTP time window tolerance (±1 period)
"""

from django.contrib.auth import get_user_model

import pyotp
import pytest

from apps.core.models import BackupCode, TOTPDevice
from apps.core.services.token_service import TokenService
from apps.core.services.totp_service import TOTPService
from tests.factories import OrganisationFactory, UserFactory

User = get_user_model()


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestSetup2FAMutation:
    """Test GraphQL setup_2fa mutation."""

    @pytest.fixture
    def authenticated_user_and_token(self, db):
        """Provide authenticated user and JWT token.

        Returns:
            Tuple of (user, access_token)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("SecureP@ss1847!#")
        user.save()

        tokens = TokenService.create_tokens(user)
        return user, tokens["access_token"]

    def test_setup_2fa_creates_device_and_backup_codes(
        self, client, authenticated_user_and_token
    ) -> None:
        """Test 2FA setup creates device with encrypted secret and backup codes.

        Given: Authenticated user without 2FA enabled
        When: setup_2fa mutation is called with device name
        Then: TOTP device is created with encrypted secret (C2)
        And: QR codes are generated (SVG and data URI)
        And: 10 backup codes are generated in XXXX-XXXX-XXXX format (M3)
        And: Backup codes are stored as hashes (H14)
        """
        user, token = authenticated_user_and_token

        mutation = """
        mutation Setup2FA($input: Setup2FAInput!) {
            setup2fa(input: $input) {
                device {
                    id
                    name
                    isConfirmed
                    createdAt
                }
                secret
                qrCodeSvg
                qrCodeDataUri
                backupCodes
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"deviceName": "iPhone 14"}},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["setup2fa"]

        # Verify device was created
        assert result["device"]["name"] == "iPhone 14"
        assert result["device"]["isConfirmed"] is False
        assert result["device"]["id"] is not None

        # Verify secret is returned (plain text for QR code display)
        assert result["secret"] is not None
        assert len(result["secret"]) == 32  # Base32 encoded secret

        # Verify QR codes are generated
        assert result["qrCodeSvg"].startswith("<?xml") or "<svg" in result["qrCodeSvg"]
        assert result["qrCodeDataUri"].startswith("data:image/svg+xml;base64,")

        # Verify backup codes (M3 format: XXXX-XXXX-XXXX)
        assert len(result["backupCodes"]) == 10
        for code in result["backupCodes"]:
            assert len(code) == 14  # XXXX-XXXX-XXXX
            assert code[4] == "-" and code[9] == "-"

        # Verify backup codes are stored as hashes (H14)
        backup_codes_db = BackupCode.objects.filter(user=user)
        assert backup_codes_db.count() == 10
        for bc in backup_codes_db:
            assert len(bc.code_hash) == 64  # SHA-256 hex digest

        # Verify secret is encrypted in database (C2)
        device = TOTPDevice.objects.get(user=user)
        assert device.secret != result["secret"].encode()  # Should be encrypted
        # Verify we can decrypt and get the same secret
        assert device.get_secret() == result["secret"]

    def test_setup_2fa_supports_multiple_devices(
        self, client, authenticated_user_and_token
    ) -> None:
        """Test user can set up multiple named TOTP devices (H13).

        Given: User with one TOTP device
        When: setup_2fa mutation is called with different device name
        Then: Second device is created
        And: Both devices are available for authentication
        """
        user, token = authenticated_user_and_token

        mutation = """
        mutation Setup2FA($input: Setup2FAInput!) {
            setup2fa(input: $input) {
                device {
                    id
                    name
                }
            }
        }
        """

        # Create first device
        response1 = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"deviceName": "iPhone"}},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data1 = response1.json()
        assert "errors" not in data1 or data1["errors"] is None
        device1_id = data1["data"]["setup2fa"]["device"]["id"]

        # Create second device
        response2 = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"deviceName": "Android Tablet"}},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data2 = response2.json()
        assert "errors" not in data2 or data2["errors"] is None
        device2_id = data2["data"]["setup2fa"]["device"]["id"]

        # Verify both devices exist
        assert device1_id != device2_id
        assert TOTPDevice.objects.filter(user=user).count() == 2

    def test_setup_2fa_requires_authentication(self, client) -> None:
        """Test 2FA setup requires authentication.

        Given: Unauthenticated request
        When: setup_2fa mutation is called
        Then: Error is returned with code NOT_AUTHENTICATED
        """
        mutation = """
        mutation Setup2FA($input: Setup2FAInput!) {
            setup2fa(input: $input) {
                device {
                    id
                }
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"deviceName": "Test"}},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "NOT_AUTHENTICATED" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestConfirm2FAMutation:
    """Test GraphQL confirm_2fa mutation."""

    @pytest.fixture
    def user_with_unconfirmed_device(self, db):
        """Provide user with unconfirmed TOTP device.

        Returns:
            Tuple of (user, access_token, device, plain_secret)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("SecureP@ss1847!#")
        user.save()

        tokens = TokenService.create_tokens(user)

        # Create unconfirmed device
        device, plain_secret = TOTPService.create_device(user, "Test Device")

        return user, tokens["access_token"], device, plain_secret

    def test_confirm_2fa_with_valid_token(self, client, user_with_unconfirmed_device) -> None:
        """Test 2FA confirmation with valid TOTP token.

        Given: User with unconfirmed TOTP device
        When: confirm_2fa mutation is called with valid token
        Then: Device is marked as confirmed
        And: confirmed_at timestamp is set
        """
        user, token, device, plain_secret = user_with_unconfirmed_device

        # Generate valid TOTP token
        totp = pyotp.TOTP(plain_secret)
        valid_token = totp.now()

        mutation = """
        mutation Confirm2FA($input: Confirm2FAInput!) {
            confirm2fa(input: $input) {
                success
                device {
                    id
                    isConfirmed
                    confirmedAt
                }
                message
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "deviceId": str(device.id),
                        "token": valid_token,
                    }
                },
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["confirm2fa"]
        assert result["success"] is True
        assert result["device"]["isConfirmed"] is True
        assert result["device"]["confirmedAt"] is not None

        # Verify in database
        device.refresh_from_db()
        assert device.is_confirmed is True
        assert device.confirmed_at is not None

    def test_confirm_2fa_with_time_tolerance(self, client, user_with_unconfirmed_device) -> None:
        """Test 2FA confirmation accepts tokens within time window (M6).

        Given: User with unconfirmed TOTP device
        When: confirm_2fa mutation is called with token from previous period
        Then: Device is confirmed (±1 period tolerance = 90 second window)
        """
        user, token, device, plain_secret = user_with_unconfirmed_device

        # Generate TOTP token from previous time period
        totp = pyotp.TOTP(plain_secret)
        # Get token from 30 seconds ago (previous period)
        import time

        previous_token = totp.at(time.time() - 30)

        mutation = """
        mutation Confirm2FA($input: Confirm2FAInput!) {
            confirm2fa(input: $input) {
                success
                device {
                    isConfirmed
                }
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "deviceId": str(device.id),
                        "token": previous_token,
                    }
                },
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["confirm2fa"]["success"] is True

    def test_confirm_2fa_with_invalid_token(self, client, user_with_unconfirmed_device) -> None:
        """Test 2FA confirmation fails with invalid token.

        Given: User with unconfirmed TOTP device
        When: confirm_2fa mutation is called with invalid token
        Then: Error is returned with code INVALID_TOTP_CODE
        And: Device remains unconfirmed
        """
        user, token, device, plain_secret = user_with_unconfirmed_device

        mutation = """
        mutation Confirm2FA($input: Confirm2FAInput!) {
            confirm2fa(input: $input) {
                success
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "deviceId": str(device.id),
                        "token": "000000",  # Invalid token
                    }
                },
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_TOTP_CODE" in str(data["errors"][0])

        # Verify device not confirmed
        device.refresh_from_db()
        assert device.is_confirmed is False

    def test_confirm_2fa_device_not_found(self, client, db) -> None:
        """Test 2FA confirmation fails for non-existent device.

        Given: Authenticated user
        When: confirm_2fa mutation is called with invalid device ID
        Then: Error is returned with code RESOURCE_NOT_FOUND
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        tokens = TokenService.create_tokens(user)

        mutation = """
        mutation Confirm2FA($input: Confirm2FAInput!) {
            confirm2fa(input: $input) {
                success
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "deviceId": "00000000-0000-0000-0000-000000000000",
                        "token": "123456",
                    }
                },
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
        )

        data = response.json()
        assert "errors" in data
        assert "RESOURCE_NOT_FOUND" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestRemove2FADeviceMutation:
    """Test GraphQL remove_2fa_device mutation (H13)."""

    @pytest.fixture
    def user_with_confirmed_device(self, db):
        """Provide user with confirmed TOTP device.

        Returns:
            Tuple of (user, access_token, device)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("SecureP@ss1847!#")
        user.save()

        tokens = TokenService.create_tokens(user)

        # Create and confirm device
        device, plain_secret = TOTPService.create_device(user, "Test Device")
        totp = pyotp.TOTP(plain_secret)
        TOTPService.confirm_device(device, totp.now())

        return user, tokens["access_token"], device

    def test_remove_2fa_device_success(self, client, user_with_confirmed_device) -> None:
        """Test removing a TOTP device (H13).

        Given: User with confirmed TOTP device
        When: remove_2fa_device mutation is called
        Then: Device is removed from database
        And: Success message indicates device removed
        """
        user, token, device = user_with_confirmed_device
        device_id = str(device.id)

        mutation = """
        mutation Remove2FADevice($input: Remove2FADeviceInput!) {
            remove2faDevice(input: $input) {
                success
                message
                remainingDevices
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"deviceId": device_id}},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["remove2faDevice"]
        assert result["success"] is True
        assert "Test Device" in result["message"]
        assert result["remainingDevices"] == 0

        # Verify device removed from database
        assert not TOTPDevice.objects.filter(id=device_id).exists()

    def test_remove_2fa_device_not_owned_by_user(self, client, db) -> None:
        """Test cannot remove another user's device.

        Given: Device owned by different user
        When: remove_2fa_device mutation is called
        Then: Error is returned with code RESOURCE_NOT_FOUND
        """
        org = OrganisationFactory.create()

        # Create first user with device
        user1 = UserFactory.create(organisation=org, email_verified=True)
        device, _ = TOTPService.create_device(user1, "User1 Device")

        # Create second user
        user2 = UserFactory.create(organisation=org, email_verified=True)
        tokens = TokenService.create_tokens(user2)

        mutation = """
        mutation Remove2FADevice($input: Remove2FADeviceInput!) {
            remove2faDevice(input: $input) {
                success
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"deviceId": str(device.id)}},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
        )

        data = response.json()
        assert "errors" in data
        assert "RESOURCE_NOT_FOUND" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestRegenerate2FABackupCodesMutation:
    """Test GraphQL regenerate_2fa_backup_codes mutation."""

    @pytest.fixture
    def user_with_2fa_enabled(self, db):
        """Provide user with 2FA enabled and backup codes.

        Returns:
            Tuple of (user, access_token, original_backup_codes)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("SecureP@ss1847!#")
        user.save()

        tokens = TokenService.create_tokens(user)

        # Create and confirm device
        device, plain_secret = TOTPService.create_device(user, "Test Device")
        totp = pyotp.TOTP(plain_secret)
        TOTPService.confirm_device(device, totp.now())

        # Generate initial backup codes
        original_codes = TOTPService.generate_backup_codes(user)

        return user, tokens["access_token"], original_codes

    def test_regenerate_backup_codes_success(self, client, user_with_2fa_enabled) -> None:
        """Test regenerating backup codes invalidates old codes (H14).

        Given: User with 2FA enabled and existing backup codes
        When: regenerate_2fa_backup_codes mutation is called with correct password
        Then: New backup codes are generated
        And: Old backup codes are invalidated
        And: Codes use XXXX-XXXX-XXXX format (M3)
        """
        user, token, original_codes = user_with_2fa_enabled

        mutation = """
        mutation Regenerate2FABackupCodes($password: String!) {
            regenerate2faBackupCodes(password: $password) {
                backupCodes
                count
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"password": "SecureP@ss1847!#"},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["regenerate2faBackupCodes"]
        assert result["count"] == 10
        assert len(result["backupCodes"]) == 10

        # Verify new codes are different from original
        new_codes = set(result["backupCodes"])
        old_codes = set(original_codes)
        assert new_codes != old_codes

        # Verify format (M3)
        for code in result["backupCodes"]:
            assert len(code) == 14
            parts = code.split("-")
            assert len(parts) == 3
            assert all(len(p) == 4 for p in parts)

        # Verify old codes no longer work
        old_code_works = TOTPService.verify_backup_code(user, original_codes[0])
        assert old_code_works is False

    def test_regenerate_backup_codes_wrong_password(self, client, user_with_2fa_enabled) -> None:
        """Test regenerating backup codes fails with wrong password.

        Given: User with 2FA enabled
        When: regenerate_2fa_backup_codes mutation is called with wrong password
        Then: Error is returned with code INVALID_CREDENTIALS
        """
        user, token, _ = user_with_2fa_enabled

        mutation = """
        mutation Regenerate2FABackupCodes($password: String!) {
            regenerate2faBackupCodes(password: $password) {
                backupCodes
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"password": "WrongPassword"},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_CREDENTIALS" in str(data["errors"][0])

    def test_regenerate_backup_codes_without_2fa(self, client, db) -> None:
        """Test regenerating backup codes fails without 2FA enabled.

        Given: User without 2FA enabled
        When: regenerate_2fa_backup_codes mutation is called
        Then: Error is returned with code INVALID_INPUT
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("SecureP@ss1847!#")
        user.save()
        tokens = TokenService.create_tokens(user)

        mutation = """
        mutation Regenerate2FABackupCodes($password: String!) {
            regenerate2faBackupCodes(password: $password) {
                backupCodes
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"password": "SecureP@ss1847!#"},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_INPUT" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestDisable2FAMutation:
    """Test GraphQL disable_2fa mutation."""

    @pytest.fixture
    def user_with_2fa_enabled(self, db):
        """Provide user with 2FA enabled.

        Returns:
            Tuple of (user, access_token)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("SecureP@ss1847!#")
        user.save()

        tokens = TokenService.create_tokens(user)

        # Create and confirm device
        device, plain_secret = TOTPService.create_device(user, "Test Device")
        totp = pyotp.TOTP(plain_secret)
        TOTPService.confirm_device(device, totp.now())

        # Generate backup codes
        TOTPService.generate_backup_codes(user)

        return user, tokens["access_token"]

    def test_disable_2fa_success(self, client, user_with_2fa_enabled) -> None:
        """Test disabling 2FA removes all devices and backup codes.

        Given: User with 2FA enabled (devices and backup codes)
        When: disable_2fa mutation is called with correct password
        Then: All TOTP devices are removed
        And: All backup codes are removed
        And: Success message is returned
        """
        user, token = user_with_2fa_enabled

        # Verify 2FA is enabled
        assert TOTPDevice.objects.filter(user=user).exists()
        assert BackupCode.objects.filter(user=user).exists()

        mutation = """
        mutation Disable2FA($password: String!) {
            disable2fa(password: $password) {
                success
                message
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"password": "SecureP@ss1847!#"},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["disable2fa"]
        assert result["success"] is True
        assert "disabled" in result["message"].lower()

        # Verify all 2FA data removed
        assert not TOTPDevice.objects.filter(user=user).exists()
        assert not BackupCode.objects.filter(user=user).exists()

    def test_disable_2fa_wrong_password(self, client, user_with_2fa_enabled) -> None:
        """Test disabling 2FA fails with wrong password.

        Given: User with 2FA enabled
        When: disable_2fa mutation is called with wrong password
        Then: Error is returned with code INVALID_CREDENTIALS
        And: 2FA remains enabled
        """
        user, token = user_with_2fa_enabled

        mutation = """
        mutation Disable2FA($password: String!) {
            disable2fa(password: $password) {
                success
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"password": "WrongPassword"},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_CREDENTIALS" in str(data["errors"][0])

        # Verify 2FA still enabled
        assert TOTPDevice.objects.filter(user=user).exists()


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestTwoFactorStatusQuery:
    """Test GraphQL two_factor_status query."""

    def test_two_factor_status_with_2fa_enabled(self, client, db) -> None:
        """Test 2FA status query shows enabled state.

        Given: User with confirmed TOTP device and backup codes
        When: two_factor_status query is called
        Then: enabled is True
        And: devices list contains the device (H13)
        And: backup_codes_remaining shows correct count
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        tokens = TokenService.create_tokens(user)

        # Enable 2FA
        device, plain_secret = TOTPService.create_device(user, "My Phone")
        totp = pyotp.TOTP(plain_secret)
        TOTPService.confirm_device(device, totp.now())
        TOTPService.generate_backup_codes(user)

        query = """
        query {
            twoFactorStatus {
                enabled
                devices {
                    id
                    name
                    isConfirmed
                }
                backupCodesRemaining
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["twoFactorStatus"]
        assert result["enabled"] is True
        assert len(result["devices"]) == 1
        assert result["devices"][0]["name"] == "My Phone"
        assert result["devices"][0]["isConfirmed"] is True
        assert result["backupCodesRemaining"] == 10

    def test_two_factor_status_without_2fa(self, client, db) -> None:
        """Test 2FA status query shows disabled state.

        Given: User without 2FA enabled
        When: two_factor_status query is called
        Then: enabled is False
        And: devices list is empty
        And: backup_codes_remaining is 0
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        tokens = TokenService.create_tokens(user)

        query = """
        query {
            twoFactorStatus {
                enabled
                devices {
                    id
                }
                backupCodesRemaining
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["twoFactorStatus"]
        assert result["enabled"] is False
        assert len(result["devices"]) == 0
        assert result["backupCodesRemaining"] == 0

    def test_two_factor_status_requires_authentication(self, client) -> None:
        """Test 2FA status query requires authentication.

        Given: Unauthenticated request
        When: two_factor_status query is called
        Then: Error is returned with code NOT_AUTHENTICATED
        """
        query = """
        query {
            twoFactorStatus {
                enabled
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "NOT_AUTHENTICATED" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestTwoFactorDevicesQuery:
    """Test GraphQL two_factor_devices query (H13)."""

    def test_two_factor_devices_lists_all_devices(self, client, db) -> None:
        """Test listing multiple TOTP devices (H13).

        Given: User with multiple TOTP devices
        When: two_factor_devices query is called
        Then: All devices are returned with details
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        tokens = TokenService.create_tokens(user)

        # Create multiple devices
        device1, secret1 = TOTPService.create_device(user, "iPhone")
        device2, secret2 = TOTPService.create_device(user, "Android")
        device3, _ = TOTPService.create_device(user, "Backup Authenticator")

        # Confirm first two devices
        totp1 = pyotp.TOTP(secret1)
        TOTPService.confirm_device(device1, totp1.now())
        totp2 = pyotp.TOTP(secret2)
        TOTPService.confirm_device(device2, totp2.now())

        query = """
        query {
            twoFactorDevices {
                id
                name
                isConfirmed
                createdAt
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {tokens['access_token']}",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        devices = data["data"]["twoFactorDevices"]
        assert len(devices) == 3

        device_names = {d["name"] for d in devices}
        assert device_names == {"iPhone", "Android", "Backup Authenticator"}

        # Verify confirmed status
        for device in devices:
            if device["name"] in ["iPhone", "Android"]:
                assert device["isConfirmed"] is True
            else:
                assert device["isConfirmed"] is False
