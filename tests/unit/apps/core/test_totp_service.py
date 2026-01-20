"""Unit tests for TOTP service.

Tests cover:
- TOTP device creation with encryption (C2)
- TOTP token verification with time tolerance (M6)
- Device confirmation
- Multiple device management (H13)
- Backup code generation with hashing (H14) and format (M3)
- Backup code verification
- 2FA disable

These tests follow TDD principles with Given/When/Then documentation.
"""

import time

from django.contrib.auth import get_user_model

import pyotp
import pytest

from apps.core.models import BackupCode, TOTPDevice
from apps.core.services.totp_service import TOTPService
from tests.factories import OrganisationFactory, UserFactory

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestTOTPDeviceCreation:
    """Test TOTP device creation functionality."""

    @pytest.fixture
    def user(self, db) -> User:
        """Create a test user."""
        org = OrganisationFactory.create()
        return UserFactory.create(organisation=org, email_verified=True)

    def test_create_device_generates_encrypted_secret(self, user) -> None:
        """Test device creation encrypts TOTP secret (C2).

        Given: A user without TOTP devices
        When: create_device is called
        Then: Device is created with Fernet-encrypted secret
        And: Plain secret is returned for QR code display
        And: Stored secret differs from plain secret
        """
        device, plain_secret = TOTPService.create_device(user, "Test Device")

        # Verify plain secret is valid base32
        assert len(plain_secret) == 32
        assert plain_secret.isalnum()

        # Verify device was created
        assert device.id is not None
        assert device.name == "Test Device"
        assert device.is_confirmed is False

        # Verify secret is encrypted (stored bytes differ from plain)
        assert device.secret != plain_secret.encode()

        # Verify we can decrypt and get original
        decrypted = device.get_secret()
        assert decrypted == plain_secret

    def test_create_device_supports_custom_name(self, user) -> None:
        """Test device creation with custom name (H13).

        Given: A user without TOTP devices
        When: create_device is called with custom name
        Then: Device is created with the specified name
        """
        device, _ = TOTPService.create_device(user, "iPhone 14 Pro")

        assert device.name == "iPhone 14 Pro"

    def test_create_device_uses_default_name(self, user) -> None:
        """Test device creation with default name.

        Given: A user without TOTP devices
        When: create_device is called without name
        Then: Device is created with default name "Default"
        """
        device, _ = TOTPService.create_device(user)

        assert device.name == "Default"

    def test_create_multiple_devices_for_same_user(self, user) -> None:
        """Test creating multiple devices for same user (H13).

        Given: A user with one TOTP device
        When: create_device is called again
        Then: Second device is created
        And: Both devices have unique IDs
        And: Both devices can generate valid tokens
        """
        device1, secret1 = TOTPService.create_device(user, "Device 1")
        device2, secret2 = TOTPService.create_device(user, "Device 2")

        assert device1.id != device2.id
        assert secret1 != secret2
        assert TOTPDevice.objects.filter(user=user).count() == 2


@pytest.mark.unit
@pytest.mark.django_db
class TestTOTPTokenVerification:
    """Test TOTP token verification functionality."""

    @pytest.fixture
    def confirmed_device(self, db) -> tuple[TOTPDevice, str]:
        """Create a confirmed TOTP device.

        Returns:
            Tuple of (device, plain_secret)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)
        device, plain_secret = TOTPService.create_device(user, "Test Device")

        # Confirm the device
        totp = pyotp.TOTP(plain_secret)
        device.is_confirmed = True
        device.save()

        return device, plain_secret

    def test_verify_token_with_valid_token(self, confirmed_device) -> None:
        """Test token verification with valid token.

        Given: A confirmed TOTP device
        When: verify_token is called with correct token
        Then: Returns True
        And: last_used_at is updated
        """
        device, plain_secret = confirmed_device
        totp = pyotp.TOTP(plain_secret)
        valid_token = totp.now()

        result = TOTPService.verify_token(device, valid_token)

        assert result is True
        device.refresh_from_db()
        assert device.last_used_at is not None

    def test_verify_token_with_invalid_token(self, confirmed_device) -> None:
        """Test token verification with invalid token.

        Given: A confirmed TOTP device
        When: verify_token is called with wrong token
        Then: Returns False
        """
        device, _ = confirmed_device

        result = TOTPService.verify_token(device, "000000")

        assert result is False

    def test_verify_token_with_time_tolerance(self, confirmed_device) -> None:
        """Test token verification within time window (M6).

        Given: A confirmed TOTP device
        When: verify_token is called with token from previous period
        Then: Returns True (±1 period = 90 second window)
        """
        device, plain_secret = confirmed_device
        totp = pyotp.TOTP(plain_secret)

        # Get token from 30 seconds ago (previous period)
        previous_token = totp.at(time.time() - 30)

        result = TOTPService.verify_token(device, previous_token)

        assert result is True

    def test_verify_token_outside_time_window(self, confirmed_device) -> None:
        """Test token verification outside time window.

        Given: A confirmed TOTP device
        When: verify_token is called with token from > 2 periods ago
        Then: Returns False
        """
        device, plain_secret = confirmed_device
        totp = pyotp.TOTP(plain_secret)

        # Get token from 90+ seconds ago (outside ±1 period window)
        old_token = totp.at(time.time() - 120)

        result = TOTPService.verify_token(device, old_token)

        assert result is False

    def test_verify_token_unconfirmed_device_fails(self, db) -> None:
        """Test token verification fails for unconfirmed device.

        Given: An unconfirmed TOTP device
        When: verify_token is called with valid token
        Then: Returns False
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)
        device, plain_secret = TOTPService.create_device(user, "Unconfirmed")

        totp = pyotp.TOTP(plain_secret)
        valid_token = totp.now()

        result = TOTPService.verify_token(device, valid_token)

        assert result is False


