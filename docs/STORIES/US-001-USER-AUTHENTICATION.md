# User Story: User Authentication with Email and Password

<!-- CLICKUP_ID: 86c7d2kp1 -->

**Phase 1 Status:** ✅ Completed (07/01/2026)
**Phase 2 Status:** ✅ Completed (08/01/2026)
**Phase 3 Status:** ✅ Completed (09/01/2026)
**Phase 4 Status:** ✅ Completed (15/01/2026)
**Phase 5 Status:** ✅ Completed (16/01/2026)
**Phase 6 Status:** ✅ Completed (17/01/2026)
**Phase 7 Status:** ✅ Completed (17/01/2026)
**Overall Status:** ✅ Backend Complete | ⬜ Frontend Pending

## Overview

Core authentication system allowing new users to create accounts with email and password, including email verification, password validation, token management, and security features like encryption and audit logging. Backend implementation complete (Phases 1-7) covering models, services, GraphQL API, 2FA, password reset, email verification, audit logging, and security hardening. Frontend implementations across web, mobile, and shared UI pending.

---

## Story

**As a** new user
**I want** to create an account with an email address and password
**So that** I can access the Syntek CMS platform and manage my content

## MoSCoW Priority

- **Must Have:** User registration with validation, email verification, password hashing, secure storage
- **Should Have:** Welcome email notification, registration form with clear feedback
- **Could Have:** Social login integration (OAuth), pre-filled profile suggestions
- **Won't Have:** Third-party account federation in Phase 1

**Sprint:** Sprint 01

## Repository Coverage

| Repository      | Required | Notes                                                     |
| --------------- | -------- | --------------------------------------------------------- |
| Backend         | ✅       | User model, email service, GraphQL mutations              |
| Frontend Web    | ✅       | Registration form, email verification page                |
| Frontend Mobile | ✅       | Registration form for mobile app                          |
| Shared UI       | ✅       | Registration form components, input validation components |

## Acceptance Criteria

### Scenario 1: Successful User Registration

**Given** the registration page is open
**When** a user enters a valid email, password, first name, and last name
**And** clicks the register button
**Then** an account is created in the system
**And** an email verification link is sent to their email address
**And** the user is notified of successful registration
**And** the user is directed to verify their email

### Scenario 2: Email Already Exists

**Given** the registration page is open
**When** a user attempts to register with an email that already exists
**Then** an error message is displayed
**And** the user is offered the option to log in instead

### Scenario 3: Invalid Password

**Given** the registration page is open
**When** a user enters a password that does not meet requirements
**Then** validation feedback is shown immediately
**And** requirements are clearly displayed:

- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character
  **And** the register button remains disabled until requirements are met

### Scenario 4: Email Verification

**Given** the user has registered successfully
**When** the user clicks the verification link in their email
**Then** their email address is marked as verified
**And** their account is activated
**And** they are redirected to complete their profile or set up their organisation

## Dependencies

- PostgreSQL database configured
- Email service configured (Mailpit for dev, SMTP for staging/prod)
- Authentication framework (django-allauth)
- Password validation utilities
- STORY-015: Organisation Creation and Setup

## Implementation Progress

### Phase 1: Core Models and Database ✅ Completed (07/01/2026)

**Backend Tasks Completed:**

- [x] Create User model extending AbstractBaseUser with 2FA support field
- [x] Create UserProfile model for extended user information
- [x] Create Organisation model for multi-tenancy
- [x] Create BaseToken abstract model for DRY token management
- [x] Create SessionToken model for JWT session management
- [x] Create EmailVerificationToken model
- [x] Create PasswordResetToken model
- [x] Create TOTPDevice model with Fernet encryption for 2FA secrets
- [x] Create PasswordHistory model for password reuse prevention
- [x] Create AuditLog model for security tracking
- [x] Implement password validators (MinimumLength, Complexity, BreachedPassword, PasswordHistory)
- [x] Add comprehensive unit tests for all models (85+ tests created)
- [x] Create TDD test suite with factory-boy factories
- [x] Create BDD feature tests with Gherkin syntax
- [x] Add database indexes for query optimisation
- [x] Security review completed with recommendations documented

**Documentation Completed:**

- [x] QA Report with 18 critical issues identified (Phase 1 marked as complete)
- [x] Backend Architecture Review (Rating: 8.7/10 Excellent)
- [x] Security Implementation Report
- [x] Database Schema Review
- [x] GDPR Compliance Analysis
- [x] Manual Testing Guide for Phase 1
- [x] Test Specification Document

### Phase 2: Authentication Service Layer ✅ Completed (08/01/2026)

**Backend Tasks Completed:**

