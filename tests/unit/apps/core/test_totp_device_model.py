"""Unit tests for TOTPDevice model.

Tests cover:
- TOTP device creation
- Fernet encryption for secret field (C2 security requirement)
- set_secret() method encrypts plain secret
- get_secret() method decrypts secret
- device_name field for multiple devices (H13)
- confirmed field tracking
- last_used_at tracking
- User can have multiple TOTP devices

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import pytest
import uuid
from django.core.exceptions import ValidationError
from django.utils import timezone
from unittest.mock import Mock, patch
from django.contrib.auth import get_user_model

from apps.core.models import TOTPDevice, Organisation

User = get_user_model()


@pytest.fixture
def mock_fernet():
    """Mock Fernet encryption for testing.

    Yields:
        Mock: Mocked Fernet instance.
    """
    with patch("apps.core.models.totp_device.Fernet") as mock:
        mock_instance = Mock()
        mock_instance.encrypt.return_value = b"encrypted_secret_data"
        mock_instance.decrypt.return_value = b"decrypted_secret_data"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.unit
@pytest.mark.django_db
class TestTOTPDeviceModel:
    """Unit tests for TOTPDevice model."""

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
        return User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

    def test_totp_device_creation_with_valid_data(self, user) -> None:
        """Test TOTP device is created successfully with valid data.

        Given: Valid TOTP device data (user, name, secret)
        When: TOTPDevice.objects.create() is called
        Then: TOTP device is created with correct attributes
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"encrypted_secret"
        )

        assert device.id is not None
        assert device.user == user
        assert device.name == "iPhone"
        assert device.is_confirmed is False
        assert device.last_used_at is None

    def test_totp_secret_is_stored_as_encrypted_binary(self, user) -> None:
        """Test TOTP secret is stored as encrypted BinaryField.

        Given: TOTP secret set
        When: Device is saved
        Then: Secret is stored as encrypted binary data
        """
        encrypted_secret = b"\x00\x01\x02\x03encrypted_data"
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=encrypted_secret
        )

        assert isinstance(device.secret, bytes)
        assert device.secret == encrypted_secret

    def test_totp_set_secret_encrypts_plain_secret(self, user) -> None:
        """Test set_secret() method encrypts plain text secret using Fernet.

        Given: Plain text TOTP secret
        When: set_secret() is called
        Then: Secret is encrypted using Fernet and stored
        """
        device = TOTPDevice(user=user, name="iPhone")

        plain_secret = "JBSWY3DPEHPK3PXP"  # Base32 TOTP secret
        device.set_secret(plain_secret)

        # Secret should be encrypted (not plain text)
        assert device.secret != plain_secret.encode()
        assert isinstance(device.secret, bytes)

    def test_totp_get_secret_decrypts_encrypted_secret(self, user) -> None:
        """Test get_secret() method decrypts stored secret using Fernet.

        Given: TOTP device with encrypted secret
        When: get_secret() is called
        Then: Secret is decrypted and returned as plain text
        """
        device = TOTPDevice(user=user, name="iPhone")

        # Set and then get the secret
        plain_secret = "JBSWY3DPEHPK3PXP"
        device.set_secret(plain_secret)
        device.save()

        decrypted_secret = device.get_secret()

        assert decrypted_secret == plain_secret

    def test_totp_device_name_allows_multiple_devices(self, user) -> None:
        """Test user can have multiple TOTP devices with different names.

        Given: User with one TOTP device
        When: Creating another TOTP device with different name
        Then: Second device is created successfully
        """
        device1 = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret1"
        )
        device2 = TOTPDevice.objects.create(
            user=user, name="Android", secret=b"secret2"
        )

        assert device1.name == "iPhone"
        assert device2.name == "Android"
        assert TOTPDevice.objects.filter(user=user).count() == 2

    def test_totp_device_name_max_length(self, user) -> None:
        """Test TOTP name has max length of 64 characters.

        Given: Device name longer than 64 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        device = TOTPDevice(
            user=user, name="a" * 65, secret=b"secret"
        )

        with pytest.raises(ValidationError) as exc_info:
            device.full_clean()

        assert "name" in exc_info.value.message_dict

    def test_totp_device_name_defaults_to_default(self, user) -> None:
        """Test TOTP name defaults to 'Default' if not specified.

        Given: TOTP device created without name
        When: Device is retrieved
        Then: name is 'Default'
        """
        device = TOTPDevice.objects.create(user=user, secret=b"secret")

        assert device.name == "Default"

    def test_totp_confirmed_defaults_to_false(self, user) -> None:
        """Test TOTP is_confirmed field defaults to False.

        Given: TOTP device created without is_confirmed
        When: Device is retrieved
        Then: is_confirmed is False by default
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )

        assert device.is_confirmed is False

    def test_totp_can_be_confirmed(self, user) -> None:
        """Test TOTP device can be confirmed after setup.

        Given: Unconfirmed TOTP device
        When: is_confirmed is set to True
        Then: Device is marked as confirmed
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )
        device.is_confirmed = True
        device.save()

        device.refresh_from_db()
        assert device.is_confirmed is True

    def test_totp_last_used_at_initially_null(self, user) -> None:
        """Test TOTP last_used_at is initially null.

        Given: New TOTP device
        When: Device is created
        Then: last_used_at is None
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )

        assert device.last_used_at is None

    def test_totp_last_used_at_updated_on_use(self, user) -> None:
        """Test TOTP last_used_at is updated when device is used.

        Given: TOTP device that has never been used
        When: last_used_at is set to current time
        Then: last_used_at timestamp is stored
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )

        before = timezone.now()
        device.last_used_at = timezone.now()
        device.save()
        after = timezone.now()

        assert device.last_used_at is not None
        assert before <= device.last_used_at <= after

    def test_totp_user_can_have_multiple_devices(self, user) -> None:
        """Test user can have multiple TOTP devices for redundancy.

        Given: User with no TOTP devices
        When: Creating multiple devices
        Then: All devices are associated with the user
        """
        devices = [
            TOTPDevice.objects.create(
                user=user, name=f"Device {i}", secret=f"secret{i}".encode()
            )
            for i in range(3)
        ]

        assert TOTPDevice.objects.filter(user=user).count() == 3
        device_names = [d.name for d in devices]
        assert "Device 0" in device_names
        assert "Device 1" in device_names
        assert "Device 2" in device_names

    def test_totp_device_deletion_does_not_delete_user(self, user) -> None:
        """Test deleting TOTP device does not delete associated user.

        Given: User with TOTP device
        When: TOTP device is deleted
        Then: User still exists
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )

        device.delete()

        assert User.objects.filter(id=user.id).exists()

    def test_totp_user_deletion_cascades_to_devices(self, user) -> None:
        """Test deleting user cascades to associated TOTP devices.

        Given: User with TOTP devices
        When: User is deleted
        Then: All associated TOTP devices are deleted
        """
        device1 = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret1"
        )
        device2 = TOTPDevice.objects.create(
            user=user, name="Android", secret=b"secret2"
        )
        device1_id = device1.id
        device2_id = device2.id

        user.delete()

        assert not TOTPDevice.objects.filter(id=device1_id).exists()
        assert not TOTPDevice.objects.filter(id=device2_id).exists()

    def test_totp_str_representation(self, user) -> None:
        """Test TOTP device string representation.

        Given: TOTP device with user and name
        When: str(device) is called
        Then: String contains user email and name
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )

        str_repr = str(device)
        assert "test@example.com" in str_repr or "iPhone" in str_repr

    def test_totp_uuid_primary_key(self, user) -> None:
        """Test TOTP device uses UUID as primary key.

        Given: TOTP device is created
        When: id field is checked
        Then: id is a valid UUID
        """
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )

        assert device.id is not None
        assert isinstance(device.id, uuid.UUID)

    def test_totp_db_table_name(self, user) -> None:
        """Test TOTP device model uses correct database table name.

        Given: TOTPDevice model
        When: _meta.db_table is checked
        Then: Table name is core_totp_device
        """
        assert TOTPDevice._meta.db_table == "core_totp_device"

    def test_totp_created_at_auto_set(self, user) -> None:
        """Test TOTP device created_at is automatically set on creation.

        Given: TOTP device is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        device = TOTPDevice.objects.create(
            user=user, name="iPhone", secret=b"secret"
        )
        after = timezone.now()

        assert device.created_at is not None
        assert before <= device.created_at <= after
