"""End-to-end tests for complete authentication workflows.

Tests cover the complete user journey:
1. Registration → Email Verification → Login → 2FA Setup → Logout
2. Full workflow with all security features enabled
3. Multi-device scenarios
4. Error recovery scenarios

These tests verify the entire system working together from start to finish.
"""


from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client
from django.utils import timezone

import pyotp
import pytest

from apps.core.models import (
    AuditLog,
    EmailVerificationToken,
    Organisation,
    SessionToken,
    TOTPDevice,
)

User = get_user_model()


@pytest.mark.e2e
@pytest.mark.django_db
class TestCompleteRegistrationToTwoFactorWorkflow:
    """Test complete user journey from registration to 2FA setup."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment.

        Args:
            db: pytest-django database fixture.
        """
        self.client = Client()
        self.organisation = Organisation.objects.create(name="Test Organisation", slug="test-org")
        self.user_email = "newuser@example.com"
        self.user_password = "SecureP@ssw0rd!2024"
        self.session_token = None
        self.totp_device = None

    def test_complete_workflow_registration_to_2fa_setup(self) -> None:
        """Test complete workflow: registration → email verification → login → 2FA → logout.

        This E2E test covers:
        1. User registration with valid data
        2. Email verification token sent
        3. User verifies email via token
        4. User logs in successfully
        5. User enables 2FA
        6. User scans QR code and enters TOTP
        7. User logs out
        8. User logs in again with 2FA challenge
        9. User enters TOTP code to complete login
        10. User logs out from all devices

        Given: A new user wants to register and set up 2FA
        When: User completes all steps in sequence
        Then: User has a fully secured account with 2FA enabled
        """
        # ==================== STEP 1: REGISTRATION ====================
        registration_mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                user {
                    id
                    email
                    emailVerified
                    firstName
                    lastName
                }
            }
        }
        """

        registration_response = self.client.post(
            "/graphql/",
            {
                "query": registration_mutation,
                "variables": {
                    "input": {
                        "email": self.user_email,
                        "password": self.user_password,
                        "firstName": "Test",
                        "lastName": "User",
                        "organisationSlug": self.organisation.slug,
                    }
                },
            },
            content_type="application/json",
        )

        reg_data = registration_response.json()
        assert "errors" not in reg_data, f"Registration failed: {reg_data.get('errors')}"

        user_data = reg_data["data"]["register"]["user"]
        user_id = user_data["id"]

        assert user_data["email"] == self.user_email
        assert user_data["emailVerified"] is False
        assert user_data["firstName"] == "Test"
        assert user_data["lastName"] == "User"

        # Verify user was created in database
        user = User.objects.get(id=user_id)
        assert user.email == self.user_email
        assert user.email_verified is False
        assert user.check_password(self.user_password)

        # Verify audit log entry for registration
        audit_log = AuditLog.objects.filter(user=user, action="user_registered").first()
        assert audit_log is not None

        # ==================== STEP 2: EMAIL VERIFICATION TOKEN ====================
        # Verify email verification token was created
        verification_token = EmailVerificationToken.objects.filter(
            user=user, used=False, expires_at__gt=timezone.now()
        ).first()

        assert verification_token is not None, "Email verification token not created"

        # Verify email was sent
        assert len(mail.outbox) == 1
        verification_email = mail.outbox[0]
        assert verification_email.to == [self.user_email]
        assert "verify" in verification_email.subject.lower()

        # ==================== STEP 3: EMAIL VERIFICATION ====================
        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
                message
            }
        }
        """

        verify_response = self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": verification_token.token,
                },
            },
            content_type="application/json",
        )

        verify_data = verify_response.json()
        assert "errors" not in verify_data, (
            f"Email verification failed: {verify_data.get('errors')}"
        )
        assert verify_data["data"]["verifyEmail"]["success"] is True

        # Verify user is now verified
        user.refresh_from_db()
        assert user.email_verified is True

        # Verify token is marked as used
        verification_token.refresh_from_db()
        assert verification_token.used is True

        # ==================== STEP 4: LOGIN ====================
        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                user {
                    id
                    email
                    hasTwoFactor
                }
                requiresTwoFactor
            }
        }
        """

        login_response = self.client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": self.user_email,
                        "password": self.user_password,
                    }
                },
            },
            content_type="application/json",
        )

        login_data = login_response.json()
        assert "errors" not in login_data, f"Login failed: {login_data.get('errors')}"

        self.session_token = login_data["data"]["login"]["token"]
        assert self.session_token is not None
        assert login_data["data"]["login"]["user"]["hasTwoFactor"] is False
        assert login_data["data"]["login"]["requiresTwoFactor"] is False

        # Verify session token was created in database
        session = SessionToken.objects.filter(
            user=user, is_revoked=False, expires_at__gt=timezone.now()
        ).first()
        assert session is not None

        # Verify audit log entry for login
        audit_log = (
            AuditLog.objects.filter(user=user, action="user_login").order_by("-created_at").first()
        )
        assert audit_log is not None

        # ==================== STEP 5: ENABLE 2FA ====================
        enable_2fa_mutation = """
        mutation Enable2FA {
            enable2FA {
                secret
                qrCodeUrl
                backupCodes
            }
        }
        """

        enable_2fa_response = self.client.post(
            "/graphql/",
            {
                "query": enable_2fa_mutation,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.session_token}",
        )

        enable_2fa_data = enable_2fa_response.json()
        assert "errors" not in enable_2fa_data, (
            f"Enable 2FA failed: {enable_2fa_data.get('errors')}"
        )

        totp_secret = enable_2fa_data["data"]["enable2FA"]["secret"]
        qr_code_url = enable_2fa_data["data"]["enable2FA"]["qrCodeUrl"]
        backup_codes = enable_2fa_data["data"]["enable2FA"]["backupCodes"]

        assert totp_secret is not None
        assert qr_code_url is not None
        assert len(backup_codes) == 10  # Should have 10 backup codes

        # Verify TOTP device was created
        totp_device = TOTPDevice.objects.filter(user=user).first()
        assert totp_device is not None
        assert totp_device.confirmed is False  # Not confirmed until TOTP verified

        # ==================== STEP 6: VERIFY 2FA WITH TOTP CODE ====================
        # Generate valid TOTP code from the secret
        totp = pyotp.TOTP(totp_secret)
        valid_code = totp.now()

        verify_2fa_mutation = """
        mutation Verify2FA($code: String!) {
            verify2FA(code: $code) {
                success
                message
            }
        }
        """

        verify_2fa_response = self.client.post(
            "/graphql/",
            {
                "query": verify_2fa_mutation,
                "variables": {
                    "code": valid_code,
                },
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.session_token}",
        )

        verify_2fa_data = verify_2fa_response.json()
        assert "errors" not in verify_2fa_data, (
            f"Verify 2FA failed: {verify_2fa_data.get('errors')}"
        )
        assert verify_2fa_data["data"]["verify2FA"]["success"] is True

        # Verify TOTP device is now confirmed
        totp_device.refresh_from_db()
        assert totp_device.confirmed is True

        # Verify user has 2FA enabled
        user.refresh_from_db()
        assert hasattr(user, "totp_device")
        assert user.totp_device.confirmed is True

        # ==================== STEP 7: LOGOUT ====================
        logout_mutation = """
        mutation Logout {
            logout {
                success
            }
        }
        """

        logout_response = self.client.post(
            "/graphql/",
            {
                "query": logout_mutation,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {self.session_token}",
        )

        logout_data = logout_response.json()
        assert "errors" not in logout_data
        assert logout_data["data"]["logout"]["success"] is True

        # Verify session was revoked
        session.refresh_from_db()
        assert session.is_revoked is True

        # ==================== STEP 8: LOGIN WITH 2FA CHALLENGE ====================
        login_2fa_response = self.client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": self.user_email,
                        "password": self.user_password,
                    }
                },
            },
            content_type="application/json",
        )

        login_2fa_data = login_2fa_response.json()
        assert "errors" not in login_2fa_data

        # Should require 2FA, not return token immediately
        assert login_2fa_data["data"]["login"]["requiresTwoFactor"] is True
        assert login_2fa_data["data"]["login"]["token"] is None  # No token yet

        # ==================== STEP 9: COMPLETE LOGIN WITH TOTP ====================
        # Generate new TOTP code
        new_totp_code = totp.now()

        verify_login_2fa_mutation = """
        mutation VerifyLogin2FA($code: String!) {
            verifyLogin2FA(code: $code) {
                token
                user {
                    id
                    email
                }
            }
        }
        """

        verify_login_2fa_response = self.client.post(
            "/graphql/",
            {
                "query": verify_login_2fa_mutation,
                "variables": {
                    "code": new_totp_code,
                },
            },
            content_type="application/json",
        )

        verify_login_2fa_data = verify_login_2fa_response.json()
        assert "errors" not in verify_login_2fa_data

        new_session_token = verify_login_2fa_data["data"]["verifyLogin2FA"]["token"]
        assert new_session_token is not None

        # Verify new session token works
        me_query = """
        query Me {
            me {
                id
                email
                hasTwoFactor
            }
        }
        """

        me_response = self.client.post(
            "/graphql/",
            {
                "query": me_query,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {new_session_token}",
        )

        me_data = me_response.json()
        assert "errors" not in me_data
        assert me_data["data"]["me"]["email"] == self.user_email
        assert me_data["data"]["me"]["hasTwoFactor"] is True

        # ==================== STEP 10: LOGOUT FROM ALL DEVICES ====================
        logout_all_mutation = """
        mutation LogoutAllDevices {
            logoutAllDevices {
                success
                devicesLoggedOut
            }
        }
        """

        logout_all_response = self.client.post(
            "/graphql/",
            {
                "query": logout_all_mutation,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {new_session_token}",
        )

        logout_all_data = logout_all_response.json()
        assert "errors" not in logout_all_data
        assert logout_all_data["data"]["logoutAllDevices"]["success"] is True

        # Verify all sessions are revoked
        active_sessions = SessionToken.objects.filter(user=user, is_revoked=False).count()
        assert active_sessions == 0

        # Verify old token no longer works
        old_token_response = self.client.post(
            "/graphql/",
            {
                "query": me_query,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {new_session_token}",
        )

        old_token_data = old_token_response.json()
        assert "errors" in old_token_data
        assert any(
            "revoked" in str(error).lower() or "expired" in str(error).lower()
            for error in old_token_data["errors"]
        )

    def test_2fa_backup_code_recovery(self) -> None:
        """Test 2FA backup code recovery workflow.

        Scenario: User loses access to their authenticator app

        Given: User has 2FA enabled with backup codes
        When: User logs in and uses a backup code instead of TOTP
        Then: Login succeeds and backup code is marked as used
        """
        # Setup: Create user with 2FA enabled
        user = User.objects.create_user(
            email="backup@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=True,
        )

        totp_device = TOTPDevice.objects.create(
            user=user,
            secret=pyotp.random_base32(),
            confirmed=True,
        )

        # Generate backup codes
        backup_codes = [f"BACKUP-{i:04d}" for i in range(10)]
        # In real implementation, these would be hashed
        totp_device.backup_codes = backup_codes
        totp_device.save()

        # Attempt login with backup code
        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                requiresTwoFactor
            }
        }
        """

        login_response = self.client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": "backup@example.com",
                        "password": "SecureP@ss123!",
                    }
                },
            },
            content_type="application/json",
        )

        login_data = login_response.json()
        assert login_data["data"]["login"]["requiresTwoFactor"] is True

        # Use backup code
        verify_backup_mutation = """
        mutation VerifyLogin2FA($code: String!) {
            verifyLogin2FA(code: $code) {
                token
            }
        }
        """

        verify_response = self.client.post(
            "/graphql/",
            {
                "query": verify_backup_mutation,
                "variables": {
                    "code": backup_codes[0],  # Use first backup code
                },
            },
            content_type="application/json",
        )

        verify_data = verify_response.json()
        assert "errors" not in verify_data
        assert verify_data["data"]["verifyLogin2FA"]["token"] is not None

        # Verify backup code cannot be reused
        verify_reuse_response = self.client.post(
            "/graphql/",
            {
                "query": verify_backup_mutation,
                "variables": {
                    "code": backup_codes[0],  # Try to reuse same code
                },
            },
            content_type="application/json",
        )

        verify_reuse_data = verify_reuse_response.json()
        assert "errors" in verify_reuse_data


