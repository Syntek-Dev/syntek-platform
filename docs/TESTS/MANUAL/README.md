# Manual Testing Guides

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team / QA
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

This directory contains manual testing guides and procedures for user stories and features. Manual testing is performed by QA team members to verify functionality that automated tests may not catch, such as:

- **User workflows**: Complete end-to-end user journeys
- **Edge cases**: Boundary conditions and unusual scenarios
- **Visual/UI testing**: Appearance and layout verification
- **Performance**: Response times and load handling
- **Accessibility**: Keyboard navigation and screen reader compatibility
- **Cross-browser**: Testing on different browsers and devices
- **Error handling**: Graceful degradation and error messages

---

## Table of Contents

- [Manual Testing Guides](#manual-testing-guides)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Manual Test Guides](#manual-test-guides)
    - [MANUAL-US-001-PHASE-1.md](#manual-us-001-phase-1md)
  - [What's in Manual Test Guides](#whats-in-manual-test-guides)
    - [Test Setup](#test-setup)
    - [Test Case Format](#test-case-format)
    - [Test Data](#test-data)
    - [Environment URLs](#environment-urls)
  - [How to Use Manual Tests](#how-to-use-manual-tests)
    - [Before Testing](#before-testing)
    - [During Testing](#during-testing)
    - [After Each Test](#after-each-test)
    - [Test Result Format](#test-result-format)
  - [Recording Test Results](#recording-test-results)
    - [Test Result Document](#test-result-document)
    - [Test Execution Checklist](#test-execution-checklist)
  - [Running Manual Tests](#running-manual-tests)
    - [Test Execution Process](#test-execution-process)
    - [Cross-Browser Testing](#cross-browser-testing)
  - [Related Documentation](#related-documentation)

---

## Directory Structure

```
MANUAL/
├── README.md                              # This file
└── MANUAL-US-001-PHASE-1.md               # Manual testing guide for US-001 Phase 1
```

---

## Manual Test Guides

### MANUAL-US-001-PHASE-1.md

**Purpose**: Manual testing procedures for User Story 001, Phase 1 (User Authentication)

**Contents**:

- **Testing overview**: What this phase covers
- **Test environment setup**: Prerequisites and configuration
- **User workflows**: Step-by-step procedures for testing:
  - User registration
  - Email verification
  - Login/logout
  - Two-factor authentication (2FA)
  - Password reset
  - Profile management
- **Edge cases**: Unusual scenarios to test
  - Invalid inputs
  - Concurrent operations
  - Network failures
  - Token expiration
- **Performance tests**: Response time checks
- **Security tests**: Penetration and security checks
- **Expected results**: What should happen in each scenario
- **Pass/fail criteria**: How to determine if tests passed

---

## What's in Manual Test Guides

### Test Setup

Prerequisites before running tests:

- **Environment**: Dev/staging/production URL
- **Account**: Test user accounts with various permissions
- **Browser**: Which browsers to test on
- **Network**: VPN or special access required
- **Data**: Sample data to prepare

### Test Case Format

Each test case includes:

1. **Test ID**: Unique identifier (e.g., `MT-US-001-001`)
2. **Title**: Short description of test
3. **Preconditions**: What must be true before test
4. **Steps**: Numbered steps to execute
5. **Expected Result**: What should happen
6. **Pass Criteria**: How to verify success
7. **Notes**: Additional context or warnings

Example:

```markdown
### Test Case: User Registration Success

**Test ID**: MT-US-001-001
**Title**: User can successfully register with valid data
**Preconditions**: New browser session, registration page loaded

**Steps**:

1. Navigate to `/register/`
2. Fill in "Email" field with "newuser@example.com"
3. Fill in "Password" field with "ValidPass123!"
4. Fill in "Confirm Password" field with "ValidPass123!"
5. Click "Sign Up" button

**Expected Result**:

- Form submits without errors
- User is redirected to email verification page
- Message displays "Verification email sent to newuser@example.com"

**Pass Criteria**:

- [ ] Redirect happens within 2 seconds
- [ ] Verification email appears in mailbox
- [ ] Email contains valid verification link

**Severity**: High (Core feature)
**Notes**: Test with different email providers (Gmail, Outlook, etc.)
```

### Test Data

Common test data sets:

| Data Type | Valid Example       | Invalid Example | Notes                      |
| --------- | ------------------- | --------------- | -------------------------- |
| Email     | <valid@example.com> | <invalid@.com>  | Test multiple domains      |
| Password  | ValidPass123!       | weak            | Test strength requirements |
| Phone     | +44 7911 123456     | invalid         | Test multiple formats      |

### Environment URLs

| Environment | URL                           | Username    | Notes             |
| ----------- | ----------------------------- | ----------- | ----------------- |
| Development | <http://localhost:8000>       | devuser     | Local development |
| Staging     | <https://staging.example.com> | staginguser | Pre-production    |

---

## How to Use Manual Tests

### Before Testing

1. **Review the guide** for your assigned user story
2. **Prepare the environment**: Set up browsers, accounts, test data
3. **Read all test cases**: Understand what you'll be testing
4. **Check prerequisites**: Ensure system is in correct state

### During Testing

1. **Follow steps exactly** as written in test case
2. **Note any issues**: Document unexpected behaviour
3. **Take screenshots**: Capture errors and important states
4. **Record timing**: Note response times for performance tests
5. **Test on multiple browsers**: If applicable
6. **Test different user roles**: Admin, manager, user, guest

### After Each Test

1. **Record result**: Pass or fail
2. **Document issues**: If failed, note exactly what happened
3. **Provide evidence**: Screenshots, logs, timestamps
4. **Clean up**: Remove test data if needed

### Test Result Format

```markdown
## Test Results: US-001 Phase 1

**Date**: 08/01/2026
**Tester**: QA Team Member Name
**Environment**: Staging
**Browser**: Chrome 120.0

### Summary

- Total Tests: 42
- Passed: 40
- Failed: 2
- Blocked: 0

### Failed Tests

#### Test MT-US-001-015: 2FA Setup with Backup Codes

**Status**: FAILED
**Severity**: High
**Steps to Reproduce**:

1. Navigate to `/settings/security/`
2. Click "Enable 2FA"
3. Scan QR code with authenticator app
4. Generate backup codes
5. Click "Save and Continue"

**Expected Result**: Backup codes should be displayed for download
**Actual Result**: Page shows "Error generating backup codes"
**Evidence**: [Screenshot attached]
**Assigned To**: Developer Name
```

---

## Recording Test Results

### Test Result Document

Create a test result summary document:

1. **File name**: `RESULTS/MANUAL-RESULTS-[DATE].md`
2. **Content**:
   - Date and tester name
   - Environment tested
   - Summary (total, passed, failed)
   - Detailed failure information
   - Blockers and issues
   - Recommendations

### Test Execution Checklist

Use this checklist when testing:

```markdown
## Manual Testing Checklist: US-001

- [ ] Environment is properly set up
- [ ] Test accounts are active
- [ ] Test data is prepared
- [ ] Browser is compatible
- [ ] Network connectivity verified
- [ ] All test cases reviewed
- [ ] Screenshots configured
- [ ] Bug tracking system ready
- [ ] Test results document prepared
- [ ] Testers are trained on procedures
```

---

## Running Manual Tests

### Test Execution Process

```bash
# 1. Prepare environment
./scripts/env/dev.sh start
./scripts/env/dev.sh migrate

# 2. Create test accounts
./scripts/env/dev.sh shell
# Create users in shell

# 3. Run tests
# Follow procedures in MANUAL-US-001-PHASE-1.md

# 4. Document results
# Update docs/TESTS/RESULTS/MANUAL-RESULTS-[DATE].md
```

### Cross-Browser Testing

Test on multiple browsers:

| Browser | Version | OS      | Status  |
| ------- | ------- | ------- | ------- |
| Chrome  | Latest  | Windows | Tested  |
| Firefox | Latest  | macOS   | Pending |
| Safari  | Latest  | iOS     | Pending |
| Edge    | Latest  | Windows | Tested  |

---

## Related Documentation

- [Testing Overview](../README.md) - Testing strategy and approach
- [Test Results](../RESULTS/) - Automated test results and metrics
- [QA Reports](../../QA/) - Quality assurance findings
- [User Stories](../../STORIES/) - Feature requirements
- [API Documentation](../../../api/README.md) - API specifications

---

**Project:** Backend Template
**Framework:** Django 5.2
**Testing Approach**: Manual + Automated (pytest)
**Last Updated:** 08/01/2026
