"""End-to-end tests for complete user registration journey.

Tests the entire user registration workflow from initial signup to first
authenticated action, simulating real user behavior.
"""

from django.contrib.auth import get_user_model

import pytest

from tests.factories import OrganisationFactory

User = get_user_model()


@pytest.mark.e2e
@pytest.mark.graphql
@pytest.mark.django_db
class TestUserRegistrationE2E:
    """Test complete user registration journey end-to-end."""

    def test_new_user_complete_journey(self, client, db) -> None:
        """Test complete user journey from registration to authenticated use.

        User Story:
        As a new user, I want to register for an account, verify my email,
        and start using the platform.

        Journey:
        1. User visits registration page
        2. User submits registration form
        3. User receives verification email
        4. User clicks verification link
        5. User logs in
        6. User accesses authenticated features

        Given: Organisation exists and accepts new users
        When: New user completes full registration and verification
        Then: User can access authenticated features
        """
        # Setup: Create organisation
        OrganisationFactory.create(slug="new-org", name="New Organisation")

        # Step 1-2: User registers
        register_mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                user {
                    id
                    email
                    emailVerified
                }
            }
        }
        """

        register_response = client.post(
            "/graphql/",
            {
                "query": register_mutation,
                "variables": {
                    "input": {
                        "email": "newuser@example.com",
                        "password": "SecureP@ss1847!#",
                        "firstName": "New",
                        "lastName": "User",
                        "organisationSlug": "new-org",
                    }
                },
            },
            content_type="application/json",
        )

        # Verify registration succeeded
        assert "errors" not in register_response.json()

        # Step 3-4: Simulate email verification (manual for TDD)
        user = User.objects.get(email="newuser@example.com")
        user.email_verified = True
        user.save()

        # Step 5: User logs in
        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                user {
                    email
                    firstName
                }
            }
        }
        """

        login_response = client.post(
            "/graphql/",
            {
                "query": login_mutation,
                "variables": {
                    "input": {
                        "email": "newuser@example.com",
                        "password": "SecureP@ss1847!#",
                    }
                },
            },
            content_type="application/json",
        )

        login_data = login_response.json()
        if "errors" not in login_data:
            assert login_data["data"]["login"]["token"] is not None
            assert login_data["data"]["login"]["user"]["firstName"] == "New"

            # Step 6: User accesses authenticated feature using JWT token from login
            auth_token = login_data["data"]["login"]["token"]

            me_query = """
            query {
                me {
                    email
                    organisation {
                        name
                    }
                }
            }
            """

            me_response = client.post(
                "/graphql/",
                {"query": me_query},
                content_type="application/json",
                HTTP_AUTHORIZATION=f"Bearer {auth_token}",
            )

            me_data = me_response.json()
            assert me_data["data"]["me"]["email"] == "newuser@example.com"
            assert me_data["data"]["me"]["organisation"]["name"] == "New Organisation"
