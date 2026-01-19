"""Unit tests for Organisation admin interface.

Tests the Django admin configuration for the Organisation model.
"""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model

import pytest

from apps.core.admin import OrganisationAdmin
from apps.core.models import Organisation

User = get_user_model()


@pytest.fixture
def admin_site():
    """Create admin site instance."""
    return AdminSite()


@pytest.fixture
def organisation_admin(admin_site):
    """Create OrganisationAdmin instance."""
    return OrganisationAdmin(Organisation, admin_site)


@pytest.fixture
def organisation(db):
    """Create test organisation."""
    return Organisation.objects.create(
        name="Test Organisation",
        slug="test-org",
    )


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


@pytest.mark.unit
class TestOrganisationAdminConfiguration:
    """Test Organisation admin configuration."""

    def test_organisation_admin_list_display(self, organisation_admin):
        """Test Organisation admin list display fields."""
        expected_fields = ("name", "slug", "is_active", "created_at")
        assert organisation_admin.list_display == expected_fields

    def test_organisation_admin_list_filter(self, organisation_admin):
        """Test Organisation admin list filters."""
        expected_filters = ("is_active", "created_at")
        assert organisation_admin.list_filter == expected_filters

    def test_organisation_admin_search_fields(self, organisation_admin):
        """Test Organisation admin search fields."""
        expected_search = ("name", "slug")
        assert organisation_admin.search_fields == expected_search

    def test_organisation_admin_ordering(self, organisation_admin):
        """Test Organisation admin ordering."""
        assert organisation_admin.ordering == ("name",)

    def test_organisation_admin_readonly_fields(self, organisation_admin):
        """Test Organisation admin readonly fields."""
        expected_readonly = ("created_at", "updated_at")
        assert organisation_admin.readonly_fields == expected_readonly

    def test_organisation_admin_prepopulated_fields(self, organisation_admin):
        """Test Organisation admin prepopulated fields."""
        expected_prepopulated = {"slug": ("name",)}
        assert organisation_admin.prepopulated_fields == expected_prepopulated


@pytest.mark.unit
class TestOrganisationAdminViews:
    """Test Organisation admin views."""

    def test_organisation_admin_changelist_view(self, admin_client, organisation):
        """Test Organisation admin changelist view."""
        response = admin_client.get("/admin/core/organisation/")
        assert response.status_code == 200
        assert b"Test Organisation" in response.content

    def test_organisation_admin_change_view(self, admin_client, organisation):
        """Test Organisation admin change view."""
        response = admin_client.get(f"/admin/core/organisation/{organisation.id}/change/")
        assert response.status_code == 200
        assert b"Test Organisation" in response.content
        assert b"test-org" in response.content

    def test_organisation_admin_add_view(self, admin_client):
        """Test Organisation admin add view."""
        response = admin_client.get("/admin/core/organisation/add/")
        assert response.status_code == 200

    def test_organisation_admin_search(self, admin_client, organisation):
        """Test Organisation admin search functionality."""
        response = admin_client.get("/admin/core/organisation/?q=Test")
        assert response.status_code == 200
        assert b"Test Organisation" in response.content

    def test_organisation_admin_filter_by_active(self, admin_client, organisation):
        """Test Organisation admin filtering by is_active."""
        response = admin_client.get("/admin/core/organisation/?is_active__exact=1")
        assert response.status_code == 200
        assert b"Test Organisation" in response.content

    def test_organisation_admin_create(self, admin_client):
        """Test creating organisation via admin."""
        data = {
            "name": "New Organisation",
            "slug": "new-org",
            "is_active": True,
        }

        response = admin_client.post("/admin/core/organisation/add/", data, follow=True)
        assert response.status_code == 200

        # Verify organisation was created
        org = Organisation.objects.filter(slug="new-org").first()
        assert org is not None
        assert org.name == "New Organisation"

    def test_organisation_admin_update(self, admin_client, organisation):
        """Test updating organisation via admin."""
        data = {
            "name": "Updated Organisation",
            "slug": organisation.slug,
            "is_active": True,
        }

        response = admin_client.post(
            f"/admin/core/organisation/{organisation.id}/change/",
            data,
            follow=True,
        )
        assert response.status_code == 200

        # Verify organisation was updated
        organisation.refresh_from_db()
        assert organisation.name == "Updated Organisation"


@pytest.mark.unit
class TestOrganisationAdminSlugGeneration:
    """Test Organisation admin slug auto-generation."""

    def test_slug_prepopulated_from_name(self, admin_client):
        """Test slug is auto-generated from name in admin form."""
        response = admin_client.get("/admin/core/organisation/add/")
        assert response.status_code == 200
        # Check that JavaScript for prepopulated fields is present
        assert b"prepopulated_fields" in response.content or b"data-prepopulate" in response.content
