# Feature: Password Reset
# As a user who forgot their password
# I want to reset my password securely
# So that I can regain access to my account

Feature: Password Reset
  Users can reset their passwords using secure, time-limited, single-use tokens.
  Password reset enforces security requirements including history and strength.

  Background:
    Given the system is running
    And the database is clean
    And an organisation "Test Org" with slug "test-org" exists

  Scenario: Successful password reset with valid token (C3)
    Given a user "user@example.com" with password "OldPassword123!@"
    And the user requests a password reset
    And a password reset email is sent to "user@example.com"
    When the user clicks the reset link with valid token
    And submits new password "NewSecurePass456!@"
    Then the password should be updated
    And the reset token should be marked as used (H12)
    And all user sessions should be revoked
    And the user should be able to log in with the new password

  Scenario: Password reset token is hashed in database (C3)
    Given a user "hash@example.com" requests a password reset
    When the reset token is generated
    Then the token should be hashed before storage
    And the plain token should not appear in the database
    And the hash should use HMAC-SHA256

  Scenario: Password reset with expired token
    Given a user "expired@example.com" has an expired reset token (16 minutes old)
    When the user tries to use the reset token
    Then the reset should fail
    And the user should see an error "Reset token has expired"
    And the user should be able to request a new reset link

  Scenario: Password reset token single-use enforcement (H12)
    Given a user "single@example.com" has a valid reset token
    When the user resets their password to "FirstPassword456!@"
    And the user tries to use the same token again with password "SecondPassword789!@"
    Then the second reset should fail
    And the password should remain "FirstPassword456!@"
    And the user should see an error "Token has already been used"

  Scenario: Password reset prevents password reuse (H11)
    Given a user "history@example.com" has password history:
      | Password          | Days Ago |
      | OldPassword1!@    | 5        |
      | OldPassword2!@    | 10       |
      | OldPassword3!@    | 15       |
      | OldPassword4!@    | 20       |
      | OldPassword5!@    | 25       |
    And the user requests a password reset
    When the user tries to reset password to "OldPassword2!@"
    Then the reset should fail
    And the user should see an error "Cannot reuse recent passwords"

  Scenario: Password reset validates password strength
    Given a user "weak@example.com" has a valid reset token
    When the user tries to reset password to "weak"
    Then the reset should fail
    And the user should see an error "Password does not meet requirements"

  Scenario Outline: Password strength validation during reset
    Given a user "strength@example.com" has a valid reset token
    When the user submits password "<password>"
    Then the result should be "<result>"

    Examples:
      | password            | result  |
      | Short1!             | failure |
      | nocapitals123!      | failure |
      | NOLOWERCASE123!     | failure |
      | NoNumbers!@         | failure |
      | NoSpecialChar123    | failure |
      | ValidPassword123!@  | success |

  Scenario: Password reset revokes all active sessions
    Given a user "sessions@example.com" has 3 active sessions
    And the user requests a password reset
    When the user completes the password reset
    Then all 3 sessions should be revoked
    And the user must log in again on all devices

  Scenario: Multiple password reset requests create new tokens
    Given a user "multiple@example.com" requests a password reset
    And 5 minutes pass
    When the user requests another password reset
    Then a new reset token should be generated
    And both tokens should exist in the database
    And only the latest token should work

  Scenario: Password reset with invalid token
    Given a user "invalid@example.com" exists
    When the user tries to reset password with token "invalid_token_xyz"
    Then the reset should fail
    And the password should remain unchanged

  Scenario: Password reset email contains correct information
    Given a user "email@example.com" requests a password reset
    When the reset email is sent
    Then the email should contain the user's name
    And the email should contain a password reset link
    And the email should mention the 15-minute expiry
    And the email should warn about unsolicited requests

  Scenario: Password reset cleanup removes expired tokens
    Given multiple users have expired reset tokens
    When the token cleanup job runs
    Then expired tokens should be removed
    And valid tokens should remain

  Scenario: Password reset for non-existent user
    Given no user with email "nonexistent@example.com" exists
    When a password reset is requested for "nonexistent@example.com"
    Then the request should appear to succeed (security)
    But no email should be sent
    And no token should be created

  Scenario: Password reset rate limiting
    Given a user "ratelimit@example.com" exists
    When the user requests password reset 10 times in 5 minutes
    Then the 11th request should be rejected
    And the user should see an error "Too many password reset attempts"

  Scenario: Password reset with IP address tracking
    Given a user "tracking@example.com" requests a password reset from IP "203.0.113.42"
    When the reset is completed
    Then the audit log should record IP address "203.0.113.42"
    And the audit log should record the password reset action