@pytest.mark.unit
@pytest.mark.django_db
class TestTOTPDeviceConfirmation:
    """Test TOTP device confirmation functionality."""

    @pytest.fixture
    def unconfirmed_device(self, db) -> tuple[TOTPDevice, str]:
        """Create an unconfirmed TOTP device.

        Returns:
            Tuple of (device, plain_secret)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)
        return TOTPService.create_device(user, "Test Device")

    def test_confirm_device_with_valid_token(self, unconfirmed_device) -> None:
        """Test device confirmation with valid token.

        Given: An unconfirmed TOTP device
        When: confirm_device is called with valid token
        Then: Device is marked as confirmed
        And: confirmed_at timestamp is set
        """
        device, plain_secret = unconfirmed_device
        totp = pyotp.TOTP(plain_secret)
        valid_token = totp.now()

        result = TOTPService.confirm_device(device, valid_token)

        assert result is True
        device.refresh_from_db()
        assert device.is_confirmed is True
        assert device.confirmed_at is not None

    def test_confirm_device_with_invalid_token(self, unconfirmed_device) -> None:
        """Test device confirmation fails with invalid token.

        Given: An unconfirmed TOTP device
        When: confirm_device is called with invalid token
        Then: Returns False
        And: Device remains unconfirmed
        """
        device, _ = unconfirmed_device

        result = TOTPService.confirm_device(device, "000000")

        assert result is False
        device.refresh_from_db()
        assert device.is_confirmed is False

    def test_confirm_already_confirmed_device(self, unconfirmed_device) -> None:
        """Test confirming already confirmed device returns True.

        Given: A confirmed TOTP device
        When: confirm_device is called again
        Then: Returns True (idempotent)
        """
        device, plain_secret = unconfirmed_device
        totp = pyotp.TOTP(plain_secret)

        # First confirmation
        TOTPService.confirm_device(device, totp.now())

        # Second confirmation attempt
        result = TOTPService.confirm_device(device, "000000")

        assert result is True  # Already confirmed


@pytest.mark.unit
@pytest.mark.django_db
class TestBackupCodeGeneration:
    """Test backup code generation functionality."""

    @pytest.fixture
    def user(self, db) -> User:
        """Create a test user."""
        org = OrganisationFactory.create()
        return UserFactory.create(organisation=org)

    def test_generate_backup_codes_creates_10_codes(self, user) -> None:
        """Test backup code generation creates 10 codes.

        Given: A user without backup codes
        When: generate_backup_codes is called
        Then: 10 backup codes are created
        And: Codes are returned in plain text
        """
        codes = TOTPService.generate_backup_codes(user)

        assert len(codes) == 10
        assert BackupCode.objects.filter(user=user).count() == 10

    def test_backup_codes_use_correct_format(self, user) -> None:
        """Test backup codes use XXXX-XXXX-XXXX format (M3).

        Given: A user
        When: generate_backup_codes is called
        Then: Each code follows XXXX-XXXX-XXXX format
        And: Each segment is 4 alphanumeric characters
        """
        codes = TOTPService.generate_backup_codes(user)

        for code in codes:
            assert len(code) == 14
            parts = code.split("-")
            assert len(parts) == 3
            assert all(len(p) == 4 for p in parts)
            assert all(p.isalnum() for p in parts)

    def test_backup_codes_are_hashed_in_database(self, user) -> None:
        """Test backup codes are stored as hashes (H14).

        Given: A user
        When: generate_backup_codes is called
        Then: Only hashed codes are stored in database
        And: Hash is SHA-256 (64 hex characters)
        """
        codes = TOTPService.generate_backup_codes(user)

        stored_codes = BackupCode.objects.filter(user=user)
        for stored in stored_codes:
            # Verify hash format (SHA-256 = 64 hex chars)
            assert len(stored.code_hash) == 64
            assert all(c in "0123456789abcdef" for c in stored.code_hash)

            # Verify stored hash is not same as any plain code
            assert stored.code_hash not in codes

    def test_regenerate_backup_codes_invalidates_old_codes(self, user) -> None:
        """Test regenerating backup codes invalidates old ones.

        Given: A user with existing backup codes
        When: generate_backup_codes is called again
        Then: Old codes are deleted
        And: New codes are created
        And: Count remains 10
        """
        old_codes = TOTPService.generate_backup_codes(user)
        old_hashes = set(BackupCode.objects.filter(user=user).values_list("code_hash", flat=True))

        new_codes = TOTPService.generate_backup_codes(user)
        new_hashes = set(BackupCode.objects.filter(user=user).values_list("code_hash", flat=True))

        assert old_codes != new_codes
        assert old_hashes != new_hashes
        assert BackupCode.objects.filter(user=user).count() == 10


@pytest.mark.unit
@pytest.mark.django_db
class TestBackupCodeVerification:
    """Test backup code verification functionality."""

    @pytest.fixture
    def user_with_backup_codes(self, db) -> tuple[User, list[str]]:
        """Create a user with backup codes.

        Returns:
            Tuple of (user, plain_backup_codes)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)
        codes = TOTPService.generate_backup_codes(user)
        return user, codes

    def test_verify_backup_code_with_valid_code(self, user_with_backup_codes) -> None:
        """Test backup code verification with valid code (H14).

        Given: A user with backup codes
        When: verify_backup_code is called with valid code
        Then: Returns True
        And: Code is marked as used
        """
        user, codes = user_with_backup_codes
        code_to_use = codes[0]

        result = TOTPService.verify_backup_code(user, code_to_use)

        assert result is True

        # Verify code is marked as used
        remaining = TOTPService.count_remaining_backup_codes(user)
        assert remaining == 9

    def test_verify_backup_code_without_hyphens(self, user_with_backup_codes) -> None:
        """Test backup code verification works without hyphens.

        Given: A user with backup codes
        When: verify_backup_code is called without hyphens
        Then: Returns True (normalisation handles both formats)
        """
        user, codes = user_with_backup_codes
        code_without_hyphens = codes[0].replace("-", "")

        result = TOTPService.verify_backup_code(user, code_without_hyphens)

        assert result is True

    def test_verify_backup_code_case_insensitive(self, user_with_backup_codes) -> None:
        """Test backup code verification is case insensitive.

        Given: A user with backup codes
        When: verify_backup_code is called with lowercase code
        Then: Returns True
        """
        user, codes = user_with_backup_codes
        lowercase_code = codes[0].lower()

        result = TOTPService.verify_backup_code(user, lowercase_code)

        assert result is True

    def test_verify_backup_code_cannot_be_reused(self, user_with_backup_codes) -> None:
        """Test backup code cannot be used twice.

        Given: A user with backup codes
        When: verify_backup_code is called twice with same code
        Then: First verification returns True
        And: Second verification returns False
        """
        user, codes = user_with_backup_codes
        code = codes[0]

        first_result = TOTPService.verify_backup_code(user, code)
        second_result = TOTPService.verify_backup_code(user, code)

        assert first_result is True
        assert second_result is False

    def test_verify_backup_code_with_invalid_code(self, user_with_backup_codes) -> None:
        """Test backup code verification with invalid code.

        Given: A user with backup codes
        When: verify_backup_code is called with invalid code
        Then: Returns False
        """
        user, _ = user_with_backup_codes

        result = TOTPService.verify_backup_code(user, "XXXX-XXXX-XXXX")

        assert result is False


