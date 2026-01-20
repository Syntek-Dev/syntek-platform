"""Unit tests for AuditLog admin interface.

Tests the Django admin configuration for the AuditLog model including
custom actions, readonly fields, and export functionality.
"""

from datetime import timedelta

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

from apps.core.admin import AuditLogAdmin
from apps.core.models import AuditLog, Organisation

User = get_user_model()


@pytest.fixture
def admin_site():
    """Create admin site instance."""
    return AdminSite()


@pytest.fixture
def audit_log_admin(admin_site):
    """Create AuditLogAdmin instance."""
    return AuditLogAdmin(AuditLog, admin_site)


@pytest.fixture
def organisation(db):
    """Create test organisation."""
    return Organisation.objects.create(
        name="Test Organisation",
        slug="test-org",
    )


@pytest.fixture
def test_user(db, organisation):
    """Create test user."""
    user = User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
        organisation=organisation,
    )
    return user


@pytest.fixture
def admin_user(db, organisation):
    """Create admin user."""
    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        organisation=organisation,
    )
    return admin


@pytest.fixture
def audit_log(db, test_user, organisation):
    """Create test audit log."""
    from apps.core.utils.encryption import IPEncryption

    return AuditLog.objects.create(
        user=test_user,
        organisation=organisation,
        action="user.login",
        ip_address=IPEncryption.encrypt_ip("192.168.1.1"),
        user_agent="Mozilla/5.0",
        device_fingerprint="test-device",
        metadata={"test": "data"},
    )


@pytest.mark.unit
class TestAuditLogAdminConfiguration:
    """Test AuditLog admin configuration."""

    def test_audit_log_admin_list_display(self, audit_log_admin):
        """Test AuditLog admin list display fields."""
        expected_fields = (
            "action",
            "user",
            "organisation",
            "device_fingerprint",
            "created_at",
            "age_display",
        )
        assert audit_log_admin.list_display == expected_fields

    def test_audit_log_admin_list_filter(self, audit_log_admin):
        """Test AuditLog admin list filters."""
        expected_filters = ("action", "organisation", "created_at")
        assert audit_log_admin.list_filter == expected_filters

    def test_audit_log_admin_search_fields(self, audit_log_admin):
        """Test AuditLog admin search fields."""
        expected_search = ("user__email", "device_fingerprint")
        assert audit_log_admin.search_fields == expected_search

    def test_audit_log_admin_ordering(self, audit_log_admin):
        """Test AuditLog admin ordering."""
        assert audit_log_admin.ordering == ("-created_at",)

    def test_audit_log_admin_readonly_fields(self, audit_log_admin):
        """Test AuditLog admin readonly fields."""
        expected_readonly = (
            "user",
            "organisation",
            "action",
            "ip_address",
            "user_agent",
            "device_fingerprint",
            "metadata",
            "created_at",
            "age_display",
        )
        assert audit_log_admin.readonly_fields == expected_readonly

    def test_audit_log_admin_has_no_add_permission(self, audit_log_admin, admin_client):
        """Test AuditLog admin disables adding via admin."""
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.user = admin_client
        assert audit_log_admin.has_add_permission(request) is False

    def test_audit_log_admin_has_no_change_permission(self, audit_log_admin, admin_client):
        """Test AuditLog admin disables editing."""
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.user = admin_client
        assert audit_log_admin.has_change_permission(request) is False


@pytest.mark.unit
class TestAuditLogAdminViews:
    """Test AuditLog admin views."""

    def test_audit_log_admin_changelist_view(self, admin_client, audit_log):
        """Test AuditLog admin changelist view."""
        response = admin_client.get("/admin/core/auditlog/")
        assert response.status_code == 200
        assert b"user.login" in response.content

    def test_audit_log_admin_change_view(self, admin_client, audit_log):
        """Test AuditLog admin change view (readonly)."""
        response = admin_client.get(f"/admin/core/auditlog/{audit_log.id}/change/")
        assert response.status_code == 200
        assert b"user.login" in response.content

    def test_audit_log_admin_search(self, admin_client, audit_log, test_user):
        """Test AuditLog admin search functionality."""
        response = admin_client.get(f"/admin/core/auditlog/?q={test_user.email}")
        assert response.status_code == 200

    def test_audit_log_admin_filter_by_action(self, admin_client, audit_log):
        """Test AuditLog admin filtering by action."""
        response = admin_client.get("/admin/core/auditlog/?action=user.login")
        assert response.status_code == 200

    def test_audit_log_admin_filter_by_organisation(self, admin_client, audit_log):
        """Test AuditLog admin filtering by organisation."""
        response = admin_client.get(
            f"/admin/core/auditlog/?organisation__id__exact={audit_log.organisation_id}"
        )
        assert response.status_code == 200


