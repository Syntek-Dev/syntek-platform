# Security Guide - Syntek CMS Platform

## Overview

Comprehensive security guide for the Syntek CMS platform featuring multi-layered security architecture with Rust security layer, Django backend protection, and frontend security measures.

## Security Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Frontend Security                      │
│  • XSS Prevention  • CSRF Protection  • Input Validation │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTPS/WSS
┌─────────────────────▼───────────────────────────────────┐
│                 Rust Security Layer                     │
│  • JWT Validation  • Rate Limiting  • Authorization    │
└─────────────────────┬───────────────────────────────────┘
                      │ Internal API
┌─────────────────────▼───────────────────────────────────┐
│              Django Backend Security                    │
│  • GraphQL Security  • Database Security  • CORS       │
└─────────────────────┬───────────────────────────────────┘
                      │ Encrypted Connection
┌─────────────────────▼───────────────────────────────────┐
│              Database & Infrastructure                  │
│  • PostgreSQL Security  • Redis Security  • Encryption │
└─────────────────────────────────────────────────────────┘
```

## Authentication & Authorization

### Multi-Factor Authentication (MFA)

#### JWT Token Flow
```rust
// security/src/auth/jwt.rs
use jsonwebtoken::{encode, decode, Header, Algorithm, Validation, EncodingKey, DecodingKey};

#[derive(Debug, Serialize, Deserialize)]
pub struct Claims {
    pub sub: String,          // User ID
    pub email: String,        // User email
    pub roles: Vec<String>,   // User roles
    pub permissions: Vec<String>, // Specific permissions
    pub org_id: String,       // Organization ID
    pub mfa_verified: bool,   // MFA completion status
    pub exp: i64,             // Expiration timestamp
    pub iat: i64,             // Issued at timestamp
    pub jti: String,          // Unique token ID
}

pub fn generate_token(user: &User, mfa_verified: bool) -> Result<String, AuthError> {
    let claims = Claims {
        sub: user.id.to_string(),
        email: user.email.clone(),
        roles: user.roles.clone(),
        permissions: get_user_permissions(&user),
        org_id: user.organization_id.to_string(),
        mfa_verified,
        exp: chrono::Utc::now().timestamp() + TOKEN_EXPIRY_SECONDS,
        iat: chrono::Utc::now().timestamp(),
        jti: uuid::Uuid::new_v4().to_string(),
    };

    encode(&Header::default(), &claims, &EncodingKey::from_secret(JWT_SECRET.as_ref()))
        .map_err(|e| AuthError::TokenGeneration(e.to_string()))
}
```

#### Role-Based Access Control (RBAC)
```rust
// security/src/auth/rbac.rs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Role {
    SuperAdmin,      // Full system access
    OrgAdmin,        // Organization administration
    Developer,       // Code editing and deployment
    Designer,        // Design and layout management
    ContentEditor,   // Content creation and editing
    Viewer,          // Read-only access
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Permission {
    // Page Management
    PageCreate,
    PageEdit,
    PageDelete,
    PagePublish,

    // Template Management
    TemplateCreate,
    TemplateEdit,
    TemplateDelete,

    // User Management
    UserInvite,
    UserEdit,
    UserDelete,

    // Organization Management
    OrgSettings,
    OrgBilling,
    OrgDelete,

    // Development Access
    CodeEdit,
    TerminalAccess,
    DatabaseAccess,
    DeploymentAccess,
}

pub fn get_role_permissions(role: &Role) -> Vec<Permission> {
    match role {
        Role::SuperAdmin => vec![/* All permissions */],
        Role::OrgAdmin => vec![
            Permission::PageCreate,
            Permission::PageEdit,
            Permission::PageDelete,
            Permission::UserInvite,
            Permission::UserEdit,
            Permission::OrgSettings,
            // ... other admin permissions
        ],
        Role::Developer => vec![
            Permission::PageCreate,
            Permission::PageEdit,
            Permission::CodeEdit,
            Permission::TerminalAccess,
            Permission::DatabaseAccess,
            // ... developer permissions
        ],
        Role::ContentEditor => vec![
            Permission::PageCreate,
            Permission::PageEdit,
            Permission::PagePublish,
            // ... content permissions only
        ],
        Role::Viewer => vec![
            // Read-only permissions only
        ],
    }
}
```

### Authentication Implementation

#### Login Flow
```typescript
// frontend/auth/login.ts
interface LoginRequest {
  email: string;
  password: string;
  mfaToken?: string;
}

