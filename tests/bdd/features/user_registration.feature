# BDD Feature: User Registration
# Tests the complete user registration workflow

Feature: User Registration
  As a new user
  I want to register an account
  So that I can access the platform

  Background:
    Given the system is running
    And the database is clean

  Scenario: Successful user registration with valid data
    Given an organisation "Test Organisation" with slug "test-org" exists
    When I register with the following details:
      | field       | value                  |
      | email       | newuser@example.com    |
      | first_name  | John                   |
      | last_name   | Doe                    |
      | password    | SecurePass9#Xk        |
      | organisation| test-org               |
    Then registration should succeed
    And I should receive an email verification token
    And the user "newuser@example.com" should exist
    And the user "newuser@example.com" should not be verified
    And the user "newuser@example.com" should have an audit log entry for "user_registered"

  Scenario: Registration fails with weak password
    Given an organisation "Test Organisation" with slug "test-org" exists
    When I register with the following details:
      | field       | value                  |
      | email       | newuser@example.com    |
      | first_name  | John                   |
      | last_name   | Doe                    |
      | password    | weak                   |
      | organisation| test-org               |
    Then registration should fail with error "Password must be at least 12 characters"

  Scenario: Registration fails with duplicate email
    Given an organisation "Test Organisation" with slug "test-org" exists
    And a user "existing@example.com" already exists
    When I register with the following details:
      | field       | value                  |
      | email       | existing@example.com   |
      | first_name  | Jane                   |
      | last_name   | Smith                  |
      | password    | TestPassword123!@      |
      | organisation| test-org               |
    Then registration should fail with error "Email address already in use"

  Scenario: Registration fails with invalid email format
    Given an organisation "Test Organisation" with slug "test-org" exists
    When I register with the following details:
      | field       | value                  |
      | email       | invalid-email          |
      | first_name  | John                   |
      | last_name   | Doe                    |
      | password    | TestPassword123!@      |
      | organisation| test-org               |
    Then registration should fail with error "Enter a valid email address"

  Scenario Outline: Password validation rules
    Given an organisation "Test Organisation" with slug "test-org" exists
    When I register with email "test@example.com" and password "<password>"
    Then registration should "<result>"
    And I should see error message "<error>"

    Examples:
      | password             | result  | error                                      |
      | SecurePass9#Xk       | succeed |                                            |
      | short                | fail    | at least 12 characters                     |
      | nocapitalsk9!@       | fail    | at least 1 uppercase letter                |
      | NOLOWERCASEK9!@      | fail    | at least 1 lowercase letter                |
      | NoNumbersHere!@      | fail    | at least 1 digit                           |
      | NoSpecialChar9k      | fail    | at least 1 special character               |

  Scenario: Email verification after registration
    Given an organisation "Test Organisation" with slug "test-org" exists
    And I have registered with email "newuser@example.com"
    And I have received an email verification token
    When I verify my email with the token
    Then email verification should succeed
    And the user "newuser@example.com" should be verified
    And the email verification token should be marked as used

  Scenario: Email verification fails with expired token
    Given an organisation "Test Organisation" with slug "test-org" exists
    And I have registered with email "newuser@example.com"
    And I have received an email verification token that has expired
    When I verify my email with the expired token
    Then email verification should fail with error "Verification token has expired"
    And the user "newuser@example.com" should not be verified

  Scenario: Email verification fails with already used token
    Given an organisation "Test Organisation" with slug "test-org" exists
    And I have registered with email "newuser@example.com"
    And I have verified my email
    When I try to verify my email again with the same token
    Then email verification should fail with error "Verification token has already been used"
