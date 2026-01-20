# Security Incident Response Procedures

**Last Updated**: 17/01/2026
**Version**: 1.0.0
**Classification**: Internal Use Only
**Owner**: Security Team

---

## Table of Contents

- [Security Incident Response Procedures](#security-incident-response-procedures)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Incident Classification](#incident-classification)
    - [Severity Levels](#severity-levels)
    - [Incident Types](#incident-types)
  - [Response Team](#response-team)
  - [Incident Response Phases](#incident-response-phases)
    - [Phase 1: Detection and Identification](#phase-1-detection-and-identification)
    - [Phase 2: Containment](#phase-2-containment)
    - [Phase 3: Eradication](#phase-3-eradication)
    - [Phase 4: Recovery](#phase-4-recovery)
    - [Phase 5: Post-Incident Review](#phase-5-post-incident-review)
  - [Specific Incident Playbooks](#specific-incident-playbooks)
    - [Playbook: Credential Compromise](#playbook-credential-compromise)
    - [Playbook: Brute Force Attack](#playbook-brute-force-attack)
    - [Playbook: Session Hijacking](#playbook-session-hijacking)
    - [Playbook: Data Breach](#playbook-data-breach)
    - [Playbook: 2FA Bypass Attempt](#playbook-2fa-bypass-attempt)
  - [Communication Templates](#communication-templates)
  - [Tools and Commands](#tools-and-commands)
  - [Audit Log Analysis](#audit-log-analysis)
  - [Escalation Matrix](#escalation-matrix)
  - [Post-Incident Checklist](#post-incident-checklist)
  - [Document History](#document-history)

---

## Overview

This document outlines the procedures for responding to security incidents related to the
authentication system. It provides step-by-step guidance for identifying, containing,
eradicating, and recovering from security incidents.

**Scope:** All authentication-related security incidents including:

- Credential compromise
- Brute force attacks
- Session hijacking
- Unauthorised access
- Data breaches involving user credentials
- 2FA bypass attempts

---

## Incident Classification

### Severity Levels

| Level | Name     | Description                                  | Response Time        | Examples                                         |
| ----- | -------- | -------------------------------------------- | -------------------- | ------------------------------------------------ |
| P1    | Critical | Active breach with data exfiltration         | Immediate (< 15 min) | Mass credential theft, active attacker in system |
| P2    | High     | Confirmed compromise, no active exfiltration | < 1 hour             | Single account compromise, 2FA bypass            |
| P3    | Medium   | Suspicious activity requiring investigation  | < 4 hours            | Unusual login patterns, failed brute force       |
| P4    | Low      | Minor security event, no immediate risk      | < 24 hours           | Single failed login attempt, policy violation    |

### Incident Types

| Type    | Description         | Typical Severity |
| ------- | ------------------- | ---------------- |
| CRED-01 | Password compromise | P2-P1            |
| CRED-02 | API token exposure  | P2-P1            |
| AUTH-01 | Brute force attack  | P3-P2            |
| AUTH-02 | Session hijacking   | P2-P1            |
| AUTH-03 | 2FA bypass attempt  | P2               |
| DATA-01 | User data exposure  | P1               |
| DATA-02 | Audit log tampering | P1               |

---

## Response Team

| Role               | Responsibilities                        | Contact                   |
| ------------------ | --------------------------------------- | ------------------------- |
| Incident Commander | Overall coordination, decision making   | security-lead@company.com |
| Security Analyst   | Investigation, log analysis             | security-team@company.com |
| DevOps Engineer    | System access, containment actions      | devops@company.com        |
| Legal/Compliance   | Regulatory notification, legal guidance | legal@company.com         |
| Communications     | Internal/external communications        | comms@company.com         |

**On-Call Rotation:** Check PagerDuty or on-call schedule for current responders.

---

## Incident Response Phases

### Phase 1: Detection and Identification

**Objective:** Confirm the incident and assess initial scope.

**Steps:**

1. **Receive Alert**
   - Source: Sentry, audit logs, user report, automated monitoring
   - Document time of detection: `__________`
   - Document alert source: `__________`

2. **Initial Triage**

   ```bash
   # Check recent authentication failures
   ./scripts/env/dev.sh shell -c "
   from apps.core.models import AuditLog
   from django.utils import timezone
   from datetime import timedelta

   recent = AuditLog.objects.filter(
       created_at__gte=timezone.now() - timedelta(hours=1),
       action__in=['LOGIN_FAILED', 'ACCOUNT_LOCKED', 'SUSPICIOUS_ACTIVITY']
   ).count()
   print(f'Recent security events: {recent}')
   "
   ```

3. **Classify Severity**
   - Determine incident type from table above
   - Assign severity level (P1-P4)
   - Document classification rationale

4. **Notify Response Team**
   - P1: Immediate all-hands notification
   - P2: Security team + on-call DevOps
   - P3-P4: Security team during business hours

**Deliverable:** Incident ticket created with initial classification.

---

### Phase 2: Containment

**Objective:** Limit the impact and prevent further damage.

**Immediate Actions (P1/P2):**

1. **Revoke Compromised Sessions**

   ```bash
   # Revoke all sessions for a specific user
   ./scripts/env/production.sh shell -c "
   from apps.core.models import User, SessionToken
   from django.utils import timezone

   user = User.objects.get(email='compromised@example.com')
   SessionToken.objects.filter(user=user).update(
       is_revoked=True,
       revoked_at=timezone.now()
   )
   print(f'Revoked all sessions for {user.email}')
   "
   ```

2. **Force Password Reset**

   ```bash
   # Invalidate password and send reset email
   ./scripts/env/production.sh shell -c "
   from apps.core.models import User
   from apps.core.services.password_reset_service import PasswordResetService

   user = User.objects.get(email='compromised@example.com')
   user.set_unusable_password()
   user.save()
   PasswordResetService.request_reset(user.email)
   print(f'Password invalidated and reset email sent to {user.email}')
   "
   ```

3. **Lock Account (if necessary)**

   ```bash
   # Temporarily deactivate account
   ./scripts/env/production.sh shell -c "
   from apps.core.models import User

   user = User.objects.get(email='compromised@example.com')
   user.is_active = False
   user.save()
   print(f'Account {user.email} has been deactivated')
   "
   ```

4. **Block Attacking IP (if identified)**

   ```bash
   # Add IP to blocklist (via Redis)
   ./scripts/env/production.sh shell -c "
   from django.core.cache import cache

   attacker_ip = '192.168.1.100'
   cache.set(f'ip_blocked:{attacker_ip}', True, timeout=86400)  # 24 hours
   print(f'IP {attacker_ip} blocked for 24 hours')
   "
   ```

5. **Disable 2FA Device (if compromised)**

   ```bash
   # Remove compromised TOTP device
   ./scripts/env/production.sh shell -c "
   from apps.core.models import User, TOTPDevice

   user = User.objects.get(email='user@example.com')
   TOTPDevice.objects.filter(user=user).delete()
   print(f'All 2FA devices removed for {user.email}')
   "
   ```

**Deliverable:** Containment actions documented with timestamps.

---

### Phase 3: Eradication

**Objective:** Remove the threat and fix vulnerabilities.

**Steps:**

1. **Identify Root Cause**
   - Review audit logs for attack vector
   - Check for malware or backdoors
   - Identify vulnerable code or configuration

2. **Remove Threat**
   - Rotate compromised secrets
   - Patch vulnerable code
   - Remove malicious accounts

3. **Rotate Secrets (if necessary)**

   ```bash
   # Rotate JWT signing key
   ./scripts/env/production.sh manage rotate_jwt_key

   # Rotate IP encryption key
   ./scripts/env/production.sh manage rotate_ip_encryption_key --batch-size=1000

   # Rotate TOTP encryption key
   ./scripts/env/production.sh manage rotate_totp_key
   ```

4. **Update Security Controls**
   - Strengthen password requirements if needed
   - Add additional rate limiting
   - Enable additional logging

**Deliverable:** Root cause analysis document.

---

### Phase 4: Recovery

**Objective:** Restore normal operations safely.

**Steps:**

1. **Verify System Integrity**

   ```bash
   # Run security tests
   ./scripts/env/test.sh run tests/security/ -v

   # Check for anomalies in audit logs
   ./scripts/env/production.sh shell -c "
   from apps.core.models import AuditLog
   from django.utils import timezone
   from datetime import timedelta

   anomalies = AuditLog.objects.filter(
       created_at__gte=timezone.now() - timedelta(hours=24),
       action__in=['SUSPICIOUS_ACTIVITY', 'RATE_LIMIT_EXCEEDED']
   )
   for a in anomalies[:20]:
       print(f'{a.created_at}: {a.action} - {a.user}')
   "
   ```

2. **Restore Affected Accounts**

   ```bash
   # Reactivate account after verification
   ./scripts/env/production.sh shell -c "
   from apps.core.models import User

   user = User.objects.get(email='user@example.com')
   user.is_active = True
   user.save()
   print(f'Account {user.email} has been reactivated')
   "
   ```

3. **Notify Affected Users**
   - Send security notification email
   - Recommend password change
   - Recommend enabling 2FA

4. **Monitor for Recurrence**
   - Set up additional alerts
   - Increase logging verbosity temporarily
   - Schedule follow-up review

**Deliverable:** Recovery completion report.

---

### Phase 5: Post-Incident Review

**Objective:** Learn from the incident and improve defences.

**Timeline:** Within 5 business days of incident closure.

**Review Agenda:**

1. **Timeline Reconstruction**
   - When did the incident start?
   - When was it detected?
   - What was the detection method?
   - What was the total time to containment?

2. **Impact Assessment**
   - Number of affected users
   - Data exposed (if any)
   - Business impact
   - Regulatory implications

3. **Response Evaluation**
   - What worked well?
   - What could be improved?
   - Were procedures followed?
   - Were tools adequate?

4. **Action Items**
   - Security improvements needed
   - Process improvements needed
   - Training requirements
   - Documentation updates

**Deliverable:** Post-incident report with action items.

---

## Specific Incident Playbooks

### Playbook: Credential Compromise

**Indicators:**

- User reports unauthorised access
- Login from unusual location/device
- Multiple sessions from different locations
- Password change not initiated by user

**Response:**

1. Immediately revoke all user sessions
2. Force password reset
3. Review audit logs for last 30 days
4. Check for data access/changes
5. Enable 2FA if not already enabled
6. Notify user with security recommendations

```bash
# Quick response script
./scripts/env/production.sh shell -c "
from apps.core.models import User, SessionToken, AuditLog
from apps.core.services.password_reset_service import PasswordResetService
from django.utils import timezone
from datetime import timedelta

email = 'compromised@example.com'
user = User.objects.get(email=email)

# 1. Revoke sessions
revoked = SessionToken.objects.filter(user=user, is_revoked=False).update(
    is_revoked=True, revoked_at=timezone.now()
)
print(f'Revoked {revoked} sessions')

# 2. Force password reset
user.set_unusable_password()
user.save()
PasswordResetService.request_reset(email)
print('Password reset email sent')

# 3. Show recent activity
logs = AuditLog.objects.filter(
    user=user,
    created_at__gte=timezone.now() - timedelta(days=30)
).order_by('-created_at')[:20]
for log in logs:
    print(f'{log.created_at}: {log.action}')
"
```

---

### Playbook: Brute Force Attack

**Indicators:**

- High volume of failed login attempts
- Multiple accounts targeted
- Rate limit alerts triggered
- Account lockouts

**Response:**

1. Identify attacking IP addresses
2. Block attacking IPs at firewall/application level
3. Review rate limiting configuration
4. Check if any accounts were compromised
5. Consider enabling CAPTCHA

```bash
# Identify top attacking IPs
./scripts/env/production.sh shell -c "
from apps.core.models import AuditLog
from django.utils import timezone
from datetime import timedelta
from collections import Counter

logs = AuditLog.objects.filter(
    action='LOGIN_FAILED',
    created_at__gte=timezone.now() - timedelta(hours=1)
).values_list('ip_address', flat=True)

# Note: IPs are encrypted, need to group by encrypted value
ip_counts = Counter(logs)
for ip, count in ip_counts.most_common(10):
    print(f'{ip}: {count} attempts')
"
```

---

### Playbook: Session Hijacking

**Indicators:**

- Session used from different IP than original
- Session used with different user agent
- Concurrent activity from multiple locations
- User reports being logged out unexpectedly

**Response:**

1. Revoke suspected hijacked session
2. Revoke all user sessions as precaution
3. Investigate session token exposure
4. Check for XSS vulnerabilities
5. Force password reset
6. Review HTTPS/secure cookie configuration

---

### Playbook: Data Breach

**Indicators:**

- Unusual database queries
- Large data exports
- Access to admin functions
- Audit log gaps

**Response:**

1. **Immediate containment** - Isolate affected systems
2. **Preserve evidence** - Create forensic copies of logs
3. **Assess scope** - Determine what data was accessed
4. **Legal notification** - Engage legal team for GDPR/regulatory requirements
5. **User notification** - Prepare breach notification (within 72 hours for GDPR)
6. **Regulatory reporting** - File required reports (ICO for UK)

**GDPR Requirements:**

- Notify supervisory authority within 72 hours
- Document the breach in breach register
- Notify affected individuals if high risk
- Provide details of breach and mitigation steps

---

### Playbook: 2FA Bypass Attempt

**Indicators:**

- Multiple failed 2FA verification attempts
- Backup code usage from unknown device
- 2FA device added without user knowledge
- Session created without 2FA verification

**Response:**

1. Lock the account immediately
2. Revoke all sessions
3. Remove all 2FA devices
4. Contact user through verified channel
5. Investigate how bypass was attempted
6. Force complete re-enrollment

---

## Communication Templates

### Internal Escalation

```
Subject: [SECURITY INCIDENT] [P{LEVEL}] - {BRIEF DESCRIPTION}

Incident ID: {ID}
Severity: P{LEVEL}
Type: {INCIDENT TYPE}
Detected: {TIMESTAMP}
Status: {INVESTIGATING|CONTAINED|RESOLVED}

Summary:
{Brief description of incident}

Impact:
- Users affected: {NUMBER}
- Systems affected: {LIST}
- Data exposed: {YES/NO/UNKNOWN}

Current Actions:
- {ACTION 1}
- {ACTION 2}

Next Steps:
- {STEP 1}
- {STEP 2}

Response Team:
- Incident Commander: {NAME}
- Technical Lead: {NAME}
```

### User Notification

```
Subject: Important Security Notice for Your Account

Dear {USER_NAME},

We detected unusual activity on your account on {DATE}. As a precaution, we have:

- Logged you out of all devices
- Required a password reset

Please take the following actions:
1. Reset your password using the link below
2. Enable two-factor authentication if not already enabled
3. Review your recent account activity

If you did not attempt to access your account, please contact our support team.

[Reset Password Button]

Security Team
```

---

## Tools and Commands

### Quick Reference Commands

```bash
# View recent failed logins
./scripts/env/production.sh shell -c "
from apps.core.models import AuditLog
from django.utils import timezone
from datetime import timedelta

for log in AuditLog.objects.filter(
    action='LOGIN_FAILED',
    created_at__gte=timezone.now() - timedelta(hours=1)
).order_by('-created_at')[:50]:
    print(f'{log.created_at} | {log.details}')
"

# View locked accounts
./scripts/env/production.sh shell -c "
from apps.core.models import User
for user in User.objects.filter(is_active=False)[:20]:
    print(f'{user.email} | Joined: {user.date_joined}')
"

# View active sessions for a user
./scripts/env/production.sh shell -c "
from apps.core.models import User, SessionToken
user = User.objects.get(email='user@example.com')
for session in SessionToken.objects.filter(user=user, is_revoked=False):
    print(f'{session.created_at} | {session.device_fingerprint}')
"

# Check rate limit status
./scripts/env/production.sh shell -c "
from django.core.cache import cache
ip = '192.168.1.100'
key = f'ratelimit:login:{ip}'
attempts = cache.get(key, 0)
print(f'Login attempts from {ip}: {attempts}')
"
```

---

## Audit Log Analysis

### Key Audit Events

| Event                 | Description                    | Severity Indicator |
| --------------------- | ------------------------------ | ------------------ |
| `LOGIN_FAILED`        | Failed login attempt           | High if > 5/hour   |
| `ACCOUNT_LOCKED`      | Account locked due to failures | Always investigate |
| `SUSPICIOUS_ACTIVITY` | Unusual login location         | Always investigate |
| `PASSWORD_CHANGED`    | Password was changed           | Verify with user   |
| `TWO_FACTOR_DISABLED` | 2FA was disabled               | Verify with user   |
| `SESSION_REVOKED`     | Session was manually revoked   | Normal operation   |
| `RATE_LIMIT_EXCEEDED` | Too many requests              | Possible attack    |

### Analysis Queries

```python
# Find users with suspicious activity
from apps.core.models import AuditLog, User
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

suspicious_users = AuditLog.objects.filter(
    action__in=['LOGIN_FAILED', 'SUSPICIOUS_ACTIVITY', 'ACCOUNT_LOCKED'],
    created_at__gte=timezone.now() - timedelta(days=7)
).values('user').annotate(
    count=Count('id')
).filter(count__gte=10).order_by('-count')

for entry in suspicious_users:
    user = User.objects.get(id=entry['user'])
    print(f"{user.email}: {entry['count']} events")
```

---

## Escalation Matrix

| Severity | Initial Response  | Escalate To   | Notify                 |
| -------- | ----------------- | ------------- | ---------------------- |
| P1       | Security Lead     | CTO, CEO      | Legal, All Engineering |
| P2       | Security Team     | Security Lead | Engineering Lead       |
| P3       | On-call Engineer  | Security Team | None initially         |
| P4       | Next business day | None          | None                   |

**Escalation Triggers:**

- No response within SLA time
- Scope expanding beyond initial assessment
- Data breach confirmed
- Regulatory implications identified
- Media attention anticipated

---

## Post-Incident Checklist

- [ ] Incident ticket created and documented
- [ ] Timeline of events recorded
- [ ] All containment actions logged with timestamps
- [ ] Root cause identified and documented
- [ ] Affected users identified and notified
- [ ] Systems restored to normal operation
- [ ] Security controls verified
- [ ] Post-incident review scheduled
- [ ] Action items assigned with owners
- [ ] Documentation updated
- [ ] Lessons learned shared with team
- [ ] Regulatory notifications completed (if required)

---

## Document History

| Version | Date       | Author        | Changes         |
| ------- | ---------- | ------------- | --------------- |
| 1.0.0   | 17/01/2026 | Security Team | Initial version |

---

**Document Owner:** Security Team
**Review Frequency:** Quarterly
**Next Review:** April 2026
