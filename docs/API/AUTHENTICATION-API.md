# Authentication API Documentation

**Last Updated**: 17/01/2026
**Version**: 1.0.0
**API Type**: GraphQL
**Audience**: Developers

---

## Table of Contents

- [Authentication API Documentation](#authentication-api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Base URL](#base-url)
  - [Authentication](#authentication)
  - [Error Handling](#error-handling)
    - [Error Codes](#error-codes)
    - [Error Response Format](#error-response-format)
  - [Rate Limiting](#rate-limiting)
  - [GraphQL Types](#graphql-types)
    - [User Type](#user-type)
    - [Organisation Type](#organisation-type)
    - [Session Type](#session-type)
    - [TOTP Device Type](#totp-device-type)
  - [Mutations](#mutations)
    - [Register](#register)
    - [Verify Email](#verify-email)
    - [Login](#login)
    - [Verify Login 2FA](#verify-login-2fa)
    - [Logout](#logout)
    - [Logout All Devices](#logout-all-devices)
    - [Request Password Reset](#request-password-reset)
    - [Reset Password](#reset-password)
    - [Change Password](#change-password)
    - [Enable 2FA](#enable-2fa)
    - [Verify 2FA](#verify-2fa)
    - [Disable 2FA](#disable-2fa)
    - [Regenerate Backup Codes](#regenerate-backup-codes)
  - [Queries](#queries)
    - [Me](#me)
    - [Active Sessions](#active-sessions)
  - [Security Features](#security-features)
    - [Password Requirements](#password-requirements)
    - [Session Management](#session-management)
    - [Two-Factor Authentication](#two-factor-authentication)
    - [CSRF Protection](#csrf-protection)
  - [Implementation Examples](#implementation-examples)
    - [JavaScript/TypeScript (React)](#javascripttypescript-react)
    - [Python](#python)
    - [curl](#curl)
  - [Testing](#testing)
  - [Changelog](#changelog)

---

## Overview

This document describes the GraphQL API for authentication, including user registration, login, two-factor authentication, password management, and session handling.

**Key Features:**

- User registration with email verification
- Email/password authentication
- Two-factor authentication (TOTP)
- Password reset functionality
- Session token management
- Multi-device session support
- Comprehensive audit logging

---

## Base URL

```
Development: http://localhost:8000/graphql/
Staging: https://staging-api.yourplatform.com/graphql/
Production: https://api.yourplatform.com/graphql/
```

---

## Authentication

All authenticated requests must include a Bearer token in the `Authorization` header:

```http
Authorization: Bearer <session_token>
```

**Example:**

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Error Handling

### Error Codes

| Error Code | Description           | Action Required          |
| ---------- | --------------------- | ------------------------ |
| `AUTH001`  | Invalid credentials   | Check email/password     |
| `AUTH002`  | Email not verified    | Verify email address     |
| `AUTH003`  | Account locked        | Wait or reset password   |
| `AUTH004`  | Session expired       | Re-authenticate          |
| `AUTH005`  | Invalid token         | Re-authenticate          |
| `AUTH006`  | 2FA required          | Provide TOTP code        |
| `AUTH007`  | Invalid 2FA code      | Check authenticator app  |
| `AUTH008`  | 2FA challenge expired | Login again              |
| `AUTH009`  | Password too weak     | Use stronger password    |
| `AUTH010`  | Password breached     | Use different password   |
| `AUTH011`  | Email already in use  | Use different email      |
| `AUTH012`  | Invalid email format  | Correct email format     |
| `AUTH013`  | Token expired         | Request new token        |
| `AUTH014`  | Token already used    | Request new token        |
| `RATE001`  | Rate limit exceeded   | Wait before retrying     |
| `CSRF001`  | CSRF token invalid    | Include valid CSRF token |
| `VAL001`   | Validation error      | Check input fields       |
| `SRV001`   | Internal server error | Contact support          |

### Error Response Format

```json
{
  "errors": [
    {
      "message": "Invalid credentials provided",
      "extensions": {
        "code": "AUTH001",
        "field": "password",
        "timestamp": "2026-01-17T12:00:00Z"
      }
    }
  ],
  "data": null
}
```

---

## Rate Limiting

Rate limits apply to all authentication endpoints to prevent abuse.

**Limits:**

| Endpoint Type          | Limit                  | Window |
| ---------------------- | ---------------------- | ------ |
| Login                  | 5 attempts per IP      | 15 min |
| Password Reset Request | 3 attempts per IP      | 60 min |
| Email Verification     | 10 attempts per IP     | 60 min |
| 2FA Verification       | 5 attempts per session | 15 min |
| Registration           | 3 attempts per IP      | 60 min |

**Rate Limit Headers:**

```http
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1705492800
```

**Rate Limit Exceeded Response:**

```json
{
  "errors": [
    {
      "message": "Rate limit exceeded. Please try again in 10 minutes.",
      "extensions": {
        "code": "RATE001",
        "retryAfter": 600,
        "limit": 5,
        "window": 900
      }
    }
  ]
}
```

---

## GraphQL Types

### User Type

```graphql
type User {
  id: ID!
  email: String!
  firstName: String!
  lastName: String!
  emailVerified: Boolean!
  hasTwoFactor: Boolean!
  organisation: Organisation
  profile: UserProfile
  createdAt: DateTime!
  lastLogin: DateTime
}
```

### Organisation Type

```graphql
type Organisation {
  id: ID!
  name: String!
  slug: String!
  createdAt: DateTime!
}
```

### Session Type

```graphql
type Session {
  id: ID!
  userAgent: String!
  lastActivity: DateTime!
  createdAt: DateTime!
  isCurrent: Boolean!
}
```

### TOTP Device Type

```graphql
type TOTPDevice {
  id: ID!
  confirmed: Boolean!
  createdAt: DateTime!
}
```

---

## Mutations

### Register

Create a new user account.

**Input:**

```graphql
input RegisterInput {
  email: String!
  password: String!
  firstName: String!
  lastName: String!
  organisationSlug: String!
}
```

**Mutation:**

```graphql
mutation Register($input: RegisterInput!) {
  register(input: $input) {
    user {
      id
      email
      firstName
      lastName
      emailVerified
    }
  }
}
```

**Variables:**

```json
{
  "input": {
    "email": "user@example.com",
    "password": "SecureP@ss123!",
    "firstName": "John",
    "lastName": "Doe",
    "organisationSlug": "acme-corp"
  }
}
```

**Response:**

```json
{
  "data": {
    "register": {
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "firstName": "John",
        "lastName": "Doe",
        "emailVerified": false
      }
    }
  }
}
```

**Notes:**

- Email verification is required before login
- Verification email is sent automatically
- Password must meet security requirements
- Rate limited to 3 attempts per hour per IP

---

### Verify Email

Verify user email address with token.

**Mutation:**

```graphql
mutation VerifyEmail($token: String!) {
  verifyEmail(token: $token) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "token": "abc123def456ghi789jkl012mno345pqr678"
}
```

**Response:**

```json
{
  "data": {
    "verifyEmail": {
      "success": true,
      "message": "Email verified successfully"
    }
  }
}
```

**Error Cases:**

- `AUTH013`: Token expired (24 hours)
- `AUTH014`: Token already used
- `AUTH005`: Invalid token

---

### Login

Authenticate user with email and password.

**Input:**

```graphql
input LoginInput {
  email: String!
  password: String!
}
```

**Mutation:**

```graphql
mutation Login($input: LoginInput!) {
  login(input: $input) {
    token
    requiresTwoFactor
    user {
      id
      email
      hasTwoFactor
    }
  }
}
```

**Variables:**

```json
{
  "input": {
    "email": "user@example.com",
    "password": "SecureP@ss123!"
  }
}
```

**Response (Without 2FA):**

```json
{
  "data": {
    "login": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "requiresTwoFactor": false,
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "hasTwoFactor": false
      }
    }
  }
}
```

**Response (With 2FA):**

```json
{
  "data": {
    "login": {
      "token": null,
      "requiresTwoFactor": true,
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "hasTwoFactor": true
      }
    }
  }
}
```

**Error Cases:**

- `AUTH001`: Invalid credentials
- `AUTH002`: Email not verified
- `AUTH003`: Account locked
- `RATE001`: Too many failed attempts

---

### Verify Login 2FA

Complete login with TOTP or backup code.

**Mutation:**

```graphql
mutation VerifyLogin2FA($code: String!) {
  verifyLogin2FA(code: $code) {
    token
    user {
      id
      email
    }
  }
}
```

**Variables (TOTP Code):**

```json
{
  "code": "123456"
}
```

**Variables (Backup Code):**

```json
{
  "code": "BACKUP-0001"
}
```

**Response:**

```json
{
  "data": {
    "verifyLogin2FA": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "user": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com"
      }
    }
  }
}
```

**Error Cases:**

- `AUTH007`: Invalid 2FA code
- `AUTH008`: 2FA challenge expired (10 minutes)
- `RATE001`: Too many failed attempts

---

### Logout

End current session.

**Mutation:**

```graphql
mutation Logout {
  logout {
    success
  }
}
```

**Response:**

```json
{
  "data": {
    "logout": {
      "success": true
    }
  }
}
```

**Headers:**

```http
Authorization: Bearer <token>
```

---

### Logout All Devices

End all sessions except current.

**Mutation:**

```graphql
mutation LogoutAllDevices {
  logoutAllDevices {
    success
    devicesLoggedOut
  }
}
```

**Response:**

```json
{
  "data": {
    "logoutAllDevices": {
      "success": true,
      "devicesLoggedOut": 4
    }
  }
}
```

---

### Request Password Reset

Request password reset email.

**Mutation:**

```graphql
mutation RequestPasswordReset($email: String!) {
  requestPasswordReset(email: $email) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "email": "user@example.com"
}
```

**Response:**

```json
{
  "data": {
    "requestPasswordReset": {
      "success": true,
      "message": "If an account exists with this email, a password reset link has been sent."
    }
  }
}
```

**Notes:**

- Same response for existing/non-existing emails (prevents enumeration)
- Reset link expires in 1 hour
- Rate limited to 3 attempts per hour per IP

---

### Reset Password

Reset password using token.

**Input:**

```graphql
input ResetPasswordInput {
  token: String!
  newPassword: String!
}
```

**Mutation:**

```graphql
mutation ResetPassword($input: ResetPasswordInput!) {
  resetPassword(input: $input) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "input": {
    "token": "abc123def456ghi789jkl012mno345pqr678",
    "newPassword": "NewSecureP@ss123!"
  }
}
```

**Response:**

```json
{
  "data": {
    "resetPassword": {
      "success": true,
      "message": "Password reset successfully"
    }
  }
}
```

**Error Cases:**

- `AUTH013`: Token expired
- `AUTH014`: Token already used
- `AUTH009`: Password too weak
- `AUTH010`: Password breached

---

### Change Password

Change password for authenticated user.

**Input:**

```graphql
input ChangePasswordInput {
  currentPassword: String!
  newPassword: String!
  totpCode: String # Required if 2FA enabled
}
```

**Mutation:**

```graphql
mutation ChangePassword($input: ChangePasswordInput!) {
  changePassword(input: $input) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "input": {
    "currentPassword": "OldSecureP@ss123!",
    "newPassword": "NewSecureP@ss123!",
    "totpCode": "123456"
  }
}
```

**Response:**

```json
{
  "data": {
    "changePassword": {
      "success": true,
      "message": "Password changed successfully. All other sessions have been logged out."
    }
  }
}
```

**Notes:**

- All other sessions are invalidated for security
- Current session remains active
- Requires 2FA code if 2FA is enabled

---

### Enable 2FA

Enable two-factor authentication.

**Mutation:**

```graphql
mutation Enable2FA {
  enable2FA {
    secret
    qrCodeUrl
    backupCodes
  }
}
```

**Response:**

```json
{
  "data": {
    "enable2FA": {
      "secret": "JBSWY3DPEHPK3PXP",
      "qrCodeUrl": "otpauth://totp/Platform:user@example.com?secret=JBSWY3DPEHPK3PXP&issuer=Platform",
      "backupCodes": [
        "BACKUP-0001",
        "BACKUP-0002",
        "BACKUP-0003",
        "BACKUP-0004",
        "BACKUP-0005",
        "BACKUP-0006",
        "BACKUP-0007",
        "BACKUP-0008",
        "BACKUP-0009",
        "BACKUP-0010"
      ]
    }
  }
}
```

**Notes:**

- Must verify with TOTP code to confirm
- Save backup codes securely
- QR code can be scanned with authenticator app

---

### Verify 2FA

Confirm 2FA setup with TOTP code.

**Mutation:**

```graphql
mutation Verify2FA($code: String!) {
  verify2FA(code: $code) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "code": "123456"
}
```

**Response:**

```json
{
  "data": {
    "verify2FA": {
      "success": true,
      "message": "Two-factor authentication enabled successfully"
    }
  }
}
```

---

### Disable 2FA

Disable two-factor authentication.

**Mutation:**

```graphql
mutation Disable2FA($code: String!) {
  disable2FA(code: $code) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "code": "123456"
}
```

**Response:**

```json
{
  "data": {
    "disable2FA": {
      "success": true,
      "message": "Two-factor authentication disabled"
    }
  }
}
```

**Notes:**

- Requires TOTP code or backup code
- All sessions are invalidated
- Security alert email sent

---

### Regenerate Backup Codes

Generate new backup codes.

**Mutation:**

```graphql
mutation RegenerateBackupCodes($code: String!) {
  regenerateBackupCodes(code: $code) {
    backupCodes
  }
}
```

**Variables:**

```json
{
  "code": "123456"
}
```

**Response:**

```json
{
  "data": {
    "regenerateBackupCodes": {
      "backupCodes": [
        "BACKUP-NEW1",
        "BACKUP-NEW2",
        "BACKUP-NEW3",
        "BACKUP-NEW4",
        "BACKUP-NEW5",
        "BACKUP-NEW6",
        "BACKUP-NEW7",
        "BACKUP-NEW8",
        "BACKUP-NEW9",
        "BACKUP-NEW10"
      ]
    }
  }
}
```

---

## Queries

### Me

Get current authenticated user.

**Query:**

```graphql
query Me {
  me {
    id
    email
    firstName
    lastName
    emailVerified
    hasTwoFactor
    organisation {
      id
      name
      slug
    }
    profile {
      bio
      avatarUrl
    }
  }
}
```

**Response:**

```json
{
  "data": {
    "me": {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "firstName": "John",
      "lastName": "Doe",
      "emailVerified": true,
      "hasTwoFactor": true,
      "organisation": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Acme Corp",
        "slug": "acme-corp"
      },
      "profile": {
        "bio": "Software developer",
        "avatarUrl": "https://cdn.example.com/avatars/user.jpg"
      }
    }
  }
}
```

---

### Active Sessions

Get all active sessions for current user.

**Query:**

```graphql
query ActiveSessions {
  activeSessions {
    id
    userAgent
    lastActivity
    createdAt
    isCurrent
  }
}
```

**Response:**

```json
{
  "data": {
    "activeSessions": [
      {
        "id": "770e8400-e29b-41d4-a716-446655440002",
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
        "lastActivity": "2026-01-17T12:00:00Z",
        "createdAt": "2026-01-17T10:00:00Z",
        "isCurrent": true
      },
      {
        "id": "880e8400-e29b-41d4-a716-446655440003",
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/604.1",
        "lastActivity": "2026-01-16T18:30:00Z",
        "createdAt": "2026-01-16T08:00:00Z",
        "isCurrent": false
      }
    ]
  }
}
```

---

## Security Features

### Password Requirements

All passwords must meet:

- Minimum 12 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character
- Not in HaveIBeenPwned breach database

### Session Management

- JWT-based session tokens
- 24-hour expiry
- Maximum 5 concurrent sessions per user
- Automatic cleanup of expired sessions
- Token revocation on password change

### Two-Factor Authentication

- TOTP-based (RFC 6238)
- 30-second time window
- ±1 window tolerance for clock drift
- Encrypted TOTP secrets (Fernet)
- 10 one-time backup codes
- Rate limiting on verification attempts

### CSRF Protection

- Double-submit cookie pattern
- Required for all mutations
- X-CSRF-Token header validation
- SameSite cookie attribute

---

## Implementation Examples

### JavaScript/TypeScript (React)

```typescript
import { ApolloClient, InMemoryCache, createHttpLink, gql } from '@apollo/client'
import { setContext } from '@apollo/client/link/context'

// Apollo Client setup
const httpLink = createHttpLink({
  uri: 'http://localhost:8000/graphql/',
  credentials: 'include', // Include cookies for CSRF
})

const authLink = setContext((_, { headers }) => {
  const token = localStorage.getItem('authToken')
  return {
    headers: {
      ...headers,
      authorization: token ? `Bearer ${token}` : '',
    },
  }
})

const client = new ApolloClient({
  link: authLink.concat(httpLink),
  cache: new InMemoryCache(),
})

// Login mutation
const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      token
      requiresTwoFactor
      user {
        id
        email
        hasTwoFactor
      }
    }
  }
`

// Login function
async function login(email: string, password: string) {
  try {
    const { data } = await client.mutate({
      mutation: LOGIN_MUTATION,
      variables: {
        input: { email, password },
      },
    })

    if (data.login.requiresTwoFactor) {
      // Redirect to 2FA page
      return { requires2FA: true }
    }

    // Store token
    localStorage.setItem('authToken', data.login.token)
    return { success: true, user: data.login.user }
  } catch (error) {
    console.error('Login failed:', error)
    return { success: false, error }
  }
}
```

### Python

```python
import requests

GRAPHQL_URL = "http://localhost:8000/graphql/"

def login(email: str, password: str) -> dict:
    """Login user and return session token."""
    query = """
    mutation Login($input: LoginInput!) {
      login(input: $input) {
        token
        requiresTwoFactor
        user {
          id
          email
        }
      }
    }
    """

    variables = {
        "input": {
            "email": email,
            "password": password
        }
    }

    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables}
    )

    data = response.json()

    if "errors" in data:
        raise Exception(f"Login failed: {data['errors']}")

    return data["data"]["login"]

# Usage
result = login("user@example.com", "SecureP@ss123!")
if result["requiresTwoFactor"]:
    print("2FA required")
else:
    token = result["token"]
    print(f"Login successful, token: {token}")
```

### curl

```bash
# Login
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Login($input: LoginInput!) { login(input: $input) { token user { email } } }",
    "variables": {
      "input": {
        "email": "user@example.com",
        "password": "SecureP@ss123!"
      }
    }
  }'

# Get current user (authenticated)
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "query": "query Me { me { id email firstName lastName } }"
  }'
```

---

## Testing

**Postman Collection:**

Import the Postman collection from `/docs/API/postman/authentication-api.json`

**GraphQL Playground:**

Access GraphQL playground at: `http://localhost:8000/graphql/`

**Test User Accounts:**

```
Email: test@example.com
Password: TestPassword123!@
2FA: Disabled

Email: test-2fa@example.com
Password: TestPassword123!@
2FA: Enabled (secret: JBSWY3DPEHPK3PXP)
```

---

## Changelog

**Version 1.0.0 (2026-01-17)**

- Initial API documentation
- All authentication endpoints documented
- Rate limiting details added
- Error codes defined
- Implementation examples provided

---

**Document Version**: 1.0.0  
**Last Updated**: 17/01/2026  
**API Support**: api-support@yourplatform.com
