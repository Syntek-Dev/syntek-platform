# Feature: Email Verification
# As a new user
# I want to verify my email address
# So that I can access my account securely

Feature: Email Verification
  Users must verify their email addresses to activate their accounts.
  Verification tokens are secure, expiring, and single-use.

  Background:
    Given the system is running
    And the database is clean
    And an organisation "Test Org" with slug "test-org" exists

  Scenario: Successful email verification with valid token
    Given a new user registers with email "newuser@example.com"
    And a verification email is sent to "newuser@example.com"
    When the user clicks the verification link in the email
    Then the user's email should be marked as verified
    And the verification token should be marked as used
    And the user should be able to log in

  Scenario: Email verification with expired token
    Given a user "expired@example.com" has an expired verification token
    When the user clicks the verification link
    Then the verification should fail
    And the user should see an error "Verification token has expired"
    And the user should be able to request a new verification email

  Scenario: Email verification with already used token (H12)
    Given a user "verified@example.com" has already verified their email
    When the user tries to use the same verification token again
    Then the verification should fail
    And the user should see an error "Token has already been used"

  Scenario: Resend verification email with cooldown (M2)
    Given a user "cooldown@example.com" just received a verification email
    When the user requests to resend the verification email within 5 minutes
    Then the request should be rejected
    And the user should see an error "Please wait 5 minutes before requesting a new email"

  Scenario: Resend verification email after cooldown period
    Given a user "resend@example.com" received a verification email 6 minutes ago
    When the user requests to resend the verification email
    Then a new verification email should be sent
    And the new token should be different from the old token
    And both tokens should exist in the database

  Scenario: Email verification with invalid token format
    Given a user "invalid@example.com" exists
    When the user tries to verify with token "invalid_short_token"
    Then the verification should fail
    And the user should see an error "Invalid verification token"

  Scenario: Multiple users verify independently
    Given user "user1@example.com" has a verification token
    And user "user2@example.com" has a verification token
    When user "user1@example.com" verifies their email
    Then only "user1@example.com" should be verified
    And "user2@example.com" should remain unverified

  Scenario: Email verification for already verified account
    Given a user "already@example.com" with verified email
    When the user requests a new verification email
    Then the request should be rejected
    And the user should see an error "Email is already verified"

  Scenario: Verification email contains correct information
    Given a new user "template@example.com" registers
    When a verification email is sent
    Then the email should contain the user's first name
    And the email should contain a verification link
    And the verification link should include a secure token
    And the email should mention the 24-hour expiry

  Scenario: Cleanup expired verification tokens
    Given multiple users have expired verification tokens
    When the token cleanup job runs
    Then all expired tokens should be removed
    And valid tokens should remain in the database
