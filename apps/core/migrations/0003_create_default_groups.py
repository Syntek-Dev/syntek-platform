"""Data migration to create default groups.

Creates the four default groups for multi-tenancy access control:
- Organisation Owner: Full access to all resources
- Admin: Administrative access except billing/ownership transfer
- Member: Standard access for content creation/editing
- Viewer: Read-only access to resources
"""

from django.db import migrations


def create_default_groups(apps, schema_editor) -> None:
    """Create default permission groups.

    Args:
        apps: Django apps registry
        schema_editor: Database schema editor
    """
    Group = apps.get_model("auth", "Group")

    groups = [
        "Organisation Owner",
        "Admin",
        "Member",
        "Viewer",
    ]

    for group_name in groups:
        Group.objects.get_or_create(name=group_name)


def remove_default_groups(apps, schema_editor) -> None:
    """Remove default permission groups.

    Args:
        apps: Django apps registry
        schema_editor: Database schema editor
    """
    Group = apps.get_model("auth", "Group")

    groups = [
        "Organisation Owner",
        "Admin",
        "Member",
        "Viewer",
    ]

    Group.objects.filter(name__in=groups).delete()


class Migration(migrations.Migration):
    """Migration to create default groups."""

    dependencies = [
        ("core", "0002_alter_sessiontoken_options_alter_totpdevice_options_and_more"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
