"""Integration tests for 2FA login flow.

Tests cover the complete 2FA authentication workflow including:
- Login with 2FA enabled requiring TOTP code
- Login with valid TOTP code
- Login with backup code
- Login with invalid 2FA code
- Multiple device verification (H13)

These tests verify the integration between auth mutations,
TOTP service, and token service.
"""

from django.contrib.auth import get_user_model

import pyotp
import pytest

from apps.core.services.token_service import TokenService
from apps.core.services.totp_service import TOTPService
from tests.factories import OrganisationFactory, UserFactory

User = get_user_model()


@pytest.mark.integration
@pytest.mark.django_db
class TestLoginWith2FA:
    """Integration tests for login with 2FA enabled."""

    @pytest.fixture
    def user_with_2fa(self, db) -> tuple[User, str]:
        """Create a user with 2FA enabled.

        Returns:
            Tuple of (user, plain_totp_secret)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(
            email="2fa_user@example.com",
            organisation=org,
            email_verified=True,
        )
        user.set_password("SecureP@ss1847!#")
        user.save()

        # Enable 2FA
        device, plain_secret = TOTPService.create_device(user, "Test Device")
        totp = pyotp.TOTP(plain_secret)
        TOTPService.confirm_device(device, totp.now())

        # Generate backup codes
        TOTPService.generate_backup_codes(user)

        return user, plain_secret

    def test_login_requires_2fa_when_enabled(self, client, user_with_2fa) -> None:
        """Test login returns requires_two_factor when 2FA is enabled.

        Given: User with 2FA enabled
        When: login mutation is called without TOTP code
        Then: requiresTwoFactor is True
        And: Token is empty (not issued until 2FA verified)
        """
        user, _ = user_with_2fa

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                refreshToken
                user {
                    email
                }
                requiresTwoFactor
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "email": "2fa_user@example.com",
                        "password": "SecureP@ss1847!#",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["login"]
        assert result["requiresTwoFactor"] is True
        assert result["token"] == ""  # No token until 2FA verified
        assert result["user"]["email"] == "2fa_user@example.com"

    def test_login_with_valid_totp_code(self, client, user_with_2fa) -> None:
        """Test login succeeds with valid TOTP code.

        Given: User with 2FA enabled
        When: login mutation is called with valid TOTP code
        Then: Token is issued
        And: requiresTwoFactor is False
        """
        user, plain_secret = user_with_2fa
        totp = pyotp.TOTP(plain_secret)
        valid_code = totp.now()

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                refreshToken
                user {
                    email
                }
                requiresTwoFactor
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "email": "2fa_user@example.com",
                        "password": "SecureP@ss1847!#",
                        "totpCode": valid_code,
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None

        result = data["data"]["login"]
        assert result["requiresTwoFactor"] is False
        assert result["token"] != ""
        assert result["refreshToken"] != ""
        assert result["user"]["email"] == "2fa_user@example.com"

    def test_login_with_backup_code(self, client, user_with_2fa) -> None:
        """Test login succeeds with valid backup code.

        Given: User with 2FA enabled and backup codes
        When: login mutation is called with valid backup code
        Then: Token is issued
        And: Backup code is consumed (cannot be reused)
        """
        user, _ = user_with_2fa

        # Get a backup code
        backup_codes = TOTPService.generate_backup_codes(user)
        backup_code = backup_codes[0]

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                requiresTwoFactor
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "email": "2fa_user@example.com",
                        "password": "SecureP@ss1847!#",
                        "totpCode": backup_code,
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["login"]["token"] != ""

        # Verify backup code was consumed
        remaining = TOTPService.count_remaining_backup_codes(user)
        assert remaining == 9

    def test_login_with_invalid_totp_code(self, client, user_with_2fa) -> None:
        """Test login fails with invalid TOTP code.

        Given: User with 2FA enabled
        When: login mutation is called with invalid TOTP code
        Then: Error is returned with code INVALID_2FA_CODE
        """
        user, _ = user_with_2fa

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "email": "2fa_user@example.com",
                        "password": "SecureP@ss1847!#",
                        "totpCode": "000000",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_2FA_CODE" in str(data["errors"][0])

    def test_login_with_wrong_password_and_totp(self, client, user_with_2fa) -> None:
        """Test login fails with wrong password even with valid TOTP.

        Given: User with 2FA enabled
        When: login mutation is called with wrong password but valid TOTP
        Then: Error is returned with code INVALID_CREDENTIALS
        """
        user, plain_secret = user_with_2fa
        totp = pyotp.TOTP(plain_secret)
        valid_code = totp.now()

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "email": "2fa_user@example.com",
                        "password": "WrongPassword",
                        "totpCode": valid_code,
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_CREDENTIALS" in str(data["errors"][0])


@pytest.mark.integration
@pytest.mark.django_db
class TestMultipleDeviceVerification:
    """Integration tests for multiple TOTP devices (H13)."""

    @pytest.fixture
    def user_with_multiple_devices(self, db) -> tuple[User, list[str]]:
        """Create a user with multiple 2FA devices.

        Returns:
            Tuple of (user, list_of_plain_secrets)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(
            email="multi_device@example.com",
            organisation=org,
            email_verified=True,
        )
        user.set_password("SecureP@ss1847!#")
        user.save()

        secrets = []
        for name in ["iPhone", "Android", "Backup Auth"]:
            device, plain_secret = TOTPService.create_device(user, name)
            totp = pyotp.TOTP(plain_secret)
            TOTPService.confirm_device(device, totp.now())
            secrets.append(plain_secret)

        return user, secrets

    def test_login_works_with_any_confirmed_device(
        self, client, user_with_multiple_devices
    ) -> None:
        """Test login works with token from any confirmed device (H13).

        Given: User with multiple confirmed 2FA devices
        When: login mutation is called with token from second device
        Then: Token is issued
        """
        user, secrets = user_with_multiple_devices

        # Use token from second device
        totp = pyotp.TOTP(secrets[1])
        valid_code = totp.now()

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                requiresTwoFactor
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "email": "multi_device@example.com",
                        "password": "SecureP@ss1847!#",
                        "totpCode": valid_code,
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["login"]["token"] != ""