@pytest.mark.unit
class TestAuditLogAdminAgeDisplay:
    """Test AuditLog admin age_display method."""

    def test_age_display_minutes(self, audit_log_admin, audit_log):
        """Test age_display shows minutes for recent logs."""
        # Create log 30 minutes ago
        audit_log.created_at = timezone.now() - timedelta(minutes=30)
        audit_log.save()

        age = audit_log_admin.age_display(audit_log)
        assert "minutes ago" in age

    def test_age_display_hours(self, audit_log_admin, audit_log):
        """Test age_display shows hours for logs within 24 hours."""
        # Create log 5 hours ago
        audit_log.created_at = timezone.now() - timedelta(hours=5)
        audit_log.save()

        age = audit_log_admin.age_display(audit_log)
        assert "hours ago" in age

    def test_age_display_days(self, audit_log_admin, audit_log):
        """Test age_display shows days for logs within 30 days."""
        # Create log 15 days ago
        audit_log.created_at = timezone.now() - timedelta(days=15)
        audit_log.save()

        age = audit_log_admin.age_display(audit_log)
        assert "days ago" in age

    def test_age_display_months(self, audit_log_admin, audit_log):
        """Test age_display shows months for logs within a year."""
        # Create log 60 days ago
        audit_log.created_at = timezone.now() - timedelta(days=60)
        audit_log.save()

        age = audit_log_admin.age_display(audit_log)
        assert "months ago" in age

    def test_age_display_years(self, audit_log_admin, audit_log):
        """Test age_display shows years for old logs."""
        # Create log 400 days ago
        audit_log.created_at = timezone.now() - timedelta(days=400)
        audit_log.save()

        age = audit_log_admin.age_display(audit_log)
        assert "years ago" in age or "year ago" in age


@pytest.mark.unit
class TestAuditLogAdminExport:
    """Test AuditLog admin CSV export action."""

    def test_export_to_csv_action_exists(self, audit_log_admin):
        """Test export_to_csv action is registered."""
        assert "export_to_csv" in audit_log_admin.actions

    def test_export_to_csv(self, admin_client, audit_log):
        """Test exporting audit logs to CSV."""
        # Select audit log for export
        data = {
            "action": "export_to_csv",
            "_selected_action": [str(audit_log.id)],
        }

        response = admin_client.post("/admin/core/auditlog/", data, follow=True)

        # Should return CSV file
        assert response.status_code == 200
        assert response["Content-Type"] == "text/csv"
        assert b"audit_logs.csv" in response.get("Content-Disposition", "").encode()

        # Check CSV contains expected data
        assert b"user.login" in response.content


@pytest.mark.unit
class TestAuditLogAdminArchive:
    """Test AuditLog admin archive action."""

    def test_archive_old_logs_action_exists(self, audit_log_admin):
        """Test archive_old_logs action is registered."""
        assert "archive_old_logs" in audit_log_admin.actions

    def test_archive_old_logs_no_old_logs(self, admin_client, audit_log):
        """Test archive action when no old logs exist."""
        # All logs are recent
        data = {
            "action": "archive_old_logs",
            "_selected_action": [str(audit_log.id)],
        }

        response = admin_client.post("/admin/core/auditlog/", data, follow=True)
        assert response.status_code == 200

    def test_archive_old_logs_with_old_logs(self, admin_client, audit_log):
        """Test archive action with old logs."""
        # Create old audit log
        old_log = AuditLog.objects.create(
            user=audit_log.user,
            organisation=audit_log.organisation,
            action="user.logout",
        )
        # Update created_at to 100 days ago (auto_now_add prevents setting during create)
        AuditLog.objects.filter(id=old_log.id).update(
            created_at=timezone.now() - timedelta(days=100)
        )

        # Run archive action
        data = {
            "action": "archive_old_logs",
            "_selected_action": [str(old_log.id)],
        }

        response = admin_client.post("/admin/core/auditlog/", data, follow=True)
        assert response.status_code == 200

        # Old log should be deleted
        assert not AuditLog.objects.filter(id=old_log.id).exists()


@pytest.mark.unit
class TestAuditLogAdminPermissions:
    """Test AuditLog admin permissions."""

    def test_only_superuser_can_delete(self, audit_log_admin, admin_user):
        """Test only superusers can delete audit logs."""
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        request.user = admin_user

        # Superuser can delete
        assert audit_log_admin.has_delete_permission(request) is True

        # Make user non-superuser
        admin_user.is_superuser = False
        admin_user.save()

        # Non-superuser cannot delete
        assert audit_log_admin.has_delete_permission(request) is False
