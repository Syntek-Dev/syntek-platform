Feature: Audit Logging and Security Events
  As a security administrator
  I want all security-relevant events logged to separate files
  So that I can monitor, audit, and investigate security incidents

  Background:
    Given the logging service is configured
    And the log directory exists

  # Authentication Logging (auth.log)
  Scenario: Successful login is logged to auth.log
    Given a registered user with email "user@example.com"
    When the user logs in successfully
    Then an entry should be written to "auth.log"
    And the log entry should contain:
      | field      | value                |
      | event      | LOGIN                |
      | user_email | ***e.com             |
      | level      | INFO                 |

  Scenario: Failed login attempt is logged to auth.log
    Given no user exists with email "unknown@example.com"
    When a login attempt is made with email "unknown@example.com"
    Then an entry should be written to "auth.log"
    And the log entry should contain:
      | field  | value         |
      | event  | LOGIN_FAILED  |
      | level  | WARNING       |

  Scenario: Logout is logged to auth.log
    Given a logged-in user
    When the user logs out
    Then an entry should be written to "auth.log"
    And the log entry should contain:
      | field | value  |
      | event | LOGOUT |
      | level | INFO   |

  Scenario: Password change is logged to auth.log
    Given a logged-in user
    When the user changes their password
    Then an entry should be written to "auth.log"
    And the log entry should contain:
      | field | value           |
      | event | PASSWORD_CHANGE |
      | level | INFO            |

  Scenario: 2FA enablement is logged to auth.log
    Given a logged-in user without 2FA
    When the user enables 2FA
    Then an entry should be written to "auth.log"
    And the log entry should contain:
      | field | value              |
      | event | TWO_FACTOR_ENABLED |
      | level | INFO               |

  Scenario: 2FA disablement is logged to auth.log
    Given a logged-in user with 2FA enabled
    When the user disables 2FA
    Then an entry should be written to "auth.log"
    And the log entry should contain:
      | field | value               |
      | event | TWO_FACTOR_DISABLED |
      | level | INFO                |

  # Email Logging (mail.log)
  Scenario: Email verification sent is logged to mail.log
    Given a newly registered user
    When a verification email is sent
    Then an entry should be written to "mail.log"
    And the log entry should contain:
      | field      | value                    |
      | event      | VERIFICATION_EMAIL_SENT  |
      | level      | INFO                     |

  Scenario: Password reset email is logged to mail.log
    Given a user requests password reset
    When the password reset email is sent
    Then an entry should be written to "mail.log"
    And the log entry should contain:
      | field | value                    |
      | event | PASSWORD_RESET_EMAIL_SENT |
      | level | INFO                      |

  Scenario: Email delivery failure is logged to mail.log
    Given an invalid email address
    When email delivery fails
    Then an entry should be written to "mail.log"
    And the log entry should contain:
      | field | value                 |
      | event | EMAIL_DELIVERY_FAILED |
      | level | ERROR                 |

  # Security Logging (security.log)
  Scenario: Rate limit exceeded is logged to security.log
    Given a user making rapid requests
    When the rate limit is exceeded
    Then an entry should be written to "security.log"
    And the log entry should contain:
      | field | value               |
      | event | RATE_LIMIT_EXCEEDED |
      | level | WARNING             |

  Scenario: Account lockout is logged to security.log
    Given a user with too many failed login attempts
    When the account is locked
    Then an entry should be written to "security.log"
    And the log entry should contain:
      | field | value          |
      | event | ACCOUNT_LOCKED |
      | level | WARNING        |

  Scenario: Suspicious activity is logged to security.log
    Given a user logging in from a new location
    When suspicious activity is detected
    Then an entry should be written to "security.log"
    And the log entry should contain:
      | field | value                |
      | event | SUSPICIOUS_ACTIVITY  |
      | level | WARNING              |

  Scenario: IP encryption key rotation is logged to security.log
    Given the IP encryption keys need rotation
    When the keys are rotated
    Then an entry should be written to "security.log"
    And the log entry should contain:
      | field | value               |
      | event | IP_KEY_ROTATED      |
      | level | INFO                |

  # Database Logging (database.log)
  Scenario: Slow query is logged to database.log
    Given a database query takes longer than threshold
    When the slow query is detected
    Then an entry should be written to "database.log"
    And the log entry should contain:
      | field       | value      |
      | event       | SLOW_QUERY |
      | level       | WARNING    |

  Scenario: Database connection error is logged to database.log
    Given the database is unavailable
    When a connection error occurs
    Then an entry should be written to "database.log"
    And the log entry should contain:
      | field | value            |
      | event | CONNECTION_ERROR |
      | level | ERROR            |

  # GraphQL Logging (graphql.log)
  Scenario: GraphQL query is logged to graphql.log
    Given a GraphQL client
    When a query is executed
    Then an entry should be written to "graphql.log"
    And the log entry should contain:
      | field          | value         |
      | event          | GRAPHQL_QUERY |
      | operation_name | exists        |

  Scenario: GraphQL mutation is logged to graphql.log
    Given a GraphQL client
    When a mutation is executed
    Then an entry should be written to "graphql.log"
    And the log entry should contain:
      | field | value            |
      | event | GRAPHQL_MUTATION |

  Scenario: GraphQL error is logged to graphql.log
    Given a GraphQL client
    When a query results in an error
    Then an entry should be written to "graphql.log"
    And the log entry should contain:
      | field | value          |
      | event | GRAPHQL_ERROR  |
      | level | ERROR          |

  # Sensitive Data Redaction
  Scenario: Password is redacted from logs
    Given log data containing a password field
    When the log entry is written
    Then the password value should be "[REDACTED]"

  Scenario: Tokens are redacted from logs
    Given log data containing access_token and refresh_token
    When the log entry is written
    Then both token values should be "[REDACTED]"

  Scenario: Email is masked in logs
    Given log data containing email "user@example.com"
    When the log entry is written
    Then the email should be masked as "***.com"

  Scenario: TOTP secret is redacted from logs
    Given log data containing totp_secret
    When the log entry is written
    Then the totp_secret value should be "[REDACTED]"

  # Log File Separation
  Scenario: Each domain writes to its own log file
    Given the logging service is configured
    When events occur in different domains
    Then each domain should have its own log file:
      | domain   | file         |
      | auth     | auth.log     |
      | mail     | mail.log     |
      | security | security.log |
      | database | database.log |
      | graphql  | graphql.log  |
      | app      | app.log      |

  # Log Rotation
  Scenario: Log files rotate when size exceeds limit
    Given a log file at maximum size
    When a new log entry is written
    Then the log file should be rotated
    And a backup file should be created

  # Sentry Integration
  Scenario: Errors are sent to Sentry in production
    Given the application is in production mode
    And Sentry is configured
    When an error is logged
    Then the error should be sent to Sentry
    And sensitive data should be redacted

  Scenario: Sentry handles missing SDK gracefully
    Given Sentry SDK is not installed
    When an error is logged
    Then no exception should be raised
    And the error should be logged to file