@pytest.mark.e2e
@pytest.mark.django_db
class TestMultiDeviceAuthenticationScenarios:
    """Test authentication across multiple devices simultaneously."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment.

        Args:
            db: pytest-django database fixture.
        """
        self.organisation = Organisation.objects.create(name="Test Organisation", slug="test-org")

        self.user = User.objects.create_user(
            email="multidevice@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=True,
        )

    def test_concurrent_logins_from_multiple_devices(self) -> None:
        """Test user can login from multiple devices simultaneously.

        Given: A verified user
        When: User logs in from 3 different devices
        Then: All 3 sessions should be active simultaneously
        """
        devices = []

        for i in range(3):
            client = Client()

            login_mutation = """
            mutation Login($input: LoginInput!) {
                login(input: $input) {
                    token
                }
            }
            """

            response = client.post(
                "/graphql/",
                {
                    "query": login_mutation,
                    "variables": {
                        "input": {
                            "email": "multidevice@example.com",
                            "password": "SecureP@ss123!",
                        }
                    },
                },
                content_type="application/json",
                HTTP_USER_AGENT=f"Device-{i}",
            )

            data = response.json()
            assert "errors" not in data

            devices.append(
                {
                    "client": client,
                    "token": data["data"]["login"]["token"],
                    "user_agent": f"Device-{i}",
                }
            )

        # Verify all 3 sessions are active
        active_sessions = SessionToken.objects.filter(
            user=self.user, is_revoked=False, expires_at__gt=timezone.now()
        ).count()

        assert active_sessions == 3

        # Verify each device can access protected resources
        for device in devices:
            me_query = """
            query Me {
                me {
                    email
                }
            }
            """

            response = device["client"].post(
                "/graphql/",
                {
                    "query": me_query,
                },
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {device['token']}",
            )

            data = response.json()
            assert "errors" not in data
            assert data["data"]["me"]["email"] == "multidevice@example.com"
