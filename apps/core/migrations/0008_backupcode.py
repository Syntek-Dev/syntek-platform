# Generated manually for Phase 5: Two-Factor Authentication

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_user_account_locked_until_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="BackupCode",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="backup_codes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("code_hash", models.CharField(db_index=True, max_length=64)),
                ("used", models.BooleanField(db_index=True, default=False)),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Backup Code",
                "verbose_name_plural": "Backup Codes",
                "db_table": "core_backup_code",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddIndex(
            model_name="backupcode",
            index=models.Index(fields=["user", "used"], name="core_backup_user_id_used_idx"),
        ),
        migrations.AddIndex(
            model_name="backupcode",
            index=models.Index(fields=["code_hash"], name="core_backup_code_hash_idx"),
        ),
        migrations.AddConstraint(
            model_name="backupcode",
            constraint=models.UniqueConstraint(
                fields=["user", "code_hash"],
                name="unique_user_code_hash",
            ),
        ),
        # Add missing indexes for TOTPDevice from model definition
        migrations.AddIndex(
            model_name="totpdevice",
            index=models.Index(fields=["is_confirmed"], name="core_totp_d_is_conf_idx"),
        ),
    ]
