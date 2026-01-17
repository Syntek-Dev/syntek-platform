# BDD Feature: Authentication Edge Cases
# Tests all 27 edge cases identified in QA review for US-001

Feature: Authentication Edge Cases and Security
  As a security-conscious system
  I want to handle all edge cases correctly
  So that authentication is robust and secure

  Background:
    Given the system is running
    And the database is clean
    And an organisation "Test Org" with slug "test-org" exists

  # Edge Case #1: Empty email/password
  Scenario: Login fails with empty email
    When I attempt to login with empty email and password "SecureP@ss123!"
    Then login should fail with error "Email is required"

  Scenario: Login fails with empty password
    When I attempt to login with email "user@example.com" and empty password
    Then login should fail with error "Password is required"

  # Edge Case #2: Email with leading/trailing spaces
  Scenario: Registration normalises email with spaces
    When I register with email " user@example.com " and password "SecureP@ss123!"
    Then registration should succeed
    And the user email should be stored as "user@example.com"
    And the user email should be lowercase

  Scenario: Login works with email containing spaces
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    When I login with email " USER@EXAMPLE.COM " and password "SecureP@ss123!"
    Then login should succeed
    And I should receive a valid session token

  # Edge Case #3: Unicode in names
  Scenario Outline: Registration accepts Unicode characters in names
    When I register with first name "<first_name>" and last name "<last_name>"
    Then registration should succeed
    And the user name should be stored correctly with Unicode

    Examples:
      | first_name | last_name  |
      | José       | García     |
      | François   | Müller     |
      | 李         | 明         |
      | Владимир   | Петров     |
      | محمد       | أحمد       |

  # Edge Case #4: Very long passwords
  Scenario: Registration rejects password over 128 characters
    When I register with a password of 129 characters
    Then registration should fail with error "Password must not exceed 128 characters"

  Scenario: Registration accepts password of exactly 128 characters
    When I register with a password of 128 characters
    Then registration should succeed

  # Edge Case #5: SQL injection in email
  Scenario Outline: System prevents SQL injection attempts in email
    When I attempt to register with email "<malicious_email>"
    Then registration should fail with validation error
    And no SQL injection should occur
    And the database should remain unchanged

    Examples:
      | malicious_email                           |
      | admin@example.com'; DROP TABLE users;--   |
      | ' OR '1'='1                               |
      | admin@example.com' UNION SELECT * FROM -- |

  # Edge Case #6: XSS in user fields
  Scenario Outline: System prevents XSS attempts in user fields
    When I register with first name "<xss_payload>" and last name "User"
    Then registration should succeed
    And the output should be properly escaped
    And the XSS payload should not execute

    Examples:
      | xss_payload                              |
      | <script>alert('XSS')</script>            |
      | <img src=x onerror=alert('XSS')>         |
      | javascript:alert('XSS')                  |
      | <svg/onload=alert('XSS')>                |

  # Edge Case #7: CSRF on mutations
  Scenario: GraphQL mutations require CSRF protection
    Given CSRF protection is enabled
    When I submit a login mutation without CSRF token
    Then the request should fail with CSRF error
    And no authentication should occur

  Scenario: GraphQL mutations succeed with valid CSRF token
    Given CSRF protection is enabled
    And I have a valid CSRF token
    When I submit a login mutation with the CSRF token
    Then login should succeed

  # Edge Case #8: Concurrent session creation
  Scenario: System handles simultaneous login attempts
    Given a verified user exists with email "user@example.com"
    When the user attempts to login from 5 different devices simultaneously
    Then all 5 login attempts should succeed
    And 5 separate session tokens should be created
    And each token should be unique
    And no race conditions should occur

  # Edge Case #9: Token collision
  Scenario: System prevents session token collisions
    Given 100 users attempt to login simultaneously
    When all users successfully authenticate
    Then all 100 session tokens should be unique
    And no token collisions should occur

  # Edge Case #10: Expired token usage
  Scenario: Login fails with expired session token
    Given a user has a session token that expired 1 hour ago
    When the user attempts to access a protected resource
    Then access should be denied
    And error should indicate "Session expired"

  Scenario: Email verification fails with expired token
    Given a user registered 25 hours ago
    And the verification token has expired (24 hour TTL)
    When the user attempts to verify their email
    Then verification should fail with error "Verification token has expired"

  # Edge Case #11: Revoked token replay
  Scenario: User cannot use token after logout
    Given a user is logged in with a valid session token
    When the user logs out
    And the user attempts to use the same token
    Then access should be denied
    And error should indicate "Token has been revoked"

  Scenario: Password change revokes all existing tokens
    Given a user is logged in on 3 different devices
    When the user changes their password
    Then all 3 session tokens should be revoked
    And all subsequent requests with old tokens should fail

  # Edge Case #12: Password reset token reuse
  Scenario: Password reset token cannot be reused
    Given a user requested a password reset
    And the user successfully reset their password using the token
    When the user attempts to use the same token again
    Then the reset should fail with error "Reset token has already been used"

  # Edge Case #13: 2FA code timing attack
  Scenario: TOTP validation uses constant-time comparison
    Given a user has 2FA enabled
    When an attacker attempts timing attacks on TOTP codes
    Then all validation attempts should take constant time
    And timing attacks should be prevented

  # Edge Case #14: Backup code enumeration
  Scenario: Backup code validation prevents enumeration
    Given a user has 2FA backup codes
    When multiple invalid backup codes are tried
    Then each attempt should return the same generic error
    And response time should be constant
    And valid/invalid codes should be indistinguishable

  # Edge Case #15: Rate limit bypass (IP spoofing)
  Scenario: Rate limiting validates X-Forwarded-For header
    Given rate limiting is configured for 5 login attempts per 15 minutes
    When an attacker tries to bypass rate limiting with spoofed IP headers
    Then the spoofed headers should be ignored
    And rate limiting should still apply
    And the 6th attempt should be blocked

  # Edge Case #16: Organisation boundary bypass
  Scenario: Users cannot access other organisation's data
    Given user "user1@example.com" belongs to organisation "org-1"
    And user "user2@example.com" belongs to organisation "org-2"
    When user1 attempts to query user2's profile
    Then access should be denied
    And organisation boundary should be enforced

  # Edge Case #17: Superuser org access
    Scenario: Platform superusers can access all organisations
    Given a platform superuser exists without organisation assignment
    When the superuser queries data from organisation "test-org"
    Then access should be granted
    And Row-Level Security should bypass for superusers

  # Edge Case #18: Deleted user token usage
  Scenario: Deactivated user cannot use existing tokens
    Given a user is logged in with a valid token
    When an administrator deactivates the user account
    And the user attempts to use their existing token
    Then access should be denied
    And error should indicate "Account has been deactivated"

  # Edge Case #19: Email change invalidation
  Scenario: Email change requires re-verification
    Given a verified user exists with email "old@example.com"
    When the user changes their email to "new@example.com"
    Then the user's email_verified flag should be set to False
    And a new verification email should be sent
    And the user should re-verify before full access

  # Edge Case #20: Password change session handling
  Scenario: Password change requires re-authentication
    Given a user is logged in on multiple devices
    When the user changes their password on device 1
    Then all other device sessions should be invalidated
    And the user should need to re-authenticate on those devices
    And only the current device session should remain active

  # Edge Case #21: Timezone DST edge cases
  Scenario: Token expiry handles Daylight Saving Time transitions
    Given a token is created at 01:30 during DST transition
    And the token has a 24-hour expiry
    When DST transitions occur (spring forward or fall back)
    Then the token expiry should be calculated correctly
    And timezone-aware datetime should handle the transition

  # Edge Case #22: Leap second handling
  Scenario: System handles leap seconds correctly
    Given a token is created during a leap second event
    When the system processes timestamps
    Then Django's timezone.now() should handle leap seconds
    And no timestamp calculation errors should occur

  # Edge Case #23: Redis unavailability
  Scenario: System degrades gracefully when Redis is unavailable
    Given Redis cache is unavailable
    When a user attempts to login
    Then the system should fall back to database-only mode
    And login should still succeed
    And session should be managed via database

  # Edge Case #24: Database connection pool exhaustion
  Scenario: System handles database connection pool exhaustion
    Given 100 simultaneous login requests occur
    And the connection pool has 20 connections
    When requests exceed available connections
    Then requests should queue and wait for available connections
    And no requests should fail due to connection exhaustion
    And PgBouncer should manage connection pooling

  # Edge Case #25: Very long user agent strings
  Scenario: System handles extremely long user agent strings
    When a login request includes a user agent of 10000 characters
    Then the login should succeed
    And the user agent should be truncated to maximum allowed length
    And no database error should occur

  # Edge Case #26: Malformed JWT
  Scenario Outline: System handles malformed JWT tokens gracefully
    When a request includes a malformed JWT token "<malformed_token>"
    Then access should be denied
    And error should indicate "Invalid token format"
    And no server error should occur

    Examples:
      | malformed_token                    |
      | not.a.jwt                          |
      | header.payload                     |
      | header.payload.signature.extra     |
      |                                    |
      | ####.####.####                     |

  # Edge Case #27: Key rotation during active sessions
  Scenario: Active sessions work during JWT key rotation
    Given 100 users have active sessions with current JWT key
    When the JWT signing key is rotated to a new key
    And the system accepts both old and new keys for 1 hour
    Then existing sessions should continue to work
    And new sessions should use the new key
    And after 1 hour, only the new key should be accepted

  # Critical Fix C1: Session token storage with HMAC
  Scenario: Session tokens are hashed with HMAC-SHA256
    Given a user logs in successfully
    When the session token is stored in the database
    Then the token should be hashed using HMAC-SHA256
    And the plain token should never be stored
    And the hash should use a secret key from environment

  # Critical Fix C2: TOTP secret encryption
  Scenario: TOTP secrets are encrypted with Fernet
    Given a user enables 2FA
    When the TOTP secret is stored in the database
    Then the secret should be encrypted using Fernet encryption
    And the encryption key should be separate from session keys
    And the secret should never be stored in plain text

  # Critical Fix C3: Password reset token hashing
  Scenario: Password reset tokens are hashed before storage
    Given a user requests a password reset
    When the reset token is generated
    Then the token hash should be stored using HMAC-SHA256
    And the plain token should be sent to the user via email
    And the plain token should never touch the database

  # Critical Fix C4: CSRF protection for GraphQL
  Scenario: GraphQL mutations are protected against CSRF
    Given a user is logged in
    When the user submits a mutation without CSRF token
    Then the mutation should be rejected
    And CSRF middleware should validate the token

  # Critical Fix C5: Email verification enforcement
  Scenario: Unverified users cannot access protected resources
    Given a user registered but has not verified their email
    When the user attempts to login
    Then login should be blocked
    And error should indicate "Please verify your email address"

  # Critical Fix C6: IP encryption key rotation
  Scenario: IP addresses are re-encrypted during key rotation
    Given 1000 users have encrypted IP addresses in audit logs
    When the IP encryption key is rotated
    Then a background job should re-encrypt all historical IPs
    And the old key should be retained until re-encryption completes
    And audit logs should continue to be accessible