- [x] Create AuthService for business logic with race condition prevention
- [x] Create TokenService for JWT and refresh token management
- [x] Create EmailService for verification and password reset emails
- [x] Create PasswordResetService with hash-then-store pattern
- [x] Create AuditService with encrypted IP logging
- [x] Create IPEncryption utility with key rotation support
- [x] Create TokenHasher utility with HMAC-SHA256 hashing
- [x] Create management command for IP key rotation
- [x] Implement user registration logic with duplicate email prevention
- [x] Implement login logic (without 2FA) with email verification check
- [x] Implement password reset logic with hashed tokens
- [x] Implement email verification logic
- [x] Implement refresh token replay detection
- [x] Implement timezone-aware datetime handling
- [x] Add comprehensive unit tests (~95% coverage for services)

**Documentation Completed:**

- [x] Phase 2 Implementation Report
- [x] Logging and Audit Implementation Report
- [x] Security Implementation Review
- [x] QA Report updated for Phase 2

### Phase 3: GraphQL API ✅ Completed (09/01/2026)

**Backend Tasks Completed:**

- [x] Set up Strawberry GraphQL schema
- [x] Create registration GraphQL mutation
- [x] Create login GraphQL mutation
- [x] Create email verification GraphQL mutation
- [x] Create password reset request GraphQL mutation
- [x] Create password reset confirmation GraphQL mutation
- [x] Create 2FA enrollment GraphQL mutations
- [x] Implement CSRF protection for GraphQL
- [x] Implement rate limiting on authentication endpoints
- [x] Implement account lockout mechanism
- [x] Implement concurrent session limit enforcement
- [x] Add integration tests for authentication flows
- [x] Add E2E tests for complete user journeys

### Phase 4: Security Hardening ✅ Completed (15/01/2026)

**Security Gap Remediation Tasks Completed:**

- [x] **C001**: Implemented password breach detection (HaveIBeenPwned API integration with k-anonymity)
- [x] **H004**: Added common password blacklist (block "Password123!" patterns, top 10,000 common passwords)
- [x] **M001**: Implemented CAPTCHA for bot protection (reCAPTCHA v3 for registration and login)
- [x] **M007**: Reviewed password reset token expiry (confirmed 15 minutes appropriate)
- [x] Added password complexity scoring beyond minimum requirements
- [x] Implemented progressive password strength feedback
- [x] Added unit tests for HIBP integration
- [x] Added integration tests for CAPTCHA flow

### Phase 5: Two-Factor Authentication ✅ Completed (16/01/2026)

**2FA Implementation Completed:**

- [x] TOTP-based two-factor authentication
- [x] QR code generation for 2FA setup
- [x] Backup codes for account recovery
- [x] 2FA enforcement policies
- [x] Time-based one-time password validation
- [x] Device management and trust settings
- [x] Comprehensive 2FA test coverage

### Phase 6: Password Reset and Email Verification ✅ Completed (17/01/2026)

**Email Workflow Tasks Completed:**

- [x] Email Verification Service with token hashing
- [x] Password Reset Service with hash-then-store pattern
- [x] Celery async email tasks with retry logic
- [x] Password history enforcement (last 5 passwords)
- [x] Single-use token enforcement
- [x] Resend cooldown mechanism
- [x] Email templates for verification, password reset, and 2FA
- [x] 32+ unit tests for email workflows

### Phase 7: Audit Logging and Advanced Security ✅ Completed (17/01/2026)

**Advanced Security Features Completed:**

- [x] Rate limiting middleware with headers
- [x] Audit log admin interface with retention policies
- [x] Concurrent session management service
- [x] Failed login tracking with progressive lockout
- [x] Suspicious activity detection and alerts
- [x] GraphQL audit log queries and session mutations
- [x] IP encryption key rotation
- [x] Security headers middleware
- [x] CORS configuration
- [x] Sentry error tracking integration

### Frontend Web Tasks

- [ ] Create registration form component with validation
- [ ] Implement email verification page
- [ ] Connect to GraphQL registration mutation
- [ ] Create error handling and user feedback UI
- [ ] Add password strength indicator

### Frontend Mobile Tasks

- [ ] Create registration form for mobile app
- [ ] Implement email verification flow for mobile
- [ ] Connect to GraphQL registration mutation

### Shared UI Tasks

- [ ] Create FormInput component with validation
- [ ] Create Button component for form submission
- [ ] Create ValidationError component
- [ ] Create PasswordStrengthIndicator component

## Repository Completion Status

**Story ID:** US-001
**Last Updated:** 19/01/2026 Europe/London

