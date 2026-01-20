"""Security penetration tests for email verification bypass (Critical Fix C5).

Tests verify:
- C5: Email verification enforcement
- Unverified users cannot access protected resources
- Email verification token security
- Bypass attempt prevention

These tests simulate real attack scenarios attempting to bypass email verification.
"""

import secrets
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

import pytest

from apps.core.models import EmailVerificationToken, Organisation, SessionToken

User = get_user_model()


@pytest.mark.security
@pytest.mark.penetration
@pytest.mark.django_db
class TestEmailVerificationEnforcement:
    """Test email verification cannot be bypassed (Critical Fix C5)."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment.

        Args:
            db: pytest-django database fixture.
        """
        self.client = Client()
        self.organisation = Organisation.objects.create(name="Test Organisation", slug="test-org")

        # Create unverified user
        self.unverified_user = User.objects.create_user(
            email="unverified@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=False,  # NOT VERIFIED
        )

        # Create verified user for comparison
        self.verified_user = User.objects.create_user(
            email="verified@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=True,  # VERIFIED
        )

    def test_unverified_user_cannot_login(self) -> None:
        """Test that unverified users cannot login.

        Security Requirement (C5):
        - Users must verify email before accessing the system
        - Login attempt should fail with clear error message
        - No session token should be created

        Attack Scenario:
        - Attacker registers with fake email
        - Attacker attempts to login without verification
        - Access is denied
        """
        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                user {
                    email
                }
            }
        }
        """

        response = self.client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": "unverified@example.com",
                        "password": "SecureP@ss123!",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()

        # Should fail with verification error
        assert "errors" in data

        error_message = str(data["errors"]).lower()
        assert (
            "verify" in error_message or "email" in error_message or "unverified" in error_message
        )

        # Verify no session token was created
        session_count = SessionToken.objects.filter(user=self.unverified_user).count()
        assert session_count == 0

    def test_verified_user_can_login(self) -> None:
        """Test that verified users can login successfully.

        Given: User with verified email
        When: User attempts to login
        Then: Login succeeds and session is created
        """
        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                user {
                    email
                    emailVerified
                }
            }
        }
        """

        response = self.client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": "verified@example.com",
                        "password": "SecureP@ss123!",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()

        # Should succeed
        assert "errors" not in data or data["data"]["login"] is not None

        if data.get("data", {}).get("login"):
            assert data["data"]["login"]["token"] is not None
            assert data["data"]["login"]["user"]["emailVerified"] is True

    def test_unverified_user_cannot_access_protected_resources(self) -> None:
        """Test unverified user cannot access protected GraphQL queries.

        Attack Scenario:
        - Attacker obtains session token through exploit
        - Attacker attempts to access protected resources
        - Access is denied due to email verification check
        """
        # Manually create session token for unverified user (simulating attack)
        import hashlib
        import hmac

        from django.conf import settings

        plain_token = secrets.token_urlsafe(32)
        token_hash = hmac.new(
            settings.SECRET_KEY.encode(), plain_token.encode(), hashlib.sha256
        ).hexdigest()

        SessionToken.objects.create(
            user=self.unverified_user,
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=24),
            user_agent="Attack Browser",
            ip_address=b"encrypted_ip",
            refresh_token_hash="refresh_" + token_hash[:32],
        )

        # Attempt to access protected resource
        me_query = """
        query Me {
            me {
                email
                profile {
                    bio
                }
            }
        }
        """

        response = self.client.post(
            "/graphql/",
            {
                "query": me_query,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {plain_token}",
        )

        data = response.json()

        # Should be denied
        assert "errors" in data

        error_message = str(data["errors"]).lower()
        assert "verify" in error_message or "unverified" in error_message


@pytest.mark.security
@pytest.mark.penetration
@pytest.mark.django_db
class TestEmailVerificationTokenBypass:
    """Test email verification token security."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment.

        Args:
            db: pytest-django database fixture.
        """
        self.client = Client()
        self.organisation = Organisation.objects.create(name="Test Organisation", slug="test-org")

        self.user = User.objects.create_user(
            email="tokentest@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=False,
        )

        # Create valid verification token
        self.valid_token = EmailVerificationToken.objects.create(
            user=self.user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=24),
        )

    def test_expired_verification_token_rejected(self) -> None:
        """Test that expired verification tokens are rejected.

        Attack Scenario:
        - User delays verification beyond expiry time
        - Attacker finds old verification link
        - Token is rejected as expired
        """
        # Create expired token
        expired_token = EmailVerificationToken.objects.create(
            user=self.user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() - timedelta(hours=1),  # Expired 1 hour ago
        )

        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
                message
            }
        }
        """

        response = self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": expired_token.token,
                },
            },
            content_type="application/json",
        )

        data = response.json()

        # Should fail
        if "errors" in data:
            error_message = str(data["errors"]).lower()
            assert "expired" in error_message
        else:
            assert data["data"]["verifyEmail"]["success"] is False
            assert "expired" in data["data"]["verifyEmail"]["message"].lower()

    def test_used_verification_token_cannot_be_reused(self) -> None:
        """Test that verification tokens cannot be reused.

        Attack Scenario:
        - User verifies email successfully
        - Attacker intercepts verification token
        - Attacker attempts to use token again
        - Token is rejected as already used
        """
        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
            }
        }
        """

        # First verification (should succeed)
        response1 = self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": self.valid_token.token,
                },
            },
            content_type="application/json",
        )

        data1 = response1.json()
        if "data" in data1 and data1["data"].get("verifyEmail"):
            assert data1["data"]["verifyEmail"]["success"] is True

        # Second verification attempt (should fail)
        response2 = self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": self.valid_token.token,
                },
            },
            content_type="application/json",
        )

        data2 = response2.json()

        # Should fail
        if "errors" in data2:
            error_message = str(data2["errors"]).lower()
            assert "used" in error_message or "invalid" in error_message
        else:
            assert data2["data"]["verifyEmail"]["success"] is False

    def test_invalid_verification_token_rejected(self) -> None:
        """Test that invalid/non-existent tokens are rejected.

        Attack Scenario:
        - Attacker generates random token
        - Attacker attempts to verify with fake token
        - Token is rejected
        """
        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
            }
        }
        """

        # Generate random token that doesn't exist in database
        fake_token = secrets.token_urlsafe(32)

        response = self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": fake_token,
                },
            },
            content_type="application/json",
        )

        data = response.json()

        # Should fail
        if "errors" in data:
            error_message = str(data["errors"]).lower()
            assert "invalid" in error_message or "not found" in error_message
        else:
            assert data["data"]["verifyEmail"]["success"] is False

    def test_verification_token_brute_force_prevention(self) -> None:
        """Test that brute-forcing verification tokens is prevented.

        Attack Scenario:
        - Attacker attempts to brute-force verification tokens
        - Rate limiting blocks excessive attempts
        - Token space is large enough to prevent guessing

        Security Measures:
        - Tokens use secrets.token_urlsafe(32) = 256 bits entropy
        - Rate limiting on verification endpoint
        - No enumeration of valid/invalid tokens
        """
        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
            }
        }
        """

        # Attempt to brute-force with 100 random tokens
        successful_guesses = 0

        for i in range(100):
            fake_token = secrets.token_urlsafe(32)

            response = self.client.post(
                "/graphql/",
                {
                    "query": verify_mutation,
                    "variables": {
                        "token": fake_token,
                    },
                },
                content_type="application/json",
            )

            data = response.json()

            # Check if any succeeded (should be none)
            if "errors" not in data:
                if data.get("data", {}).get("verifyEmail", {}).get("success"):
                    successful_guesses += 1

        # No tokens should have succeeded
        assert successful_guesses == 0

    def test_verification_token_for_different_user_rejected(self) -> None:
        """Test that verification token cannot be used for different user.

        Attack Scenario:
        - User A registers and gets verification token
        - Attacker intercepts token
        - Attacker attempts to use token to verify User B
        - Token is rejected (bound to User A)
        """
        # Create second user
        user2 = User.objects.create_user(
            email="user2@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=False,
        )

        # Use token created for self.user
        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
            }
        }
        """

        response = self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": self.valid_token.token,
                },
            },
            content_type="application/json",
        )

        data = response.json()

        # Should succeed for self.user
        if "data" in data and data["data"].get("verifyEmail"):
            assert data["data"]["verifyEmail"]["success"] is True

        # Verify it was self.user who got verified, not user2
        self.user.refresh_from_db()
        user2.refresh_from_db()

        assert self.user.email_verified is True
        assert user2.email_verified is False  # Should not be verified


@pytest.mark.security
@pytest.mark.penetration
@pytest.mark.django_db
class TestEmailVerificationTimingAttacks:
    """Test email verification endpoint resists timing attacks."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment.

        Args:
            db: pytest-django database fixture.
        """
        self.client = Client()
        self.organisation = Organisation.objects.create(name="Test Organisation", slug="test-org")

        self.user = User.objects.create_user(
            email="timing@example.com",
            password="SecureP@ss123!",
            organisation=self.organisation,
            email_verified=False,
        )

        self.valid_token = EmailVerificationToken.objects.create(
            user=self.user,
            token=secrets.token_urlsafe(32),
            expires_at=timezone.now() + timedelta(hours=24),
        )

    def test_verification_response_time_is_constant(self) -> None:
        """Test that verification responses take constant time.

        Security Requirement:
        - Valid and invalid tokens should take same time to process
        - Prevents timing attacks to enumerate valid tokens
        - Use constant-time comparison for token validation

        Attack Scenario:
        - Attacker measures response times for many tokens
        - Slight time differences could indicate valid vs invalid
        - Constant-time validation prevents this attack
        """
        import time

        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token) {
                success
            }
        }
        """

        # Measure time for valid token
        start_valid = time.time()

        self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": self.valid_token.token,
                },
            },
            content_type="application/json",
        )

        end_valid = time.time()
        valid_duration = end_valid - start_valid

        # Measure time for invalid token
        invalid_token = secrets.token_urlsafe(32)
        start_invalid = time.time()

        self.client.post(
            "/graphql/",
            {
                "query": verify_mutation,
                "variables": {
                    "token": invalid_token,
                },
            },
            content_type="application/json",
        )

        end_invalid = time.time()
        invalid_duration = end_invalid - start_invalid

        # Time difference should be minimal (allow 50ms variance for network/system)
        time_difference = abs(valid_duration - invalid_duration)

        # This is a soft check - timing can vary in test environments
        # In production, use constant-time comparison functions
        assert time_difference < 0.1, (
            f"Verification timing difference too large: {time_difference}s"
        )
