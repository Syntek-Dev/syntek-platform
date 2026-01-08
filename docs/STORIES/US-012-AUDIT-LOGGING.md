# User Story: Comprehensive Audit Logging System

<!-- CLICKUP_ID: 86c7d2q72 -->

## Overview

Security administrators need detailed audit logging to track all user actions and system changes for security, compliance, and debugging purposes. This story covers action logging, user tracking, IP address encryption, GraphQL query logging, change history, audit log viewing, searching, filtering, and export capabilities.

---

## Story

**As a** security administrator
**I want** to track all user actions and system changes with detailed audit logs
**So that** I can maintain security, compliance, and debug issues

## MoSCoW Priority

- **Must Have:** Action logging (CRUD operations), user tracking, timestamp, IP address encryption, GraphQL query logging
- **Should Have:** Change history (old/new values), user agent tracking, export capability, filtering and search
- **Could Have:** Real-time alerting for suspicious activity, automated compliance reports
- **Won't Have:** Advanced ML-based anomaly detection in Phase 1

**Sprint:** Sprint 23

## Repository Coverage

| Repository      | Required | Notes                                                |
| --------------- | -------- | ---------------------------------------------------- |
| Backend         | ✅       | Audit logging middleware, IP encryption, GraphQL API |
| Frontend Web    | ✅       | Audit log viewer interface                           |
| Frontend Mobile | ❌       | Audit logs are for admins only                       |
| Shared UI       | ✅       | Log viewer, filter components                        |

## Acceptance Criteria

### Scenario 1: Log Authentication Events

**Given** a user logs in or fails to log in
**When** the authentication event occurs
**Then** the following is logged:

- User ID (or email if login fails)
- Action (login, login_failed, logout)
- IP address (encrypted)
- User agent
- Timestamp
- Success/failure status

### Scenario 2: Log CRUD Operations

**Given** content is created, read, updated, or deleted
**When** the operation completes
**Then** the following is logged:

- User ID
- Action (create, update, delete)
- Resource type (Page, Media, etc.)
- Resource ID
- Old values (for updates)
- New values (for updates)
- IP address (encrypted)
- Timestamp

### Scenario 3: View Audit Logs

**Given** a user with admin role is viewing the audit log page
**When** they access the logs
**Then** they see:

- List of all logged actions (paginated)
- Each log entry shows: user, action, resource, timestamp
- Full details expandable
- Filters available for user, action, resource type, date range

### Scenario 4: Search Audit Logs

**Given** the audit log interface is open
**When** an admin searches or filters
**Then** they can filter by:

- User
- Action (login, create, update, delete)
- Resource type (Page, Media, User, etc.)
- Date range
- IP address (with decryption permission)
  **And** results update in real-time

### Scenario 5: View Change History

**Given** a resource has been updated multiple times
**When** an admin views the audit logs for that resource
**Then** they can see:

- All versions of the resource
- Who made the change and when
- What changed (old value → new value)
- Side-by-side comparison view

### Scenario 6: Export Audit Logs

**Given** audit logs exist
**When** an admin requests export
**Then** they can export as:

- CSV file
- JSON file
  **And** filters are applied to the export
  **And** IP addresses are encrypted in exports
  **And** only users with security role can decrypt IPs

### Scenario 7: IP Address Encryption

**Given** an audit log contains an IP address
**When** the IP is stored
**Then** it is encrypted using Fernet encryption
**And** only users with security role can decrypt and view IPs
**And** IP viewing is logged as a security event

### Scenario 8: GraphQL Query Logging

**Given** a GraphQL query is executed
**When** the query completes
**Then** the following is logged:

- User ID
- Query (first 500 chars)
- Response size
- Execution time
- Any errors
- IP address (encrypted)

## Dependencies

- AuditLog model defined
- IP encryption library (Fernet)
- GraphQL API with logging middleware
- User authentication system

## Tasks

### Backend Tasks

- [ ] Create AuditLog model with all required fields
- [ ] Implement IP encryption/decryption service
- [ ] Create audit logging middleware for Django
- [ ] Implement GraphQL query logging middleware
- [ ] Create signal handlers for model CRUD events
- [ ] Implement auto-logging of model changes
- [ ] Create GraphQL queries for audit log retrieval
- [ ] Create search/filtering logic for audit logs
- [ ] Implement pagination for large audit datasets
- [ ] Create export service (CSV, JSON)
- [ ] Add permission checks (security role for IP decryption)
- [ ] Create audit log cleanup/archival strategy
- [ ] Add indexing on frequently queried fields
- [ ] Create audit log monitoring/alerting triggers
- [ ] Add unit tests for logging functionality
- [ ] Add integration tests for audit trails

### Frontend Web Tasks

- [ ] Create AuditLog page/dashboard
- [ ] Create AuditLogTable component
- [ ] Create AuditLogDetail component for expanded view
- [ ] Create AuditLogFilter component
- [ ] Create DateRangeFilter component
- [ ] Create UserSelectFilter component
- [ ] Create ActionSelectFilter component
- [ ] Create ResourceTypeFilter component
- [ ] Create ChangeComparison view (old vs new)
- [ ] Create export button (CSV, JSON)
- [ ] Add pagination controls
- [ ] Implement real-time log updates (via subscriptions)
- [ ] Add search input field
- [ ] Create IP address visibility toggle (with confirmation)

### Shared UI Tasks

- [ ] Create Table component for log display
- [ ] Create FilterPanel component
- [ ] Create DateRangeSelector component
- [ ] Create SelectFilter component
- [ ] Create ExpandableRow component
- [ ] Create ExportButton component
- [ ] Create ConfirmationDialog for sensitive operations

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- Encryption/decryption implementation
- Comprehensive logging across all operations
- Large dataset pagination and performance
- Export functionality to multiple formats
- GraphQL middleware integration
- Permission-based field visibility
- Change history tracking and comparison
- Cleanup and archival strategy

---

## Related Stories

- US-002: User Login with 2FA (login logging)
- US-004: Organisation Creation (org operation logging)
- US-011: GraphQL API (GraphQL query logging)
- US-026: Rate Limiting and DDoS Protection
