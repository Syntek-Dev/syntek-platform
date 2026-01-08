# User Story: User Authentication with Email and Password

<!-- CLICKUP_ID: 86c7d2kp1 -->

**Phase 1 Status:** ✅ Completed (07/01/2026)
**Overall Status:** 🔄 In Progress

## Overview

Core authentication system allowing new users to create accounts with email and password, including email verification, password validation, token management, and security features like encryption and audit logging. Phase 1 (models and database) is complete; remaining phases cover GraphQL API, email workflows, and frontend implementations across all platforms.

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

### Phase 2: GraphQL API and Services ⬜ Not Started

**Backend Tasks Pending:**

- [ ] Set up Strawberry GraphQL schema
- [ ] Create AuthenticationService for business logic
- [ ] Create registration GraphQL mutation
- [ ] Create login GraphQL mutation
- [ ] Create email verification GraphQL mutation
- [ ] Create password reset request GraphQL mutation
- [ ] Create password reset confirmation GraphQL mutation
- [ ] Create 2FA enrollment GraphQL mutations
- [ ] Implement CSRF protection for GraphQL
- [ ] Implement rate limiting on authentication endpoints
- [ ] Implement account lockout mechanism
- [ ] Implement concurrent session limit enforcement
- [ ] Add integration tests for authentication flows
- [ ] Add E2E tests for complete user journeys

### Phase 3: Email Service and Workflows ⬜ Not Started

**Backend Tasks Pending:**

- [ ] Configure email service (Mailpit for dev, SMTP for staging/prod)
- [ ] Create email templates for verification
- [ ] Create email templates for password reset
- [ ] Create email templates for 2FA setup
- [ ] Implement email sending service with retry logic
- [ ] Implement email verification workflow
- [ ] Implement password reset workflow
- [ ] Add email sending tests

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
**Last Updated:** 08/01/2026 09:30 Europe/London

| Repository      | Required | Status         | Completed By  | Date        | Notes                        |
| --------------- | -------- | -------------- | ------------- | ----------- | ---------------------------- |
| Backend         | ✅       | 🔄 In Progress | Backend Agent | Phase 1: ✅ | Models complete, API pending |
| Frontend Web    | ✅       | ⬜ Not Started | -             | -           | Waiting for GraphQL API      |
| Frontend Mobile | ✅       | ⬜ Not Started | -             | -           | Waiting for GraphQL API      |
| Shared UI       | ✅       | ⬜ Not Started | -             | -           | Components to be designed    |

### Completion Notes

#### Backend (Phase 1 Complete)

- **Completed:** 07/01/2026
- **Phase:** Phase 1 - Core Models and Database
- **PR/Commit:** Branch `us001/user-authentication`
- **Verified By:** QA Agent, Backend Specialist
- **Notes:**
  - All 11 Django models implemented and tested (85+ unit tests)
  - Password validators with HaveIBeenPwned integration
  - Comprehensive security review completed (Rating: 8.7/10)
  - TDD test suite with factory-boy and BDD Gherkin features
  - 18 critical issues identified for Phase 2 implementation
  - Database schema optimised with indexes
  - GDPR compliance analysis complete
  - **Next:** Phase 2 - GraphQL API and authentication services

#### Frontend Web

- **Status:** Not Started
- **Blocked By:** Backend Phase 2 (GraphQL API mutations)
- **Notes:** Registration form components depend on API availability

#### Frontend Mobile

- **Status:** Not Started
- **Blocked By:** Backend Phase 2 (GraphQL API mutations)
- **Notes:** Mobile registration flow requires API endpoints

#### Shared UI

- **Status:** Not Started
- **Blocked By:** Design token system (US-005)
- **Notes:** Form components, validation, and password strength indicators

## Story Points (Fibonacci)

**Original Estimate:** 5
**Actual Effort (Phase 1):** 8 (Models, validators, tests exceeded initial estimate)
**Remaining Estimate:** 13 (GraphQL API, email workflows, frontend implementations)
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