interface LoginResponse {
  requiresMfa: boolean;
  token?: string;
  mfaQrCode?: string;
  user?: User;
}

export async function loginUser(credentials: LoginRequest): Promise<LoginResponse> {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    throw new Error('Authentication failed');
  }

  return response.json();
}

export async function setupMfa(): Promise<{ qrCode: string; secret: string }> {
  const response = await fetch('/api/auth/mfa/setup', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${getToken()}` },
  });

  return response.json();
}

export async function verifyMfa(token: string): Promise<{ verified: boolean }> {
  const response = await fetch('/api/auth/mfa/verify', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getToken()}`,
    },
    body: JSON.stringify({ token }),
  });

  return response.json();
}
```

## GraphQL Security

### Query Depth Limiting
```python
# backend/apps/api/security.py
from strawberry.extensions import QueryDepthLimiter, ValidationCache
from strawberry import Schema

def create_secure_schema():
    return Schema(
        query=Query,
        mutation=Mutation,
        subscription=Subscription,
        extensions=[
            QueryDepthLimiter(max_depth=15),  # Prevent deeply nested queries
            ValidationCache(maxsize=100),     # Cache query validations
        ]
    )
```

### Rate Limiting
```rust
// security/src/middleware/rate_limit.rs
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use tokio::time::{Duration, Instant};

pub struct RateLimiter {
    requests: Arc<Mutex<HashMap<String, Vec<Instant>>>>,
    max_requests: usize,
    window: Duration,
}

impl RateLimiter {
    pub fn new(max_requests: usize, window_seconds: u64) -> Self {
        Self {
            requests: Arc::new(Mutex::new(HashMap::new())),
            max_requests,
            window: Duration::from_secs(window_seconds),
        }
    }

    pub fn check_rate_limit(&self, user_id: &str) -> bool {
        let mut requests = self.requests.lock().unwrap();
        let now = Instant::now();

        let user_requests = requests.entry(user_id.to_string()).or_insert_with(Vec::new);

        // Remove old requests outside the time window
        user_requests.retain(|&request_time| now.duration_since(request_time) < self.window);

        if user_requests.len() >= self.max_requests {
            false // Rate limit exceeded
        } else {
            user_requests.push(now);
            true
        }
    }
}

// Rate limiting by role
pub fn get_rate_limits(role: &Role) -> (usize, u64) {
    match role {
        Role::SuperAdmin => (1000, 60),    // 1000 requests per minute
        Role::OrgAdmin => (500, 60),       // 500 requests per minute
        Role::Developer => (300, 60),      // 300 requests per minute
        Role::ContentEditor => (200, 60),  // 200 requests per minute
        Role::Viewer => (100, 60),         // 100 requests per minute
    }
}
```

### Input Validation & Sanitization
```python
# backend/apps/api/validators.py
import bleach
from typing import Any, Dict
from strawberry import Field
import strawberry

ALLOWED_HTML_TAGS = [
    'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'blockquote', 'a', 'img'
]

ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
}

def sanitize_html(content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks"""
    return bleach.clean(
        content,
        tags=ALLOWED_HTML_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )

@strawberry.input
class CreatePageInput:
    title: str = Field(description="Page title")
    content: Dict[str, Any] = Field(description="Page content blocks")
    template_id: strawberry.ID = Field(description="Template ID")

    def validate(self) -> Dict[str, str]:
        errors = {}

        # Validate title
        if not self.title or len(self.title.strip()) == 0:
            errors['title'] = "Title is required"
        elif len(self.title) > 255:
            errors['title'] = "Title must be less than 255 characters"

        # Validate content structure
        if not isinstance(self.content, dict):
            errors['content'] = "Content must be a valid object"
        elif 'blocks' not in self.content:
            errors['content'] = "Content must contain blocks array"

        # Sanitize HTML in content blocks
        if 'blocks' in self.content:
            for i, block in enumerate(self.content['blocks']):
                if 'content' in block and isinstance(block['content'], str):
                    self.content['blocks'][i]['content'] = sanitize_html(block['content'])

        return errors
```

## Data Protection & Privacy

### GDPR Compliance
```python
# backend/apps/users/models.py
from django.db import models
from django.utils import timezone

class User(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    # GDPR fields
    gdpr_consent = models.BooleanField(default=False)
    gdpr_consent_date = models.DateTimeField(null=True, blank=True)
    data_retention_date = models.DateTimeField(null=True, blank=True)
    deletion_requested = models.BooleanField(default=False)
    deletion_requested_date = models.DateTimeField(null=True, blank=True)

    def request_deletion(self):
        """Handle GDPR right to be forgotten"""
        self.deletion_requested = True
        self.deletion_requested_date = timezone.now()
        self.save()

    def export_personal_data(self) -> Dict[str, Any]:
        """Export all personal data for GDPR compliance"""
        return {
            'personal_info': {
                'email': self.email,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'created_at': self.created_at.isoformat(),
            },
            'pages': [page.to_dict() for page in self.pages.all()],
            'audit_logs': [log.to_dict() for log in self.audit_logs.all()],
        }

class AuditLog(models.Model):
    """Audit trail for GDPR compliance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=50)
    resource_id = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
