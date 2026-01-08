# Security Policy

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

This security policy outlines how to responsibly report vulnerabilities, which versions are currently supported with security updates, and the security features implemented in this project. Please read this entire policy before reporting any security issues. All vulnerabilities should be reported privately through GitHub Security Advisories rather than public GitHub issues.

---

## Table of Contents

- [Security Policy](#security-policy)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Supported Versions](#supported-versions)
  - [Reporting a Vulnerability](#reporting-a-vulnerability)
    - [How to Report](#how-to-report)
    - [What to Include](#what-to-include)
    - [Response Timeline](#response-timeline)
    - [After Reporting](#after-reporting)
  - [Security Features](#security-features)
  - [Security Updates](#security-updates)
  - [Scope](#scope)

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| < 0.2.0 | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue, please report it responsibly.

### How to Report

**Please DO NOT create a public GitHub issue for security vulnerabilities.**

Instead, report vulnerabilities through one of these channels:

1. **GitHub Security Advisories** (Preferred)
   - Go to the [Security tab](../../security/advisories) of this repository
   - Click "Report a vulnerability"
   - Provide detailed information about the vulnerability

2. **Private Disclosure**
   - If you cannot use GitHub Security Advisories, contact the maintainers directly
   - Include "SECURITY" in the subject line

### What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce the issue
- Affected versions
- Potential impact
- Any suggested fixes (if available)

### Response Timeline

- **Acknowledgement**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Resolution Target**: Within 30 days (depending on severity)

### After Reporting

1. We will acknowledge your report within 48 hours
2. We will investigate and validate the vulnerability
3. We will work on a fix and coordinate disclosure timing with you
4. Once fixed, we will publicly acknowledge your contribution (unless you prefer anonymity)

## Security Features

This project implements comprehensive security measures:

- **Authentication**: Session-based with CSRF protection
- **Password Security**: Strong complexity requirements, breach detection
- **Rate Limiting**: Protection against brute force attacks
- **HTTP Security Headers**: HSTS, CSP, X-Frame-Options, etc.
- **GraphQL Security**: Query depth/complexity limiting
- **Audit Logging**: Security event tracking

For detailed security documentation, see [docs/SECURITY/SECURITY.md](docs/SECURITY/SECURITY.md).

## Security Updates

Security updates are released as patch versions. We recommend:

- Enabling GitHub Dependabot alerts
- Subscribing to security advisories for this repository
- Keeping dependencies up to date

## Scope

This security policy covers:

- The backend template codebase
- Docker configurations
- CI/CD workflows
- Documentation

It does **not** cover:

- Third-party dependencies (report to their maintainers)
- Infrastructure you deploy to (your responsibility)
- Modifications you make to the template