@pytest.mark.unit
@pytest.mark.django_db
class TestTOTPDeviceManagement:
    """Test TOTP device management functionality (H13)."""

    @pytest.fixture
    def user_with_devices(self, db) -> tuple[User, list[TOTPDevice]]:
        """Create a user with multiple TOTP devices.

        Returns:
            Tuple of (user, devices_list)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)

        devices = []
        for name in ["iPhone", "Android", "Backup"]:
            device, secret = TOTPService.create_device(user, name)
            devices.append(device)

        return user, devices

    def test_list_user_devices(self, user_with_devices) -> None:
        """Test listing all devices for a user (H13).

        Given: A user with multiple TOTP devices
        When: list_user_devices is called
        Then: All devices are returned
        """
        user, expected_devices = user_with_devices

        devices = TOTPService.list_user_devices(user)

        assert len(devices) == 3
        device_names = {d.name for d in devices}
        assert device_names == {"iPhone", "Android", "Backup"}

    def test_remove_device(self, user_with_devices) -> None:
        """Test removing a device (H13).

        Given: A user with multiple TOTP devices
        When: remove_device is called
        Then: Device is deleted
        And: Other devices remain
        """
        user, devices = user_with_devices
        device_to_remove = devices[0]

        TOTPService.remove_device(device_to_remove)

        remaining = TOTPService.list_user_devices(user)
        assert len(remaining) == 2
        assert device_to_remove not in remaining

    def test_has_confirmed_device_true(self, user_with_devices) -> None:
        """Test has_confirmed_device returns True when device is confirmed.

        Given: A user with one confirmed TOTP device
        When: has_confirmed_device is called
        Then: Returns True
        """
        user, devices = user_with_devices
        device = devices[0]

        # Confirm the device
        plain_secret = device.get_secret()
        totp = pyotp.TOTP(plain_secret)
        TOTPService.confirm_device(device, totp.now())

        result = TOTPService.has_confirmed_device(user)

        assert result is True

    def test_has_confirmed_device_false(self, user_with_devices) -> None:
        """Test has_confirmed_device returns False with no confirmed devices.

        Given: A user with only unconfirmed TOTP devices
        When: has_confirmed_device is called
        Then: Returns False
        """
        user, _ = user_with_devices

        result = TOTPService.has_confirmed_device(user)

        assert result is False


@pytest.mark.unit
@pytest.mark.django_db
class TestDisable2FA:
    """Test 2FA disable functionality."""

    @pytest.fixture
    def user_with_2fa(self, db) -> User:
        """Create a user with 2FA enabled.

        Returns:
            User with confirmed device and backup codes
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)

        # Create and confirm device
        device, secret = TOTPService.create_device(user, "Test")
        totp = pyotp.TOTP(secret)
        TOTPService.confirm_device(device, totp.now())

        # Generate backup codes
        TOTPService.generate_backup_codes(user)

        return user

    def test_disable_2fa_removes_all_devices_and_codes(self, user_with_2fa) -> None:
        """Test disabling 2FA removes all devices and backup codes.

        Given: A user with 2FA enabled (devices and backup codes)
        When: disable_2fa is called
        Then: All TOTP devices are deleted
        And: All backup codes are deleted
        """
        user = user_with_2fa

        # Verify 2FA is enabled
        assert TOTPDevice.objects.filter(user=user).exists()
        assert BackupCode.objects.filter(user=user).exists()

        TOTPService.disable_2fa(user)

        # Verify all removed
        assert not TOTPDevice.objects.filter(user=user).exists()
        assert not BackupCode.objects.filter(user=user).exists()
        assert TOTPService.has_confirmed_device(user) is False


