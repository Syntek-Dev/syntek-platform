# User Story: User Login with Two-Factor Authentication (2FA)

<!-- CLICKUP_ID: 86c7d2kwy -->

## Overview

Secure login system with optional two-factor authentication (TOTP), JWT token generation, session management, and account security features. Includes backup codes for recovery, rate limiting on failed attempts, account lockout mechanisms, and audit logging of all login events. Enables optional 2FA enforcement policies and remember device functionality.

---

## Story

**As a** registered user
**I want** to log in with my email and password, with optional two-factor authentication
**So that** only I can access my account, even if my password is compromised

## MoSCoW Priority

- **Must Have:** Basic login validation, 2FA option for admin users, JWT token generation, session management
- **Should Have:** Remember device option, backup codes for recovery, 2FA enforcement policy
- **Could Have:** Biometric login on mobile, single sign-on (SSO) integration
- **Won't Have:** Third-party MFA providers in Phase 1

**Sprint:** Sprint 22

## Repository Coverage

| Repository      | Required | Notes                                                      |
| --------------- | -------- | ---------------------------------------------------------- |
| Backend         | ✅       | 2FA verification, JWT token generation, session management |
| Frontend Web    | ✅       | Login form, 2FA code entry, 2FA setup wizard               |
| Frontend Mobile | ✅       | Login form with biometric support                          |
| Shared UI       | ✅       | Login form components, OTP input component                 |

## Acceptance Criteria

### Scenario 1: Successful Login without 2FA

**Given** a user with 2FA disabled
**When** they enter correct email and password
**Then** they are authenticated
**And** a JWT token is issued
**And** they are redirected to the dashboard
**And** a login audit log is created with their IP address

### Scenario 2: Login with 2FA Required

**Given** a user with 2FA enabled
**When** they enter correct email and password
**Then** they are prompted to enter their 2FA code
**And** they have 2 minutes to enter the code
**And** invalid codes show an error message
**And** invalid attempts are rate-limited to 3 attempts per minute

### Scenario 3: Valid 2FA Code

**Given** a user is prompted for a 2FA code
**When** they enter a valid TOTP code
**Then** they are authenticated
**And** a JWT token is issued
**And** they are redirected to the dashboard
**And** the login audit log is marked as 2FA verified

### Scenario 4: Failed Login Attempts

**Given** a user enters an incorrect password
**When** they attempt to log in
**Then** an error message is displayed (without revealing if email exists)
**And** the failed attempt is logged
**And** after 5 failed attempts in 15 minutes, the account is temporarily locked
**And** the user is notified via email

### Scenario 5: Using Backup Codes

**Given** a user has lost access to their 2FA device
**When** they enter a backup code instead of TOTP
**Then** the backup code is validated
**And** the account is logged in
**And** a system notification alerts the user to reset their 2FA device

## Dependencies

- US-001: User Authentication with Email and Password
- django-otp for TOTP implementation
- JWT token management library
- Email service for notifications

## Tasks

### Backend Tasks

- [ ] Install and configure django-otp package
- [ ] Create 2FA setup flow with secret generation
- [ ] Implement TOTP verification logic
- [ ] Generate backup codes (8 codes, single-use)
- [ ] Create failed login attempt tracking
- [ ] Implement account lockout mechanism (5 attempts in 15 min)
- [ ] Create JWT token generation and validation
- [ ] Implement token refresh mechanism
- [ ] Create login GraphQL mutation with 2FA support
- [ ] Create 2FA setup GraphQL mutation
- [ ] Create audit logging for login events
- [ ] Implement rate limiting on login endpoint
- [ ] Create email notifications for failed login attempts
- [ ] Add unit tests for 2FA flow
- [ ] Add integration tests for complete login flow

### Frontend Web Tasks

- [ ] Create login form component
- [ ] Create 2FA code entry component (6-digit input)
- [ ] Create 2FA setup wizard
- [ ] Display backup codes and download option
- [ ] Implement session token storage and refresh
- [ ] Add login attempt tracking on client
- [ ] Create password visibility toggle
- [ ] Implement "remember device" option (30 days)

### Frontend Mobile Tasks

- [ ] Create login form for mobile
- [ ] Implement biometric authentication (Face ID/Touch ID)
- [ ] Create 2FA code entry component
- [ ] Create 2FA setup wizard for mobile

### Shared UI Tasks

- [ ] Create FormInput component with security features
- [ ] Create OTPInput component (auto-focus, auto-submit)
- [ ] Create TogglePassword component
- [ ] Create AlertBox component for security messages

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- Two-factor authentication (TOTP) implementation
- Token management and refresh logic
- Security features (rate limiting, account lockout)
- Backup code generation and validation
- Multi-platform implementation
- Comprehensive testing required for security feature
- Email notification integration
- Audit logging integration

---

## Related Stories

- US-001: User Authentication with Email and Password
- US-003: Password Reset and Recovery
- US-025: Audit Logging System
