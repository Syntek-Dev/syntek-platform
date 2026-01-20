"""Unit tests for AuditLog model.

Tests cover:
- AuditLog creation with valid data
- Action choices validation
- User foreign key (nullable for failed login attempts)
- Organisation foreign key (SET_NULL on delete per H3)
- IP address encryption (BinaryField)
- User agent storage
- Metadata JSON field
- Timestamps
- UUID primary key
- Indexes for efficient querying
- Immutability considerations

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import uuid

from django.utils import timezone

import pytest

from apps.core.models import AuditLog, Organisation, User


@pytest.mark.unit
@pytest.mark.django_db
class TestAuditLogModel:
    """Unit tests for AuditLog model."""

    @pytest.fixture
    def organisation(self, db) -> Organisation:
        """Create a test organisation.

        Returns:
            Organisation instance for testing.
        """
        return Organisation.objects.create(name="Test Org", slug="test-org")

    @pytest.fixture
    def user(self, organisation) -> User:
        """Create a test user.

        Args:
            organisation: Organisation fixture.

        Returns:
            User instance for testing.
        """
        return User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            organisation=organisation,
        )

    def test_audit_log_creation_with_valid_data(self, user, organisation) -> None:
        """Test audit log is created successfully with valid data.

        Given: Valid audit log data (user, organisation, action, ip_address)
        When: AuditLog.objects.create() is called
        Then: AuditLog is created with correct attributes
        """
        encrypted_ip = b"\x00\x01\x02\x03encrypted_ip_data"
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=encrypted_ip,
            user_agent="Mozilla/5.0 Test Browser",
            metadata={"device": "desktop"},
        )

        assert log.id is not None
        assert log.user == user
        assert log.organisation == organisation
        assert log.action == "login_success"
        assert log.ip_address == encrypted_ip
        assert log.user_agent == "Mozilla/5.0 Test Browser"
        assert log.metadata == {"device": "desktop"}

    def test_audit_log_action_choices_login_success(self, user, organisation) -> None:
        """Test audit log accepts 'login_success' action.

        Given: Action value 'login_success'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        assert log.action == "login_success"

    def test_audit_log_action_choices_login_failed(self, organisation) -> None:
        """Test audit log accepts 'login_failed' action with null user.

        Given: Action value 'login_failed' and no user
        When: AuditLog is created
        Then: Log is created successfully with null user
        """
        log = AuditLog.objects.create(
            user=None,
            organisation=organisation,
            action="login_failed",
            ip_address=b"encrypted",
        )

        assert log.action == "login_failed"
        assert log.user is None

    def test_audit_log_action_choices_logout(self, user, organisation) -> None:
        """Test audit log accepts 'logout' action.

        Given: Action value 'logout'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="logout",
            ip_address=b"encrypted",
        )

        assert log.action == "logout"

    def test_audit_log_action_choices_register(self, user, organisation) -> None:
        """Test audit log accepts 'register' action.

        Given: Action value 'register'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="register",
            ip_address=b"encrypted",
        )

        assert log.action == "register"

    def test_audit_log_action_choices_password_reset_request(self, user, organisation) -> None:
        """Test audit log accepts 'password_reset_request' action.

        Given: Action value 'password_reset_request'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="password_reset_request",
            ip_address=b"encrypted",
        )

        assert log.action == "password_reset_request"

    def test_audit_log_action_choices_password_reset_complete(self, user, organisation) -> None:
        """Test audit log accepts 'password_reset_complete' action.

        Given: Action value 'password_reset_complete'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="password_reset_complete",
            ip_address=b"encrypted",
        )

        assert log.action == "password_reset_complete"

    def test_audit_log_action_choices_password_change(self, user, organisation) -> None:
        """Test audit log accepts 'password_change' action.

        Given: Action value 'password_change'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="password_change",
            ip_address=b"encrypted",
        )

        assert log.action == "password_change"

    def test_audit_log_action_choices_email_verify(self, user, organisation) -> None:
        """Test audit log accepts 'email_verify' action.

        Given: Action value 'email_verify'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="email_verify",
            ip_address=b"encrypted",
        )

        assert log.action == "email_verify"

    def test_audit_log_action_choices_2fa_enable(self, user, organisation) -> None:
        """Test audit log accepts '2fa_enable' action.

        Given: Action value '2fa_enable'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="2fa_enable",
            ip_address=b"encrypted",
        )

        assert log.action == "2fa_enable"

    def test_audit_log_action_choices_2fa_disable(self, user, organisation) -> None:
        """Test audit log accepts '2fa_disable' action.

        Given: Action value '2fa_disable'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="2fa_disable",
            ip_address=b"encrypted",
        )

        assert log.action == "2fa_disable"

    def test_audit_log_action_choices_2fa_verify_success(self, user, organisation) -> None:
        """Test audit log accepts '2fa_verify_success' action.

        Given: Action value '2fa_verify_success'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="2fa_verify_success",
            ip_address=b"encrypted",
        )

        assert log.action == "2fa_verify_success"

    def test_audit_log_action_choices_2fa_verify_failed(self, user, organisation) -> None:
        """Test audit log accepts '2fa_verify_failed' action.

        Given: Action value '2fa_verify_failed'
        When: AuditLog is created
        Then: Log is created successfully
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="2fa_verify_failed",
            ip_address=b"encrypted",
        )

        assert log.action == "2fa_verify_failed"

    def test_audit_log_user_can_be_null(self, organisation) -> None:
        """Test audit log user can be null (for failed login attempts).

        Given: AuditLog without user
        When: Log is created
        Then: Log is created with null user
        """
        log = AuditLog.objects.create(
            user=None,
            organisation=organisation,
            action="login_failed",
            ip_address=b"encrypted",
        )

        assert log.user is None
        assert log.id is not None

    def test_audit_log_organisation_set_null_on_delete(self, user, organisation) -> None:
        """Test audit log organisation is SET_NULL when organisation is deleted.

        Given: AuditLog with organisation
        When: Organisation is deleted
        Then: Log organisation is set to null (not deleted)
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )
        log_id = log.id

        organisation.delete()

        log.refresh_from_db()
        assert log.organisation is None
        assert AuditLog.objects.filter(id=log_id).exists()

    def test_audit_log_user_set_null_on_delete(self, user, organisation) -> None:
        """Test audit log user is SET_NULL when user is deleted.

        Given: AuditLog with user
        When: User is deleted
        Then: Log user is set to null (not deleted)
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )
        log_id = log.id

        user.delete()

        log.refresh_from_db()
        assert log.user is None
        assert AuditLog.objects.filter(id=log_id).exists()

    def test_audit_log_ip_address_stored_as_binary(self, user, organisation) -> None:
        """Test audit log IP address is stored as encrypted BinaryField.

        Given: Encrypted IP address data
        When: Log is saved
        Then: IP is stored as binary data
        """
        encrypted_ip = b"\x00\x01\x02\x03\x04\x05encrypted_ip"
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=encrypted_ip,
        )

        log.refresh_from_db()
        assert isinstance(log.ip_address, (bytes, memoryview))

    def test_audit_log_user_agent_optional(self, user, organisation) -> None:
        """Test audit log user_agent field is optional.

        Given: AuditLog without user_agent
        When: Log is created
        Then: Log is created with blank user_agent
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        assert log.user_agent == ""

    def test_audit_log_user_agent_stores_long_text(self, user, organisation) -> None:
        """Test audit log user_agent can store long text (TextField).

        Given: Long user agent string
        When: Log is saved
        Then: Full user agent is stored
        """
        long_user_agent = "Mozilla/5.0 " + "A" * 1000
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
            user_agent=long_user_agent,
        )

        log.refresh_from_db()
        assert log.user_agent == long_user_agent

    def test_audit_log_metadata_defaults_to_empty_dict(self, user, organisation) -> None:
        """Test audit log metadata defaults to empty dict.

        Given: AuditLog without metadata
        When: Log is created
        Then: Metadata is empty dict
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        assert log.metadata == {}

    def test_audit_log_metadata_stores_json(self, user, organisation) -> None:
        """Test audit log metadata stores JSON data correctly.

        Given: JSON metadata
        When: Log is saved
        Then: Metadata is stored and retrieved correctly
        """
        metadata = {
            "device": "desktop",
            "browser": "Chrome",
            "version": 120,
            "nested": {"key": "value"},
        }
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
            metadata=metadata,
        )

        log.refresh_from_db()
        assert log.metadata == metadata
        assert log.metadata["nested"]["key"] == "value"

    def test_audit_log_uses_uuid_primary_key(self, user, organisation) -> None:
        """Test audit log uses UUID as primary key.

        Given: AuditLog is created
        When: Log ID is checked
        Then: ID is a UUID instance
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        assert isinstance(log.id, uuid.UUID)

    def test_audit_log_created_at_auto_set(self, user, organisation) -> None:
        """Test audit log created_at is automatically set on creation.

        Given: AuditLog is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )
        after = timezone.now()

        assert log.created_at is not None
        assert before <= log.created_at <= after

    def test_audit_log_ordering_by_created_at_descending(self, user, organisation) -> None:
        """Test audit logs are ordered by created_at descending by default.

        Given: Multiple audit logs
        When: Logs are queried
        Then: Results are ordered newest first
        """
        import time

        log1 = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )
        time.sleep(0.1)
        log2 = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="logout",
            ip_address=b"encrypted",
        )
        time.sleep(0.1)
        log3 = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="password_change",
            ip_address=b"encrypted",
        )

        logs = list(AuditLog.objects.all())
        assert logs[0] == log3
        assert logs[1] == log2
        assert logs[2] == log1

    def test_audit_log_str_representation(self, user, organisation) -> None:
        """Test audit log string representation.

        Given: AuditLog with user and action
        When: str(log) is called
        Then: String contains action or relevant info
        """
        log = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        str_repr = str(log)
        # Should contain action or meaningful text
        assert "login" in str_repr.lower() or "audit" in str_repr.lower()

    def test_audit_log_db_table_name(self) -> None:
        """Test audit log uses correct database table name.

        Given: AuditLog model
        When: Model Meta is checked
        Then: db_table is 'audit_logs'
        """
        assert AuditLog._meta.db_table == "audit_logs"

    def test_audit_log_has_user_created_at_index(self) -> None:
        """Test audit log has index on (user, -created_at).

        Given: AuditLog model
        When: Model Meta indexes are checked
        Then: Index on user and created_at exists
        """
        index_fields = []
        for index in AuditLog._meta.indexes:
            index_fields.append(index.fields)

        assert ["user", "-created_at"] in index_fields

    def test_audit_log_has_organisation_created_at_index(self) -> None:
        """Test audit log has index on (organisation, -created_at).

        Given: AuditLog model
        When: Model Meta indexes are checked
        Then: Index on organisation and created_at exists
        """
        index_fields = []
        for index in AuditLog._meta.indexes:
            index_fields.append(index.fields)

        assert ["organisation", "-created_at"] in index_fields

    def test_audit_log_has_action_created_at_index(self) -> None:
        """Test audit log has index on (action, -created_at).

        Given: AuditLog model
        When: Model Meta indexes are checked
        Then: Index on action and created_at exists
        """
        index_fields = []
        for index in AuditLog._meta.indexes:
            index_fields.append(index.fields)

        assert ["action", "-created_at"] in index_fields

    def test_audit_log_filter_by_user(self, user, organisation) -> None:
        """Test filtering audit logs by user.

        Given: Multiple logs for different users
        When: Filtering by specific user
        Then: Only logs for that user are returned
        """
        other_user = User.objects.create(email="other@example.com", organisation=organisation)

        log1 = AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )
        log2 = AuditLog.objects.create(
            user=other_user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        user_logs = AuditLog.objects.filter(user=user)
        assert log1 in user_logs
        assert log2 not in user_logs

    def test_audit_log_filter_by_action(self, user, organisation) -> None:
        """Test filtering audit logs by action type.

        Given: Multiple logs with different actions
        When: Filtering by specific action
        Then: Only logs with that action are returned
        """
        AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )
        AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="logout",
            ip_address=b"encrypted",
        )
        AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="login_success",
            ip_address=b"encrypted",
        )

        login_logs = AuditLog.objects.filter(action="login_success")
        assert login_logs.count() == 2