| Repository      | Required | Status         | Completed By  | Date       | Notes                                 |
| --------------- | -------- | -------------- | ------------- | ---------- | ------------------------------------- |
| Backend         | ✅       | ✅ Complete    | Backend Agent | 17/01/2026 | All phases 1-7 complete (100%)        |
| Frontend Web    | ✅       | ⬜ Not Started | -             | -          | Ready to begin - GraphQL API complete |
| Frontend Mobile | ✅       | ⬜ Not Started | -             | -          | Ready to begin - GraphQL API complete |
| Shared UI       | ✅       | ⬜ Not Started | -             | -          | Components to be designed             |

### Completion Notes

#### Backend (✅ All Phases Complete)

**Phase 1 - Core Models and Database:**

- **Completed:** 07/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** QA Agent, Backend Specialist
- **Notes:**
  - All 11 Django models implemented and tested (85+ unit tests)
  - Password validators with HaveIBeenPwned integration
  - Comprehensive security review completed (Rating: 8.7/10)
  - TDD test suite with factory-boy and BDD Gherkin features
  - Database schema optimised with indexes
  - GDPR compliance analysis complete

**Phase 2 - Authentication Service Layer:**

- **Completed:** 08/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** Security Specialist, Backend Agent
- **Notes:**
  - 5 service classes implemented (Auth, Token, Email, PasswordReset, Audit)
  - 2 utility modules (IPEncryption, TokenHasher)
  - 1 management command (rotate_ip_keys)
  - HMAC-SHA256 token hashing with secret key
  - Fernet IP encryption with key rotation
  - Race condition prevention with SELECT FOR UPDATE
  - Refresh token replay detection implemented
  - Timezone-aware datetime handling throughout
  - ~95% test coverage for service layer
  - Hash-then-store pattern for all authentication tokens

**Phase 3 - GraphQL API:**

- **Completed:** 09/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** API Specialist, Security Review
- **Notes:**
  - Complete Strawberry GraphQL schema
  - All authentication mutations (register, login, verify, reset)
  - CSRF protection for mutations
  - Rate limiting on endpoints
  - Integration and E2E tests passing

**Phase 4 - Security Hardening:**

- **Completed:** 15/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** Security Specialist
- **Notes:**
  - HaveIBeenPwned password breach checking
  - Common password blacklist
  - reCAPTCHA v3 integration
  - Account lockout mechanism
  - Comprehensive security test coverage

**Phase 5 - Two-Factor Authentication:**

- **Completed:** 16/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** Security Review, QA Agent
- **Notes:**
  - TOTP-based 2FA with QR codes
  - Backup codes for recovery
  - Device management
  - 2FA enforcement policies
  - Complete test coverage

**Phase 6 - Password Reset and Email Verification:**

- **Completed:** 17/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** Backend Agent, QA Review
- **Notes:**
  - Email verification with token hashing
  - Password reset with hash-then-store
  - Celery async email tasks
  - Password history enforcement
  - 32+ unit tests for workflows

**Phase 7 - Audit Logging and Advanced Security:**

- **Completed:** 17/01/2026
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** Security Specialist, DevOps
- **Notes:**
  - Rate limiting middleware
  - Audit log admin interface
  - Session management service
  - Failed login tracking
  - Suspicious activity detection
  - IP encryption key rotation
  - Sentry integration

#### Frontend Web

- **Status:** Not Started
- **Blocked By:** None - Backend complete, ready to begin
- **Notes:** Registration form components can now be implemented with complete GraphQL API

#### Frontend Mobile

- **Status:** Not Started
- **Blocked By:** None - Backend complete, ready to begin
- **Notes:** Mobile registration flow can use complete GraphQL API

#### Shared UI

- **Status:** Not Started
- **Blocked By:** Design token system (US-005)
- **Notes:** Form components, validation, and password strength indicators pending design system

## Story Points (Fibonacci)

**Original Estimate:** 5
**Actual Effort (Backend Complete):** 10 (All 7 phases complete)
**Remaining Estimate:** 11 (Frontend implementations: Web, Mobile, Shared UI)
**Total Revised Estimate:** 21

**Complexity factors:**

- Multiple validation layers (email, password, format)
- Email service integration required
- Token-based verification workflow
- Error handling for edge cases
- User experience feedback mechanisms
- Multi-platform implementation
- Comprehensive security requirements (2FA, encryption, audit logging)
- TDD approach with 85+ unit tests required more time than estimated

---

## Related Stories

- US-002: User Login with 2FA (Depends on US-001 Phase 1 ✅)
- US-003: Password Reset and Recovery (Depends on US-001 Phase 1 ✅)
- US-004: Organisation Creation and Setup (Depends on US-001 Phase 2)