```

### Data Encryption
```rust
// security/src/encryption/mod.rs
use aes_gcm::{Aes256Gcm, Key, Nonce, aead::{Aead, NewAead}};
use rand::{thread_rng, RngCore};

pub struct DataEncryption {
    cipher: Aes256Gcm,
}

impl DataEncryption {
    pub fn new(key: &[u8; 32]) -> Self {
        let key = Key::from_slice(key);
        let cipher = Aes256Gcm::new(key);
        Self { cipher }
    }

    pub fn encrypt(&self, plaintext: &[u8]) -> Result<Vec<u8>, EncryptionError> {
        let mut nonce_bytes = [0u8; 12];
        thread_rng().fill_bytes(&mut nonce_bytes);
        let nonce = Nonce::from_slice(&nonce_bytes);

        let ciphertext = self.cipher
            .encrypt(nonce, plaintext)
            .map_err(|e| EncryptionError::EncryptionFailed(e.to_string()))?;

        // Prepend nonce to ciphertext
        let mut result = nonce_bytes.to_vec();
        result.extend_from_slice(&ciphertext);
        Ok(result)
    }

    pub fn decrypt(&self, ciphertext: &[u8]) -> Result<Vec<u8>, EncryptionError> {
        if ciphertext.len() < 12 {
            return Err(EncryptionError::InvalidCiphertext);
        }

        let (nonce_bytes, encrypted) = ciphertext.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);

        self.cipher
            .decrypt(nonce, encrypted)
            .map_err(|e| EncryptionError::DecryptionFailed(e.to_string()))
    }
}

// Encrypt sensitive database fields
#[derive(Debug)]
pub struct EncryptedField {
    pub encrypted_value: Vec<u8>,
}

impl EncryptedField {
    pub fn new(plaintext: &str, encryption: &DataEncryption) -> Result<Self, EncryptionError> {
        let encrypted_value = encryption.encrypt(plaintext.as_bytes())?;
        Ok(Self { encrypted_value })
    }

    pub fn decrypt(&self, encryption: &DataEncryption) -> Result<String, EncryptionError> {
        let decrypted = encryption.decrypt(&self.encrypted_value)?;
        String::from_utf8(decrypted).map_err(|e| EncryptionError::InvalidUtf8(e.to_string()))
    }
}
```

## Frontend Security

### XSS Prevention
```typescript
// frontend/utils/security.ts
import DOMPurify from 'dompurify';

/**
 * Sanitize HTML content to prevent XSS attacks
 */
export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'blockquote', 'a', 'img'
    ],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'width', 'height'],
    ALLOW_DATA_ATTR: false,
  });
}

/**
 * Escape HTML entities
 */
export function escapeHtml(unsafe: string): string {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Validate and sanitize URLs
 */
export function sanitizeUrl(url: string): string {
  const allowedProtocols = ['http:', 'https:', 'mailto:'];

  try {
    const parsed = new URL(url);
    if (allowedProtocols.includes(parsed.protocol)) {
      return url;
    }
  } catch {
    // Invalid URL
  }

  return '#'; // Return safe fallback
}
```

### CSRF Protection
```typescript
// frontend/utils/csrf.ts
/**
 * Get CSRF token from meta tag or cookie
 */
export function getCsrfToken(): string {
  // Try to get from meta tag first
  const metaTag = document.querySelector('meta[name="csrf-token"]');
  if (metaTag) {
    return metaTag.getAttribute('content') || '';
  }

  // Fallback to cookie
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return decodeURIComponent(value);
    }
  }

  return '';
}