@pytest.mark.unit
@pytest.mark.django_db
class TestQRCodeGeneration:
    """Test QR code generation functionality."""

    @pytest.fixture
    def device(self, db) -> TOTPDevice:
        """Create a TOTP device for testing."""
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email="test@example.com")
        device, _ = TOTPService.create_device(user, "Test Device")
        return device

    def test_generate_qr_code_svg(self, device) -> None:
        """Test QR code SVG generation.

        Given: A TOTP device
        When: generate_qr_code_svg is called
        Then: Valid SVG string is returned
        """
        svg = TOTPService.generate_qr_code_svg(device)

        assert "<svg" in svg or "<?xml" in svg
        assert "</svg>" in svg

    def test_generate_qr_code_data_uri(self, device) -> None:
        """Test QR code data URI generation.

        Given: A TOTP device
        When: generate_qr_code_data_uri is called
        Then: Valid base64 data URI is returned
        """
        data_uri = TOTPService.generate_qr_code_data_uri(device)

        assert data_uri.startswith("data:image/svg+xml;base64,")
        # Verify it's valid base64
        import base64

        b64_part = data_uri.split(",")[1]
        decoded = base64.b64decode(b64_part)
        assert b"<svg" in decoded or b"<?xml" in decoded

    def test_qr_code_contains_user_email(self, device) -> None:
        """Test QR code URI contains user email.

        Given: A TOTP device for user with email
        When: QR code URI is generated
        Then: URI contains user's email
        """
        uri = device.generate_qr_code_uri()

        assert "test%40example.com" in uri or "test@example.com" in uri

    def test_qr_code_contains_issuer(self, device) -> None:
        """Test QR code URI contains issuer name.

        Given: A TOTP device
        When: QR code URI is generated with custom issuer
        Then: URI contains the issuer name
        """
        uri = device.generate_qr_code_uri(issuer_name="My App")

        assert "My%20App" in uri or "My App" in uri
