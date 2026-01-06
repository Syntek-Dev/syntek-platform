# User Story: SaaS Email Service Integration

<!-- CLICKUP_ID: 86c7d2t9j -->

## Story

**As a** business owner
**I want** to access an integrated email service with custom branding
**So that** I can manage email communications directly from the Syntek platform

## MoSCoW Priority

- **Must Have:** Email account management, inbox interface, compose functionality, email sending, domain configuration
- **Should Have:** Email templates, contact management, basic email analytics, spam filtering
- **Could Have:** Email scheduling, automation rules, advanced analytics
- **Won't Have:** Complex workflow automation in Phase 8


**Sprint:** Sprint 19

## Repository Coverage

| Repository      | Required | Notes                                                      |
| --------------- | -------- | ---------------------------------------------------------- |
| Backend         | ✅       | Email service, SMTP integration, email models, GraphQL API |
| Frontend Web    | ✅       | Email interface (inbox, compose, contacts)                 |
| Frontend Mobile | ✅       | Basic email viewing and compose                            |
| Shared UI       | ✅       | Email editor, message components                           |

## Acceptance Criteria

### Scenario 1: Configure Email Domain

**Given** a user has set up an organisation
**When** they access the email service
**Then** they can:

- Connect a custom domain (e.g., mail.company.com)
- Configure DNS records (MX, SPF, DKIM)
- Verify domain ownership
- Enable email service for the domain
  **And** DNS configuration guide is provided
  **And** verification status is shown

### Scenario 2: Create Email Account

**Given** a domain is configured
**When** an administrator creates an email account
**Then** they can:

- Specify email address (name@domain.com)
- Set password with requirements
- Assign user/role
- Configure forwarding rules
  **And** the account is created in the email system
  **And** user can log in immediately

### Scenario 3: Access Email Inbox

**Given** a user has an email account
**When** they access the Email app (via subdomain email.domain.com)
**Then** they can:

- View inbox with all received messages
- View message details
- Manage folders (Inbox, Sent, Drafts, Trash)
- Search messages
  **And** unread count is shown
  **And** messages are properly formatted

### Scenario 4: Compose and Send Email

**Given** a user is in the email application
**When** they compose a new email
**Then** they can:

- Add recipient(s) (with autocomplete from contacts)
- Add CC/BCC
- Compose message (rich text editor)
- Add attachments
- Attach design template (optional)
  **And** email is sent via configured SMTP
  **And** email appears in Sent folder
  **And** delivery status is tracked

### Scenario 5: Email Templates

**Given** a user needs to send similar emails
**When** they create an email template
**Then** they can:

- Save template with name
- Use design tokens for styling
- Insert dynamic variables (recipient name, etc.)
- Reuse templates in compose
  **And** templates are available per organisation

### Scenario 6: Contact Management

**Given** a user receives emails
**When** they manage contacts
**Then** they can:

- View all contacts
- Add contact details (name, email, company)
- Organise contacts in groups
- Search contacts
  **And** contacts are automatically created from received emails
  **And** contacts can be imported from CSV

### Scenario 7: Email Analytics

**Given** emails are sent
**When** analytics are viewed
**Then** the user can see:

- Number of emails sent/received (per day, week, month)
- Top senders/recipients
- Response times
- Email size distribution
  **And** analytics are visualised in charts

### Scenario 8: Spam and Security

**Given** emails are received
**When** spam filtering is active
**Then** the system:

- Automatically filters known spam
- Learns from user spam reports
- Shows spam score per email
- Allows user to whitelist/blacklist senders
  **And** phishing warnings are displayed

## Dependencies

- Email service provider (Mailgun, SendGrid custom)
- SMTP server setup
- DNS configuration
- Email models and database

## Tasks

### Backend Tasks

- [ ] Create EmailAccount model
- [ ] Create EmailMessage model with full message content
- [ ] Create EmailFolder model
- [ ] Create EmailTemplate model
- [ ] Create EmailContact model
- [ ] Create EmailDomain model with DNS records
- [ ] Implement SMTP integration
- [ ] Create email sending service
- [ ] Create email receiving/sync service
- [ ] Implement domain verification
- [ ] Create GraphQL queries for email operations
- [ ] Create GraphQL mutations for sending/composing
- [ ] Implement full-text search for emails
- [ ] Create email analytics aggregation
- [ ] Add spam filtering integration
- [ ] Implement attachment handling
- [ ] Create attachment virus scanning
- [ ] Add audit logging for email operations
- [ ] Create unit tests for email service
- [ ] Create integration tests with email provider

### Frontend Web Tasks

- [ ] Create Email application layout
- [ ] Create Inbox component with message list
- [ ] Create MessageDetail component
- [ ] Create Compose window
- [ ] Create RichTextEditor for email body
- [ ] Create AttachmentUploader
- [ ] Create RecipientInput with autocomplete
- [ ] Create FolderNavigation sidebar
- [ ] Create Contact list page
- [ ] Create ContactEditor component
- [ ] Create TemplateList and TemplateEditor
- [ ] Create EmailAnalyticsDashboard
- [ ] Create DomainSetupWizard
- [ ] Create SearchBar for emails
- [ ] Add drag-and-drop to move messages between folders

### Frontend Mobile Tasks

- [ ] Create Email app with tab navigation
- [ ] Create Inbox view (optimized for mobile)
- [ ] Create Message detail view
- [ ] Create Reply/Forward interface
- [ ] Create Compose interface (simplified)
- [ ] Create Attachment viewer

### Shared UI Tasks

- [ ] Create RichTextEditor component
- [ ] Create AttachmentList component
- [ ] Create EmailMessageRenderer component
- [ ] Create ContactSelector component
- [ ] Create TemplateSelector component
- [ ] Create MessageList component

## Story Points (Fibonacci)

**Estimate:** 21

**Complexity factors:**

- Complete email system implementation
- SMTP server integration
- DNS configuration and verification
- Email sending and receiving pipelines
- Message storage and retrieval
- Rich text editor integration
- Contact management
- Attachment handling and virus scanning
- Search and filtering
- Analytics generation
- Spam filtering
- Multi-platform UI implementation

---

## Related Stories

- US-004: Organisation Creation (domain setup)
- US-005: Design Token System (email template tokens)
- US-014: Third-Party Integration (email provider integration)