/**
 * Enhanced fetch with CSRF protection
 */
export async function secureFetch(url: string, options: RequestInit = {}): Promise<Response> {
  const csrfToken = getCsrfToken();

  const secureOptions: RequestInit = {
    ...options,
    headers: {
      ...options.headers,
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
  };

  return fetch(url, secureOptions);
}
```

### Content Security Policy (CSP)
```typescript
// frontend/next.config.js
const ContentSecurityPolicy = `
  default-src 'self';
  script-src 'self' 'unsafe-eval' 'unsafe-inline' *.googleapis.com *.gstatic.com;
  style-src 'self' 'unsafe-inline' *.googleapis.com;
  img-src 'self' data: blob: *.amazonaws.com;
  font-src 'self' *.gstatic.com *.googleapis.com;
  connect-src 'self' wss: *.syntek-cms.com;
  frame-src 'none';
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
  upgrade-insecure-requests;
`;

const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: ContentSecurityPolicy.replace(/\s{2,}/g, ' ').trim()
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-DNS-Prefetch-Control',
    value: 'false'
  },
  {
    key: 'Strict-Transport-Security',
    value: 'max-age=31536000; includeSubDomains'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()'
  }
];

module.exports = {
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: securityHeaders,
      },
    ];
  },
};
```

## Database Security

### PostgreSQL Security Configuration
```sql
-- Create database roles with minimal privileges
CREATE ROLE syntek_app_user LOGIN PASSWORD 'strong_password_here';
CREATE ROLE syntek_readonly LOGIN PASSWORD 'readonly_password_here';

-- Grant only necessary privileges
GRANT CONNECT ON DATABASE syntek_cms TO syntek_app_user;
GRANT USAGE ON SCHEMA public TO syntek_app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO syntek_app_user;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO syntek_app_user;

-- Read-only access for reporting
GRANT CONNECT ON DATABASE syntek_cms TO syntek_readonly;
GRANT USAGE ON SCHEMA public TO syntek_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO syntek_readonly;

-- Enable row-level security
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policies for multi-tenant isolation
CREATE POLICY pages_isolation_policy ON pages
  USING (organization_id = current_setting('app.current_organization_id')::uuid);

CREATE POLICY templates_isolation_policy ON templates
  USING (organization_id = current_setting('app.current_organization_id')::uuid);

-- Audit logging
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  table_name VARCHAR(255) NOT NULL,
  operation VARCHAR(10) NOT NULL,
  old_values JSONB,
  new_values JSONB,
  user_id UUID,
  organization_id UUID,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_func()
  RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO audit_logs (table_name, operation, old_values, user_id, organization_id)
    VALUES (TG_TABLE_NAME, TG_OP, to_jsonb(OLD),
            current_setting('app.current_user_id', true)::uuid,
            current_setting('app.current_organization_id', true)::uuid);
    RETURN OLD;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO audit_logs (table_name, operation, old_values, new_values, user_id, organization_id)
    VALUES (TG_TABLE_NAME, TG_OP, to_jsonb(OLD), to_jsonb(NEW),
            current_setting('app.current_user_id', true)::uuid,
            current_setting('app.current_organization_id', true)::uuid);
    RETURN NEW;
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO audit_logs (table_name, operation, new_values, user_id, organization_id)
    VALUES (TG_TABLE_NAME, TG_OP, to_jsonb(NEW),
            current_setting('app.current_user_id', true)::uuid,
            current_setting('app.current_organization_id', true)::uuid);
    RETURN NEW;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

## Security Monitoring & Incident Response

