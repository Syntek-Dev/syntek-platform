"""Unit tests for Organisation model.

Tests cover:
- Model creation with valid data
- Field validation (name, slug, industry)
- Unique constraints
- Model methods
- String representation
- Timestamps (created_at, updated_at)

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
import time
import uuid

from apps.core.models import Organisation


@pytest.mark.unit
@pytest.mark.django_db
class TestOrganisationModel:
    """Unit tests for Organisation model."""

    def test_organisation_creation_with_valid_data(self, db) -> None:
        """Test organisation is created successfully with valid data.

        Given: Valid organisation data (name, slug, industry)
        When: Organisation.objects.create() is called
        Then: Organisation is created with correct attributes
        """
        org = Organisation.objects.create(
            name="Test Organisation",
            slug="test-org",
            industry="technology",
        )

        assert org.id is not None
        assert org.name == "Test Organisation"
        assert org.slug == "test-org"
        assert org.industry == "technology"
        assert org.is_active is True
        assert org.created_at is not None
        assert org.updated_at is not None

    def test_organisation_slug_must_be_unique(self, db) -> None:
        """Test organisation slug must be unique.

        Given: An organisation with slug "test-org" exists
        When: Creating another organisation with the same slug
        Then: IntegrityError is raised
        """
        Organisation.objects.create(name="First Org", slug="test-org")

        with pytest.raises(IntegrityError):
            Organisation.objects.create(name="Second Org", slug="test-org")

    def test_organisation_name_required(self, db) -> None:
        """Test organisation name is required.

        Given: Organisation data without name
        When: full_clean() is called
        Then: ValidationError is raised
        """
        org = Organisation(slug="test-org", industry="technology")

        with pytest.raises(ValidationError) as exc_info:
            org.full_clean()

        assert "name" in exc_info.value.message_dict

    def test_organisation_slug_required(self, db) -> None:
        """Test organisation slug is required.

        Given: Organisation data without slug
        When: full_clean() is called
        Then: ValidationError is raised
        """
        org = Organisation(name="Test Org", industry="technology")

        with pytest.raises(ValidationError) as exc_info:
            org.full_clean()

        assert "slug" in exc_info.value.message_dict

    def test_organisation_slug_max_length(self, db) -> None:
        """Test organisation slug has max length of 255 characters.

        Given: Organisation with slug longer than 255 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        org = Organisation(name="Test Org", slug="a" * 256, industry="technology")

        with pytest.raises(ValidationError) as exc_info:
            org.full_clean()

        assert "slug" in exc_info.value.message_dict

    def test_organisation_name_max_length(self, db) -> None:
        """Test organisation name has max length of 255 characters.

        Given: Organisation with name longer than 255 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        org = Organisation(name="a" * 256, slug="test-org", industry="technology")

        with pytest.raises(ValidationError) as exc_info:
            org.full_clean()

        assert "name" in exc_info.value.message_dict

    def test_organisation_industry_optional(self, db) -> None:
        """Test organisation industry field is optional.

        Given: Organisation data without industry
        When: Organisation is created
        Then: Organisation is created successfully with blank industry
        """
        org = Organisation.objects.create(name="Test Org", slug="test-org")

        assert org.industry == ""
        assert org.id is not None

    def test_organisation_is_active_defaults_to_true(self, db) -> None:
        """Test organisation is_active field defaults to True.

        Given: Organisation created without specifying is_active
        When: Organisation is retrieved
        Then: is_active is True by default
        """
        org = Organisation.objects.create(name="Test Org", slug="test-org")

        assert org.is_active is True

    def test_organisation_can_be_deactivated(self, db) -> None:
        """Test organisation can be deactivated.

        Given: An active organisation exists
        When: is_active is set to False
        Then: Organisation is marked as inactive
        """
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        org.is_active = False
        org.save()

        org.refresh_from_db()
        assert org.is_active is False

    def test_organisation_str_representation(self, db) -> None:
        """Test organisation string representation returns name.

        Given: An organisation with a name
        When: str(organisation) is called
        Then: Organisation name is returned
        """
        org = Organisation.objects.create(name="Test Org", slug="test-org")

        assert str(org) == "Test Org"

    def test_organisation_created_at_auto_set(self, db) -> None:
        """Test organisation created_at is automatically set on creation.

        Given: Organisation is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        after = timezone.now()

        assert org.created_at is not None
        assert before <= org.created_at <= after

    def test_organisation_updated_at_auto_updates(self, db) -> None:
        """Test organisation updated_at is automatically updated on save.

        Given: An organisation exists
        When: Organisation is modified and saved
        Then: updated_at timestamp is updated
        """
        org = Organisation.objects.create(name="Test Org", slug="test-org")
        original_updated = org.updated_at

        # Small delay to ensure timestamp difference
        time.sleep(0.1)

        org.name = "Updated Org"
        org.save()

        assert org.updated_at > original_updated

    def test_organisation_slug_allows_hyphens(self, db) -> None:
        """Test organisation slug allows hyphens.

        Given: Organisation with slug containing hyphens
        When: Organisation is created
        Then: Organisation is created successfully
        """
        org = Organisation.objects.create(
            name="Test Organisation", slug="test-org-name-with-hyphens"
        )

        assert org.slug == "test-org-name-with-hyphens"

    def test_organisation_slug_validation_format(self, db) -> None:
        """Test organisation slug only allows valid slug characters.

        Given: Organisation with invalid slug characters (spaces, special chars)
        When: full_clean() is called
        Then: ValidationError is raised
        """
        org = Organisation(name="Test Org", slug="invalid slug!")

        with pytest.raises(ValidationError) as exc_info:
            org.full_clean()

        assert "slug" in exc_info.value.message_dict

    def test_organisation_industry_max_length(self, db) -> None:
        """Test organisation industry field has max length of 100 characters.

        Given: Organisation with industry longer than 100 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        org = Organisation(name="Test Org", slug="test-org", industry="a" * 101)

        with pytest.raises(ValidationError) as exc_info:
            org.full_clean()

        assert "industry" in exc_info.value.message_dict

    def test_organisation_ordering_by_name(self, db) -> None:
        """Test organisations are ordered by name by default.

        Given: Multiple organisations with different names
        When: Organisations are queried
        Then: Results are ordered alphabetically by name
        """
        Organisation.objects.create(name="Zebra Org", slug="zebra-org")
        Organisation.objects.create(name="Alpha Org", slug="alpha-org")
        Organisation.objects.create(name="Beta Org", slug="beta-org")

        orgs = list(Organisation.objects.all())
        names = [org.name for org in orgs]

        assert names == ["Alpha Org", "Beta Org", "Zebra Org"]

    def test_organisation_queryset_active_filter(self, db) -> None:
        """Test filtering organisations by is_active status.

        Given: Mix of active and inactive organisations
        When: Filtering by is_active=True
        Then: Only active organisations are returned
        """
        active_org = Organisation.objects.create(
            name="Active Org", slug="active-org", is_active=True
        )
        inactive_org = Organisation.objects.create(
            name="Inactive Org", slug="inactive-org", is_active=False
        )

        active_orgs = Organisation.objects.filter(is_active=True)

        assert active_org in active_orgs
        assert inactive_org not in active_orgs

    def test_organisation_uuid_primary_key(self, db) -> None:
        """Test organisation uses UUID as primary key.

        Given: Organisation is created
        When: id field is checked
        Then: id is a valid UUID
        """
        org = Organisation.objects.create(name="Test Org", slug="test-org")

        assert org.id is not None
        assert isinstance(org.id, uuid.UUID)

    def test_organisation_db_table_name(self, db) -> None:
        """Test organisation model uses correct database table name.

        Given: Organisation model
        When: _meta.db_table is checked
        Then: Table name is core_organisation
        """
        assert Organisation._meta.db_table == "core_organisation"

    def test_organisation_slug_index_exists(self, db) -> None:
        """Test organisation slug field has a database index.

        Given: Organisation model
        When: _meta.indexes is checked
        Then: slug field has an index
        """
        indexes = [idx.fields for idx in Organisation._meta.indexes]
        # Check if slug is indexed (either as standalone or in composite)
        has_slug_index = any("slug" in fields for fields in indexes)
        assert has_slug_index or Organisation._meta.get_field("slug").db_index