@pytest.mark.integration
@pytest.mark.django_db
class TestComplete2FASetupFlow:
    """Integration tests for complete 2FA setup workflow."""

    def test_complete_2fa_setup_and_login_flow(self, client, db) -> None:
        """Test complete 2FA setup and subsequent login.

        Workflow:
        1. User registers and verifies email
        2. User sets up 2FA
        3. User confirms 2FA with valid token
        4. User logs out
        5. User logs in with 2FA code
        """
        # Step 1: Create verified user
        org = OrganisationFactory.create()
        user = UserFactory.create(
            email="flow_test@example.com",
            organisation=org,
            email_verified=True,
        )
        user.set_password("SecureP@ss1847!#")
        user.save()

        tokens = TokenService.create_tokens(user)
        access_token = tokens["access_token"]

        # Step 2: Set up 2FA
        setup_mutation = """
        mutation Setup2FA($input: Setup2FAInput!) {
            setup2fa(input: $input) {
                device {
                    id
                }
                secret
                backupCodes
            }
        }
        """

        setup_response = client.post(
            "/graphql/",
            {
                "query": setup_mutation,
                "variables": {"input": {"deviceName": "Test Phone"}},
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        setup_data = setup_response.json()
        assert "errors" not in setup_data or setup_data["errors"] is None

        device_id = setup_data["data"]["setup2fa"]["device"]["id"]
        plain_secret = setup_data["data"]["setup2fa"]["secret"]
        backup_codes = setup_data["data"]["setup2fa"]["backupCodes"]

        assert len(backup_codes) == 10

        # Step 3: Confirm 2FA
        totp = pyotp.TOTP(plain_secret)
        valid_token = totp.now()

        confirm_mutation = """
        mutation Confirm2FA($input: Confirm2FAInput!) {
            confirm2fa(input: $input) {
                success
                device {
                    isConfirmed
                }
            }
        }
        """

        confirm_response = client.post(
            "/graphql/",
            {
                "query": confirm_mutation,
                "variables": {
                    "input": {
                        "deviceId": device_id,
                        "token": valid_token,
                    }
                },
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        confirm_data = confirm_response.json()
        assert "errors" not in confirm_data or confirm_data["errors"] is None
        assert confirm_data["data"]["confirm2fa"]["success"] is True
        assert confirm_data["data"]["confirm2fa"]["device"]["isConfirmed"] is True

        # Step 4: Logout
        logout_mutation = """
        mutation {
            logout
        }
        """

        client.post(
            "/graphql/",
            {"query": logout_mutation},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )

        # Step 5: Login with 2FA
        # Need to get a fresh token since time may have passed
        fresh_token = totp.now()

        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                requiresTwoFactor
            }
        }
        """

        login_response = client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": "flow_test@example.com",
                        "password": "SecureP@ss1847!#",
                        "totpCode": fresh_token,
                    }
                },
            },
            content_type="application/json",
        )

        login_data = login_response.json()
        assert "errors" not in login_data or login_data["errors"] is None
        assert login_data["data"]["login"]["token"] != ""
        assert login_data["data"]["login"]["requiresTwoFactor"] is False
