# Authentication User Guide

**Last Updated**: 17/01/2026
**Version**: 1.0.0
**Audience**: End Users

---

## Table of Contents

- [Authentication User Guide](#authentication-user-guide)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Getting Started](#getting-started)
    - [Creating an Account](#creating-an-account)
    - [Email Verification](#email-verification)
    - [Logging In](#logging-in)
  - [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa)
    - [What is 2FA?](#what-is-2fa)
    - [Why Should I Enable 2FA?](#why-should-i-enable-2fa)
    - [Setting Up 2FA](#setting-up-2fa)
    - [Logging In with 2FA](#logging-in-with-2fa)
    - [Backup Codes](#backup-codes)
    - [Disabling 2FA](#disabling-2fa)
  - [Password Management](#password-management)
    - [Password Requirements](#password-requirements)
    - [Changing Your Password](#changing-your-password)
    - [Resetting a Forgotten Password](#resetting-a-forgotten-password)
  - [Account Security](#account-security)
    - [Active Sessions](#active-sessions)
    - [Security Notifications](#security-notifications)
    - [Account Lockout Protection](#account-lockout-protection)
  - [Troubleshooting](#troubleshooting)
    - [I Didn't Receive the Verification Email](#i-didnt-receive-the-verification-email)
    - [I Lost Access to My Authenticator App](#i-lost-access-to-my-authenticator-app)
    - [I'm Locked Out of My Account](#im-locked-out-of-my-account)
    - [My Sessions Keep Getting Logged Out](#my-sessions-keep-getting-logged-out)
  - [Best Practices](#best-practices)
  - [Getting Help](#getting-help)

---

## Overview

This guide explains how to use the authentication features of the platform, including account creation, login, two-factor authentication, and password management.

**Key Features:**

- Secure account registration with email verification
- Two-factor authentication (2FA) for enhanced security
- Password reset functionality
- Active session management
- Security notifications for account activity

---

## Getting Started

### Creating an Account

To create a new account:

1. Navigate to the registration page
2. Fill in the required information:
   - **Email address**: Must be a valid email address
   - **First name**: Your given name
   - **Last name**: Your surname
   - **Password**: Must meet security requirements (see below)
   - **Organisation**: Select your organisation from the list

3. Click "Create Account"
4. Check your email for a verification link

**Password Requirements:**

- At least 12 characters long
- Contains at least 1 uppercase letter (A-Z)
- Contains at least 1 lowercase letter (a-z)
- Contains at least 1 digit (0-9)
- Contains at least 1 special character (!@#$%^&\*()\_+-=[]{}|;:,.<>?)
- Cannot be a commonly breached password

**Example of a strong password**: `MySecure2024Pass!`

### Email Verification

After registering, you must verify your email address:

1. Check your email inbox for a message from our platform
2. Click the verification link in the email
3. You will be redirected to a confirmation page
4. You can now log in to your account

**Important Notes:**

- Verification links expire after 24 hours
- If the link expires, you can request a new verification email
- You cannot log in until your email is verified

### Logging In

To log in to your account:

1. Navigate to the login page
2. Enter your email address and password
3. Click "Log In"
4. If you have 2FA enabled, you will be prompted for your authentication code (see below)

---

## Two-Factor Authentication (2FA)

### What is 2FA?

Two-factor authentication (2FA) adds an extra layer of security to your account. Instead of just using your password, you'll also need to provide a temporary code from your phone.

### Why Should I Enable 2FA?

2FA significantly increases your account security:

- **Prevents unauthorised access**: Even if someone knows your password, they can't log in without your phone
- **Protects sensitive data**: Adds extra security for accessing your account information
- **Industry standard**: Recommended by security experts and required by many organisations

### Setting Up 2FA

To enable 2FA on your account:

1. Log in to your account
2. Navigate to **Settings** > **Security** > **Two-Factor Authentication**
3. Click "Enable 2FA"
4. You'll receive:
   - A **QR code** to scan with your authenticator app
   - A **secret key** if you prefer to enter it manually
   - **10 backup codes** for emergency access

5. Scan the QR code using an authenticator app:
   - **Recommended apps**: Google Authenticator, Authy, Microsoft Authenticator
   - Available on iOS and Android

6. Enter the 6-digit code shown in your app
7. Click "Verify"
8. **Save your backup codes** in a secure location

**Important: Save Your Backup Codes**

Store your backup codes in a safe place. You'll need them if:

- You lose your phone
- You uninstall your authenticator app
- You get a new phone and forget to transfer your accounts

### Logging In with 2FA

Once 2FA is enabled, logging in requires two steps:

1. **Step 1**: Enter your email and password as usual
2. **Step 2**: Enter the 6-digit code from your authenticator app
3. Click "Verify"

**Tips:**

- The code changes every 30 seconds
- If a code expires, wait for the next one
- The system accepts codes from the previous and next 30-second window to account for clock drift

### Backup Codes

Backup codes are one-time-use codes for accessing your account if you lose access to your authenticator app.

**Using a Backup Code:**

1. On the 2FA challenge screen, click "Use a backup code instead"
2. Enter one of your 10 backup codes
3. Click "Verify"
4. The backup code will be marked as used and cannot be reused

**Generating New Backup Codes:**

1. Log in to your account
2. Navigate to **Settings** > **Security** > **Two-Factor Authentication**
3. Click "Generate New Backup Codes"
4. Confirm with your current TOTP code
5. Save the new codes securely
6. **Note**: Old backup codes will be invalidated

### Disabling 2FA

If you need to disable 2FA:

1. Log in to your account
2. Navigate to **Settings** > **Security** > **Two-Factor Authentication**
3. Click "Disable 2FA"
4. Confirm with your current TOTP code or a backup code
5. 2FA will be disabled

**Security Note:**

- You'll receive a security alert email when 2FA is disabled
- All your active sessions will be logged out
- You'll need to log in again

---

## Password Management

### Password Requirements

All passwords must meet these security requirements:

- **Minimum length**: 12 characters
- **Uppercase letters**: At least 1 (A-Z)
- **Lowercase letters**: At least 1 (a-z)
- **Digits**: At least 1 (0-9)
- **Special characters**: At least 1 (!@#$%^&\*()\_+-=[]{}|;:,.<>?)
- **Not breached**: Cannot be a commonly breached password

**Password Tips:**

- Use a passphrase: `Coffee&Morning2024!`
- Use a password manager to generate and store strong passwords
- Don't reuse passwords across different websites
- Change your password if you suspect it has been compromised

### Changing Your Password

To change your password:

1. Log in to your account
2. Navigate to **Settings** > **Security** > **Change Password**
3. Enter your current password
4. Enter your new password (must meet requirements)
5. Confirm your new password
6. If you have 2FA enabled, enter your authentication code
7. Click "Change Password"

**What Happens After Changing Your Password:**

- All other sessions will be logged out for security
- You'll remain logged in on the current device
- You'll receive a confirmation email
- If you have 2FA, you'll need to verify with your authenticator

### Resetting a Forgotten Password

If you've forgotten your password:

1. Navigate to the login page
2. Click "Forgot Password?"
3. Enter your email address
4. Click "Send Reset Link"
5. Check your email for a password reset link
6. Click the link (valid for 1 hour)
7. Enter your new password
8. Confirm your new password
9. Click "Reset Password"
10. Log in with your new password

**Important Notes:**

- Password reset links expire after 1 hour
- Each link can only be used once
- If you have 2FA enabled, you'll still need your authenticator after resetting

---

## Account Security

### Active Sessions

You can view and manage all active sessions on your account:

1. Log in to your account
2. Navigate to **Settings** > **Security** > **Active Sessions**
3. You'll see a list of all devices where you're logged in:
   - Device type and browser
   - IP address (anonymised)
   - Last activity time
   - Current session (marked)

**Managing Sessions:**

- **Log out a specific device**: Click "Log Out" next to that session
- **Log out all devices**: Click "Log Out All Devices" (except current)
- **Force log out everywhere**: Click "Log Out All Devices (Including This One)"

**Session Limits:**

- Maximum of 5 concurrent sessions per user
- When limit is reached, oldest session is automatically logged out
- No limit for administrator accounts

### Security Notifications

You'll receive email notifications for important security events:

- Login from a new device or location
- Password changed
- Email address changed
- 2FA enabled or disabled
- Multiple failed login attempts
- Password reset requested

**What to Do if You Receive an Unexpected Notification:**

1. Change your password immediately
2. Enable 2FA if not already enabled
3. Review active sessions and log out any unfamiliar devices
4. Contact support if you suspect unauthorised access

### Account Lockout Protection

Your account is protected against brute-force attacks:

- After 5 failed login attempts, your account is temporarily locked
- Lockout duration increases exponentially:
  - 1st lockout: 5 minutes
  - 2nd lockout: 15 minutes
  - 3rd lockout: 30 minutes
  - 4th+ lockout: 1 hour

**If Your Account is Locked:**

- Wait for the lockout period to expire
- Use the "Forgot Password?" link to reset your password
- Contact support if you need immediate access

---

## Troubleshooting

### I Didn't Receive the Verification Email

If you don't receive the verification email:

1. **Check your spam/junk folder**: Sometimes emails are filtered incorrectly
2. **Wait a few minutes**: Email delivery can be delayed
3. **Check the email address**: Ensure you registered with the correct email
4. **Request a new link**: Click "Resend Verification Email" on the login page
5. **Contact support**: If still not received after 30 minutes

### I Lost Access to My Authenticator App

If you've lost access to your authenticator app:

**Option 1: Use a Backup Code**

1. On the 2FA challenge screen, click "Use a backup code instead"
2. Enter one of your saved backup codes
3. After logging in, set up 2FA again with your new authenticator

**Option 2: Contact Support**

If you don't have backup codes:

1. Contact support with proof of identity
2. Support will temporarily disable 2FA on your account
3. Log in and immediately set up 2FA again
4. Save your new backup codes in a secure location

### I'm Locked Out of My Account

If you're locked out:

**Reason 1: Too Many Failed Login Attempts**

- Wait for the lockout period to expire (5-60 minutes)
- Use "Forgot Password?" to reset your password
- Enable 2FA for added security

**Reason 2: Forgot Password**

- Use the "Forgot Password?" link
- Follow the password reset process
- Check your email for the reset link

**Reason 3: Lost 2FA Device and No Backup Codes**

- Contact support immediately
- Provide proof of identity
- Support will disable 2FA temporarily
- Set up 2FA again after regaining access

### My Sessions Keep Getting Logged Out

If you're being logged out unexpectedly:

**Possible Causes:**

1. **Session Timeout**: Sessions expire after 24 hours of inactivity
2. **IP Address Changes**: Using VPN or changing networks
3. **Password Changed**: All sessions are logged out when password changes
4. **Multiple Devices**: You've exceeded the 5-session limit
5. **Browser Settings**: Cookies are being cleared automatically

**Solutions:**

- Stay active to prevent session timeout
- Use "Remember Me" if available
- Check browser cookie settings
- Log out unused devices from Active Sessions page

---

## Best Practices

Follow these security best practices:

1. **Use a Strong, Unique Password**
   - At least 12 characters
   - Mix of uppercase, lowercase, digits, and special characters
   - Never reuse passwords across sites
   - Use a password manager

2. **Enable Two-Factor Authentication**
   - Adds critical extra security layer
   - Save backup codes in a secure location
   - Use a trusted authenticator app

3. **Verify Your Email Address**
   - Required for account recovery
   - Ensures you receive security notifications
   - Keep your email address current

4. **Keep Your Email Secure**
   - Your email is the key to account recovery
   - Enable 2FA on your email account too
   - Use a strong password for your email

5. **Review Active Sessions Regularly**
   - Check for unfamiliar devices
   - Log out unused sessions
   - Report suspicious activity immediately

6. **Be Cautious of Phishing**
   - Never share your password or 2FA codes
   - Verify URLs before entering credentials
   - Be suspicious of unexpected password reset emails

7. **Update Contact Information**
   - Keep your email address current
   - Ensure you can receive security notifications

8. **Log Out on Shared Devices**
   - Always log out when using public or shared computers
   - Don't use "Remember Me" on shared devices

---

## Getting Help

If you need assistance:

**Support Channels:**

- **Email**: support@yourplatform.com
- **Help Centre**: https://help.yourplatform.com
- **Live Chat**: Available during business hours

**Before Contacting Support:**

- Check this user guide for answers
- Try the troubleshooting steps above
- Have your account email address ready
- Note any error messages you received

**Emergency Support:**

For urgent security issues (suspected unauthorised access):

- Email: security@yourplatform.com
- Response time: Within 1 hour during business hours

**What Support Can Help With:**

- Account recovery and password resets
- 2FA issues and device access problems
- Security concerns and suspicious activity
- Technical issues with login
- Questions about account security features

**What Support Cannot Do:**

- Provide your password (passwords are encrypted and cannot be retrieved)
- Bypass 2FA without proper identity verification
- Access your account without your permission

---

**Document Version**: 1.0.0  
**Last Updated**: 17/01/2026  
**Need Help?** Contact support@yourplatform.com