### Security Event Logging
```rust
// security/src/monitoring/events.rs
use serde::{Deserialize, Serialize};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize)]
pub enum SecurityEvent {
    LoginAttempt {
        user_id: Option<String>,
        email: String,
        success: bool,
        ip_address: String,
        user_agent: String,
    },
    MfaVerification {
        user_id: String,
        success: bool,
        ip_address: String,
    },
    UnauthorizedAccess {
        user_id: Option<String>,
        resource: String,
        required_permission: String,
        ip_address: String,
    },
    SuspiciousActivity {
        user_id: Option<String>,
        activity_type: String,
        description: String,
        risk_level: RiskLevel,
        ip_address: String,
    },
    RateLimitExceeded {
        user_id: Option<String>,
        endpoint: String,
        ip_address: String,
        request_count: usize,
    },
}

#[derive(Debug, Serialize, Deserialize)]
pub enum RiskLevel {
    Low,
    Medium,
    High,
    Critical,
}

pub async fn log_security_event(event: SecurityEvent) {
    let event_id = Uuid::new_v4();
    let timestamp = chrono::Utc::now();

    // Log to structured logging system
    log::warn!(
        event_id = %event_id,
        timestamp = %timestamp,
        event = ?event,
        "Security event logged"
    );

    // Send to monitoring system (Grafana/Prometheus)
    match &event {
        SecurityEvent::LoginAttempt { success: false, .. } => {
            metrics::counter!("security.failed_logins").increment(1);
        }
        SecurityEvent::UnauthorizedAccess { .. } => {
            metrics::counter!("security.unauthorized_access").increment(1);
        }
        SecurityEvent::SuspiciousActivity { risk_level: RiskLevel::High, .. } => {
            metrics::counter!("security.high_risk_events").increment(1);
            // Trigger immediate alert
            send_security_alert(&event).await;
        }
        _ => {}
    }
}
```

### Vulnerability Scanning
```bash
# Backend security scanning
cd backend
safety check                    # Python dependency vulnerabilities
bandit -r apps/                 # Python code security issues
semgrep --config=auto apps/     # OWASP security patterns

# Frontend security scanning
cd frontend
npm audit                       # Node.js dependency vulnerabilities
eslint . --ext .ts,.tsx --config .eslintrc-security.js

# Security layer scanning
cd security
cargo audit                     # Rust dependency vulnerabilities
cargo clippy -- -D warnings    # Rust code quality and security
```

## Security Best Practices

### Development Guidelines

1. **Never Store Secrets in Code**
   - Use environment variables for all secrets
   - Use proper secret management (HashiCorp Vault)
   - Rotate secrets regularly

2. **Input Validation**
   - Validate all user inputs on both frontend and backend
   - Use parameterized queries to prevent SQL injection
   - Sanitize HTML content to prevent XSS

3. **Authentication & Authorization**
   - Implement proper MFA for all admin accounts
   - Use strong password requirements
   - Implement proper session management
   - Use principle of least privilege

4. **Data Protection**
   - Encrypt sensitive data at rest and in transit
   - Implement proper backup encryption
   - Follow GDPR compliance requirements
   - Use secure communication protocols (HTTPS/WSS)

### Production Security Checklist

- [ ] SSL/TLS certificates properly configured
- [ ] Security headers implemented (CSP, HSTS, etc.)
- [ ] Rate limiting configured appropriately
- [ ] Audit logging enabled for all sensitive operations
- [ ] Database access properly restricted
- [ ] Secrets properly managed and rotated
- [ ] Security monitoring and alerting configured
- [ ] Regular security updates applied
- [ ] Penetration testing completed
- [ ] Incident response plan documented

## Security Testing

### Automated Security Tests
```python
# backend/apps/security/tests/test_authentication.py
class SecurityTestCase(TestCase):
    def test_password_brute_force_protection(self):
        """Test that multiple failed login attempts trigger lockout"""
        user = User.objects.create_user(email='test@example.com', password='testpass')

        # Attempt multiple failed logins
        for _ in range(5):
            response = self.client.post('/auth/login', {
                'email': 'test@example.com',
                'password': 'wrongpass'
            })

        # Next attempt should be locked out
        response = self.client.post('/auth/login', {
            'email': 'test@example.com',
            'password': 'testpass'  # Correct password, but account locked
        })
        self.assertEqual(response.status_code, 429)  # Too Many Requests

    def test_sql_injection_prevention(self):
        """Test that GraphQL queries are protected against injection"""
        malicious_query = """
            query {
                pages(filter: {title: "'; DROP TABLE pages; --"}) {
                    id
                    title
                }
            }
        """
        response = self.graphql_query(malicious_query)
        self.assertIsNone(response.errors)
        # Verify tables still exist
        self.assertTrue(Page.objects.exists())
```

---

**Use Syntek Dev Suite for Security:**
- `/syntek-dev-suite:security` - Implement and audit security measures
- `/syntek-dev-suite:qa-tester` - Find security vulnerabilities
- `/syntek-dev-suite:review` - Security code review