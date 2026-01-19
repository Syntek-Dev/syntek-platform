# BDD Feature: Two-Factor Authentication (2FA)
# Tests complete 2FA workflows including setup, login, and backup codes

Feature: Two-Factor Authentication
  As a security-conscious user
  I want to enable two-factor authentication
  So that my account is protected with an additional security layer

  Background:
    Given the system is running
    And the database is clean
    And an organisation "Test Organisation" with slug "test-org" exists

  # ==================== 2FA SETUP ====================

  Scenario: User successfully enables 2FA
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    When the user enables 2FA
    Then 2FA should be enabled successfully
    And the user should receive a TOTP secret
    And the user should receive a QR code URL
    And the user should receive 10 backup codes
    And the TOTP device should be marked as not confirmed

  Scenario: User confirms 2FA with valid TOTP code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has enabled 2FA
    When the user submits a valid TOTP code
    Then 2FA confirmation should succeed
    And the TOTP device should be marked as confirmed
    And an audit log entry should be created for "2fa_enabled"

  Scenario: User fails to confirm 2FA with invalid TOTP code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has enabled 2FA
    When the user submits an invalid TOTP code
    Then 2FA confirmation should fail with error "Invalid authentication code"
    And the TOTP device should remain unconfirmed

  Scenario: User cannot enable 2FA twice
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has 2FA already enabled and confirmed
    When the user attempts to enable 2FA again
    Then the request should fail with error "Two-factor authentication is already enabled"

  # ==================== 2FA LOGIN FLOW ====================

  Scenario: User with 2FA logs in with valid TOTP code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    When the user submits login credentials
    Then login should indicate 2FA is required
    And no session token should be provided yet
    When the user submits a valid TOTP code
    Then 2FA verification should succeed
    And the user should receive a session token
    And the user should be fully authenticated
    And an audit log entry should be created for "2fa_login_success"

  Scenario: User with 2FA fails login with invalid TOTP code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    When the user submits login credentials
    Then login should indicate 2FA is required
    When the user submits an invalid TOTP code
    Then 2FA verification should fail with error "Invalid authentication code"
    And no session token should be provided
    And an audit log entry should be created for "2fa_login_failure"

  Scenario: User with 2FA times out during login challenge
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    When the user submits login credentials
    Then login should indicate 2FA is required
    When 10 minutes pass without submitting TOTP code
    And the user attempts to submit a TOTP code
    Then 2FA verification should fail with error "2FA challenge has expired"
    And the user should need to login again

  Scenario: User without 2FA logs in without TOTP challenge
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user does not have 2FA enabled
    When the user submits login credentials
    Then login should succeed immediately
    And the user should receive a session token
    And no 2FA challenge should be required

  # ==================== BACKUP CODES ====================

  Scenario: User logs in with valid backup code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled with backup codes
    When the user submits login credentials
    Then login should indicate 2FA is required
    When the user submits a valid backup code instead of TOTP
    Then 2FA verification should succeed
    And the user should receive a session token
    And the backup code should be marked as used
    And an audit log entry should be created for "2fa_backup_code_used"

  Scenario: User cannot reuse a backup code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled with backup codes
    And the user has used backup code "BACKUP-0001"
    When the user submits login credentials
    And the user attempts to use backup code "BACKUP-0001" again
    Then 2FA verification should fail with error "Invalid authentication code"
    And no session token should be provided

  Scenario: User generates new backup codes
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has 2FA enabled with backup codes
    When the user requests new backup codes
    Then 10 new backup codes should be generated
    And old backup codes should be invalidated
    And an audit log entry should be created for "2fa_backup_codes_regenerated"

  Scenario: User runs out of backup codes
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled with backup codes
    And all 10 backup codes have been used
    When the user loses access to their authenticator app
    Then the user should contact support for account recovery
    And the user should not be able to login without TOTP device

  # ==================== 2FA DISABLE ====================

  Scenario: User disables 2FA successfully
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has 2FA enabled and confirmed
    When the user requests to disable 2FA
    And the user confirms with their current TOTP code
    Then 2FA should be disabled successfully
    And the TOTP device should be deleted
    And backup codes should be invalidated
    And an audit log entry should be created for "2fa_disabled"
    And a security alert email should be sent

  Scenario: User cannot disable 2FA without valid TOTP code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has 2FA enabled and confirmed
    When the user requests to disable 2FA
    And the user provides an invalid TOTP code
    Then 2FA disable should fail with error "Invalid authentication code"
    And 2FA should remain enabled

  # ==================== 2FA SECURITY ====================

  Scenario: TOTP code expires after 30 seconds
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    And a TOTP code is generated at time T
    When 35 seconds pass
    And the user attempts to use the code from time T
    Then 2FA verification should fail with error "Invalid authentication code"
    And the user should generate a new code

  Scenario: TOTP code time window allows for clock drift
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    And there is a 15 second clock drift between server and user device
    When the user submits a TOTP code
    Then 2FA verification should succeed
    And the system should accept codes within ±1 time window

  Scenario: User cannot brute-force TOTP codes
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    When the user submits login credentials
    And the user attempts 5 incorrect TOTP codes in quick succession
    Then the account should be temporarily locked
    And further 2FA attempts should be blocked for 15 minutes
    And an audit log entry should be created for "2fa_brute_force_detected"
    And a security alert email should be sent

  Scenario: TOTP secret is encrypted in database
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled and confirmed
    When an attacker gains read access to the database
    Then the TOTP secret should be encrypted with Fernet
    And the attacker should not be able to extract the plain secret
    And the attacker should not be able to generate valid TOTP codes

  # ==================== 2FA RECOVERY ====================

  Scenario: User loses authenticator app and uses backup code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user has 2FA enabled with backup codes
    And the user has lost access to their authenticator app
    When the user submits login credentials
    And the user uses a valid backup code
    Then login should succeed
    And the user should be advised to set up 2FA again
    And the user should generate new backup codes

  Scenario: User disables 2FA using backup code
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in via backup code
    And the user has 2FA enabled
    When the user requests to disable 2FA
    And the user confirms with a valid backup code
    Then 2FA should be disabled successfully
    And the user should be prompted to re-enable 2FA

  # ==================== 2FA ACCOUNT SECURITY ====================

  Scenario: Password change requires 2FA verification
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has 2FA enabled and confirmed
    When the user attempts to change their password
    Then the user should be prompted for TOTP code
    When the user provides a valid TOTP code
    Then password change should succeed
    And all sessions except current should be invalidated

  Scenario: Email change requires 2FA verification
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in
    And the user has 2FA enabled and confirmed
    When the user attempts to change their email
    Then the user should be prompted for TOTP code
    When the user provides a valid TOTP code
    Then email change should succeed
    And the user should re-verify the new email address

  Scenario: All sessions revoked when 2FA is disabled
    Given a verified user exists with email "user@example.com" and password "SecureP@ss123!"
    And the user is logged in on 3 devices
    And the user has 2FA enabled and confirmed
    When the user disables 2FA from device 1
    Then all sessions on all devices should be invalidated
    And the user should need to re-authenticate on all devices
    And an audit log entry should be created for "all_sessions_revoked"

  # ==================== 2FA ADMINISTRATION ====================

  Scenario: Administrator can view user 2FA status
    Given an administrator is logged in
    And a user exists with email "user@example.com"
    And the user has 2FA enabled
    When the administrator queries the user's 2FA status
    Then the administrator should see that 2FA is enabled
    But the administrator should not see the TOTP secret
    And the administrator should not see backup codes

  Scenario: Administrator can force-disable 2FA for account recovery
    Given an administrator is logged in
    And a user exists with email "locked@example.com"
    And the user has 2FA enabled but lost all access
    When the administrator force-disables 2FA for the user
    Then 2FA should be disabled for the user
    And the user should receive a security alert email
    And an audit log entry should be created for "admin_2fa_disabled"
    And the administrator action should be logged with reason
