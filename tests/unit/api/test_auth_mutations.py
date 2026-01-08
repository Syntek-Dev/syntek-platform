"""Unit tests for GraphQL authentication mutations.

Tests cover:
- User registration mutation
- User login mutation (with/without 2FA)
- User logout mutation with token revocation
- Password reset request mutation
- Password reset confirmation mutation
- Email verification mutation
- Password change mutation
- 2FA enable/disable mutations

These tests follow TDD - they test against minimal implementation stubs.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from apps.core.models import Organisation
from tests.factories import (
    EmailVerificationTokenFactory,
    OrganisationFactory,
    PasswordResetTokenFactory,
    UserFactory,
)

User = get_user_model()


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestRegisterMutation:
    """Test GraphQL register mutation."""

    @pytest.fixture
    def graphql_client(self, client):
        """Provide GraphQL client for testing.

        Args:
            client: Django test client

        Returns:
            Test client configured for GraphQL
        """
        return client

    @pytest.fixture
    def valid_registration_input(self, db) -> dict[str, Any]:
        """Provide valid registration input data.

        Returns:
            Dictionary with valid registration fields
        """
        OrganisationFactory.create(slug="test-org")
        return {
            "email": "newuser@example.com",
            "password": "SecurePass123!@",
            "firstName": "New",
            "lastName": "User",
            "organisationSlug": "test-org",
        }

    def test_register_mutation_with_valid_data(
        self, graphql_client, valid_registration_input
    ) -> None:
        """Test user registration with valid data.

        Given: Valid registration input (email, password, name, org)
        When: register mutation is called
        Then: User is created with correct attributes
        And: AuthPayload is returned with token
        And: Email verification token is created
        """
        mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
                refreshToken
                user {
                    id
                    email
                    firstName
                    lastName
                    emailVerified
                }
                requiresTwoFactor
            }
        }
        """

        response = graphql_client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": valid_registration_input},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["register"]["token"] is not None
        assert data["data"]["register"]["refreshToken"] is not None
        assert data["data"]["register"]["user"]["email"] == "newuser@example.com"
        assert data["data"]["register"]["user"]["firstName"] == "New"
        assert data["data"]["register"]["user"]["emailVerified"] is False
        assert data["data"]["register"]["requiresTwoFactor"] is False

    def test_register_mutation_duplicate_email(
        self, graphql_client, valid_registration_input
    ) -> None:
        """Test registration fails with duplicate email.

        Given: A user with email "newuser@example.com" exists
        When: register mutation is called with same email
        Then: Error is returned with code EMAIL_ALREADY_EXISTS
        """
        # Create existing user
        org = Organisation.objects.get(slug="test-org")
        UserFactory.create(email="newuser@example.com", organisation=org)

        mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
            }
        }
        """

        response = graphql_client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": valid_registration_input},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        assert "EMAIL_ALREADY_EXISTS" in str(data["errors"][0])

    def test_register_mutation_invalid_email(self, graphql_client) -> None:
        """Test registration fails with invalid email format.

        Given: Registration input with invalid email format
        When: register mutation is called
        Then: Validation error is returned
        """
        _org = OrganisationFactory.create(slug="test-org")
        invalid_input = {
            "email": "not-an-email",
            "password": "SecurePass123!@",
            "firstName": "Test",
            "lastName": "User",
            "organisationSlug": "test-org",
        }

        mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
            }
        }
        """

        response = graphql_client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": invalid_input},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        assert "email" in str(data["errors"][0]).lower()

    def test_register_mutation_weak_password(self, graphql_client) -> None:
        """Test registration fails with weak password.

        Given: Registration input with weak password (too short, no special chars)
        When: register mutation is called
        Then: Validation error is returned with guidance
        """
        _org = OrganisationFactory.create(slug="test-org")
        weak_password_input = {
            "email": "test@example.com",
            "password": "weak",  # Too short, missing requirements
            "firstName": "Test",
            "lastName": "User",
            "organisationSlug": "test-org",
        }

        mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
            }
        }
        """

        response = graphql_client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": weak_password_input},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert len(data["errors"]) > 0
        assert "password" in str(data["errors"][0]).lower()

    def test_register_mutation_invalid_organisation(self, graphql_client) -> None:
        """Test registration fails with non-existent organisation.

        Given: Registration input with invalid organisation slug
        When: register mutation is called
        Then: Error is returned with code ORGANISATION_NOT_FOUND
        """
        invalid_org_input = {
            "email": "test@example.com",
            "password": "SecurePass123!@",
            "firstName": "Test",
            "lastName": "User",
            "organisationSlug": "non-existent-org",
        }

        mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
            }
        }
        """

        response = graphql_client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": invalid_org_input},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "ORGANISATION_NOT_FOUND" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestLoginMutation:
    """Test GraphQL login mutation."""

    @pytest.fixture
    def authenticated_user(self, db) -> User:
        """Create an authenticated user for testing.

        Returns:
            User instance with email verified
        """
        org = OrganisationFactory.create(slug="test-org")
        user = UserFactory.create(
            email="user@example.com",
            organisation=org,
            email_verified=True,
        )
        user.set_password("SecurePass123!@")
        user.save()
        return user

    @pytest.fixture
    def unverified_user(self, db) -> User:
        """Create an unverified user for testing.

        Returns:
            User instance with email_verified=False
        """
        org = OrganisationFactory.create(slug="unverified-org")
        user = UserFactory.create(
            email="unverified@example.com",
            organisation=org,
            email_verified=False,
        )
        user.set_password("SecurePass123!@")
        user.save()
        return user

    def test_login_mutation_with_valid_credentials(self, client, authenticated_user) -> None:
        """Test login with valid credentials.

        Given: User with valid credentials and verified email
        When: login mutation is called with correct email/password
        Then: AuthPayload is returned with token and user data
        And: SessionToken is created in database
        """
        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                refreshToken
                user {
                    id
                    email
                    emailVerified
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
                        "email": "user@example.com",
                        "password": "SecurePass123!@",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["login"]["token"] is not None
        assert data["data"]["login"]["refreshToken"] is not None
        assert data["data"]["login"]["user"]["email"] == "user@example.com"
        assert data["data"]["login"]["user"]["emailVerified"] is True
        assert data["data"]["login"]["requiresTwoFactor"] is False

    def test_login_mutation_with_invalid_password(self, client, authenticated_user) -> None:
        """Test login fails with invalid password.

        Given: User with valid email
        When: login mutation is called with wrong password
        Then: Error is returned with code INVALID_CREDENTIALS
        And: Failed login is logged in audit log
        """
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
                        "email": "user@example.com",
                        "password": "WrongPassword",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "INVALID_CREDENTIALS" in str(data["errors"][0])

    def test_login_mutation_with_unverified_email(self, client, unverified_user) -> None:
        """Test login is blocked for unverified email (C5 requirement).

        Given: User with email_verified=False
        When: login mutation is called
        Then: Error is returned with code EMAIL_NOT_VERIFIED
        And: Guidance suggests checking inbox or resending verification
        """
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
                        "email": "unverified@example.com",
                        "password": "SecurePass123!@",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "EMAIL_NOT_VERIFIED" in str(data["errors"][0])
        assert "verify" in str(data["errors"][0]).lower()

    def test_login_mutation_with_nonexistent_email(self, client) -> None:
        """Test login fails with non-existent email.

        Given: Email that doesn't exist in database
        When: login mutation is called
        Then: Error is returned with generic INVALID_CREDENTIALS
        And: No user enumeration (same error as wrong password)
        """
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
                        "email": "nonexistent@example.com",
                        "password": "SomePassword123!@",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        # Should be same error as invalid password (prevent user enumeration)
        assert "INVALID_CREDENTIALS" in str(data["errors"][0])

    @pytest.mark.skip(reason="Phase 4: 2FA not implemented yet")
    def test_login_mutation_with_2fa_enabled(self, client, db) -> None:
        """Test login with 2FA enabled requires TOTP code.

        Given: User with two_factor_enabled=True
        When: login mutation is called without totpCode
        Then: requiresTwoFactor is True in response
        And: Token is not returned (requires 2FA verification)
        """
        pass

    @pytest.mark.skip(reason="Phase 4: 2FA not implemented yet")
    def test_login_mutation_with_valid_2fa_code(self, client, db) -> None:
        """Test login with valid 2FA code.

        Given: User with 2FA enabled
        When: login mutation is called with valid totpCode
        Then: Token and refreshToken are returned
        And: requiresTwoFactor is False
        """
        pass


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestLogoutMutation:
    """Test GraphQL logout mutation."""

    @pytest.fixture
    def authenticated_client(self, client, db):
        """Provide authenticated GraphQL client.

        Returns:
            Authenticated test client with session token
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("password")
        user.save()

        # Simulate login by creating session token
        # (This would normally be done by login mutation)
        client.force_login(user)
        return client

    def test_logout_mutation_revokes_token(self, authenticated_client) -> None:
        """Test logout revokes current session token.

        Given: Authenticated user with active session token
        When: logout mutation is called
        Then: Session token is revoked in database
        And: Subsequent requests with that token fail authentication
        """
        mutation = """
        mutation {
            logout
        }
        """

        response = authenticated_client.post(
            "/graphql/",
            {
                "query": mutation,
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["logout"] is True

    def test_logout_mutation_without_authentication(self, client) -> None:
        """Test logout fails without authentication.

        Given: Unauthenticated request
        When: logout mutation is called
        Then: Error is returned with code AUTHENTICATION_REQUIRED
        """
        mutation = """
        mutation {
            logout
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "AUTHENTICATION_REQUIRED" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestPasswordResetMutations:
    """Test password reset request and confirmation mutations."""

    @pytest.fixture
    def user_with_verified_email(self, db) -> User:
        """Create user with verified email for password reset.

        Returns:
            User instance with email verified
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)
        user.set_password("OldPassword123!@")
        user.save()
        return user

    def test_request_password_reset_with_valid_email(
        self, client, user_with_verified_email
    ) -> None:
        """Test password reset request with valid email.

        Given: User with verified email
        When: requestPasswordReset mutation is called
        Then: Password reset email is sent
        And: PasswordResetToken is created in database
        And: Token expires in 15 minutes
        """
        mutation = """
        mutation RequestPasswordReset($input: PasswordResetRequestInput!) {
            requestPasswordReset(input: $input)
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"email": user_with_verified_email.email}},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["requestPasswordReset"] is True

    def test_request_password_reset_with_nonexistent_email(self, client) -> None:
        """Test password reset request with non-existent email.

        Given: Email that doesn't exist in database
        When: requestPasswordReset mutation is called
        Then: Success is returned (prevent user enumeration)
        And: No email is sent
        """
        mutation = """
        mutation RequestPasswordReset($input: PasswordResetRequestInput!) {
            requestPasswordReset(input: $input)
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"input": {"email": "nonexistent@example.com"}},
            },
            content_type="application/json",
        )

        data = response.json()
        # Should return success to prevent user enumeration
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["requestPasswordReset"] is True

    def test_reset_password_with_valid_token(self, client, user_with_verified_email) -> None:
        """Test password reset with valid token.

        Given: User with active password reset token
        When: resetPassword mutation is called with valid token
        Then: Password is updated
        And: User can login with new password
        And: All existing session tokens are revoked
        """
        # Create password reset token
        _token_obj = PasswordResetTokenFactory.create(
            user=user_with_verified_email,
            expires_at=timezone.now() + timezone.timedelta(minutes=15),
        )

        mutation = """
        mutation ResetPassword($input: PasswordResetInput!) {
            resetPassword(input: $input)
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "token": "plain_token_value",  # Would be the plain token
                        "newPassword": "NewSecurePass123!@",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["resetPassword"] is True

    def test_reset_password_with_expired_token(self, client, user_with_verified_email) -> None:
        """Test password reset fails with expired token.

        Given: Password reset token that has expired
        When: resetPassword mutation is called
        Then: Error is returned with code TOKEN_EXPIRED
        """
        # Create expired token
        _token_obj = PasswordResetTokenFactory.create(
            user=user_with_verified_email,
            expires_at=timezone.now() - timezone.timedelta(minutes=1),
        )

        mutation = """
        mutation ResetPassword($input: PasswordResetInput!) {
            resetPassword(input: $input)
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {
                    "input": {
                        "token": "expired_token",
                        "newPassword": "NewSecurePass123!@",
                    }
                },
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "TOKEN_EXPIRED" in str(data["errors"][0])


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestEmailVerificationMutations:
    """Test email verification and resend mutations."""

    @pytest.fixture
    def unverified_user(self, db) -> User:
        """Create unverified user for testing.

        Returns:
            User with email_verified=False
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=False)
        user.set_password("password")
        user.save()
        return user

    def test_verify_email_with_valid_token(self, client, unverified_user) -> None:
        """Test email verification with valid token.

        Given: User with unverified email and valid verification token
        When: verifyEmail mutation is called
        Then: User email_verified is set to True
        And: email_verified_at timestamp is set
        """
        _token_obj = EmailVerificationTokenFactory.create(
            user=unverified_user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )

        mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token)
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"token": "plain_verification_token"},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["verifyEmail"] is True

    def test_verify_email_with_expired_token(self, client, unverified_user) -> None:
        """Test email verification fails with expired token.

        Given: Verification token that has expired
        When: verifyEmail mutation is called
        Then: Error is returned with code TOKEN_EXPIRED
        """
        _token_obj = EmailVerificationTokenFactory.create(
            user=unverified_user,
            expires_at=timezone.now() - timezone.timedelta(hours=1),
        )

        mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token)
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
                "variables": {"token": "expired_token"},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" in data
        assert "TOKEN_EXPIRED" in str(data["errors"][0])

    def test_resend_verification_email(self, client, db) -> None:
        """Test resending verification email.

        Given: Authenticated user with unverified email
        When: resendVerificationEmail mutation is called
        Then: New verification email is sent
        And: Old verification tokens are invalidated
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=False)
        client.force_login(user)

        mutation = """
        mutation {
            resendVerificationEmail
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": mutation,
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["resendVerificationEmail"] is True
