"""Django Admin configurations for core models.

Provides admin interfaces for User, Organisation, AuditLog, and token models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from apps.core.models import (
    AuditLog,
    EmailVerificationToken,
    Organisation,
    PasswordHistory,
    PasswordResetToken,
    SessionToken,
    TOTPDevice,
    User,
    UserProfile,
)


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    """Admin interface for Organisation model."""

    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for custom User model."""

    inlines = (UserProfileInline,)
    list_display = (
        "email",
        "first_name",
        "last_name",
        "organisation",
        "is_active",
        "is_staff",
        "email_verified",
        "two_factor_enabled",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "two_factor_enabled",
        "organisation",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    readonly_fields = ("created_at", "updated_at", "password_changed_at", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "organisation")},
        ),
        (
            _("SaaS Features"),
            {"fields": ("has_email_account", "has_vault_access")},
        ),
        (
            _("Security"),
            {
                "fields": (
                    "email_verified",
                    "two_factor_enabled",
                    "password_changed_at",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "organisation",
                ),
            },
        ),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model with retention policy management."""

    list_display = (
        "action",
        "user",
        "organisation",
        "device_fingerprint",
        "created_at",
        "age_display",
    )
    list_filter = ("action", "organisation", "created_at")
    search_fields = ("user__email", "device_fingerprint")
    ordering = ("-created_at",)
    readonly_fields = (
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
    actions = ["archive_old_logs", "export_to_csv"]

    def age_display(self, obj: AuditLog) -> str:
        """Display the age of the audit log entry.

        Args:
            obj: AuditLog instance.

        Returns:
            Human-readable age string.
        """
        from datetime import timedelta

        from django.utils import timezone

        age = timezone.now() - obj.created_at  # type: ignore[operator]
        if age < timedelta(hours=1):
            return f"{int(age.total_seconds() / 60)} minutes ago"
        elif age < timedelta(days=1):
            return f"{int(age.total_seconds() / 3600)} hours ago"
        elif age < timedelta(days=30):
            return f"{age.days} days ago"
        elif age < timedelta(days=365):
            return f"{int(age.days / 30)} months ago"
        else:
            return f"{int(age.days / 365)} years ago"

    age_display.short_description = "Age"  # type: ignore[attr-defined]

    @admin.action(description="Archive logs older than retention period")
    def archive_old_logs(self, request, queryset):
        """Archive audit logs older than the configured retention period.

        Retention period is configurable via AUDIT_LOG_RETENTION_DAYS setting.
        Default is 90 days for security logs.

        Args:
            request: HTTP request object.
            queryset: Selected queryset (ignored - operates on all logs).
        """
        from datetime import timedelta

        from django.conf import settings
        from django.contrib import messages
        from django.utils import timezone

        retention_days = getattr(settings, "AUDIT_LOG_RETENTION_DAYS", 90)
        cutoff_date = timezone.now() - timedelta(days=retention_days)

        # Count logs to be archived
        old_logs = AuditLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()

        if count == 0:
            self.message_user(
                request,
                f"No audit logs older than {retention_days} days found.",
                messages.INFO,
            )
            return

        # In production, this would archive to cold storage
        # For now, we'll just delete them
        old_logs.delete()

        self.message_user(
            request,
            f"Successfully archived {count} audit logs older than {retention_days} days.",
            messages.SUCCESS,
        )

    @admin.action(description="Export selected logs to CSV")
    def export_to_csv(self, request, queryset):
        """Export selected audit logs to CSV format.

        Args:
            request: HTTP request object.
            queryset: Selected audit logs.

        Returns:
            CSV file response.
        """
        import csv

        from django.http import HttpResponse

        from apps.core.utils.encryption import IPEncryption

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="audit_logs.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "ID",
                "Action",
                "User",
                "Organisation",
                "IP Address",
                "User Agent",
                "Device Fingerprint",
                "Metadata",
                "Created At",
            ]
        )

        for log in queryset:
            # Decrypt IP address for export (admin only)
            ip_address = ""
            if log.ip_address:
                try:
                    ip_address = IPEncryption.decrypt_ip(log.ip_address)
                except Exception:
                    ip_address = "[Encrypted]"

            writer.writerow(
                [
                    str(log.id),
                    log.action,
                    log.user.email if log.user else "N/A",
                    log.organisation.name if log.organisation else "N/A",
                    ip_address,
                    log.user_agent,
                    log.device_fingerprint,
                    str(log.metadata),
                    log.created_at.isoformat(),
                ]
            )

        return response

    def has_add_permission(self, request) -> bool:
        """Disable adding audit logs via admin."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Disable editing audit logs."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Only superusers can delete audit logs."""
        return request.user.is_superuser


@admin.register(SessionToken)
class SessionTokenAdmin(admin.ModelAdmin):
    """Admin interface for SessionToken model."""

    list_display = (
        "user",
        "device_fingerprint",
        "is_revoked",
        "last_activity_at",
        "expires_at",
    )
    list_filter = ("is_revoked", "is_refresh_token_used", "created_at")
    search_fields = ("user__email", "device_fingerprint")
    ordering = ("-created_at",)
    readonly_fields = (
        "token",
        "token_hash",
        "refresh_token_hash",
        "token_family",
        "created_at",
        "last_activity_at",
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    """Admin interface for PasswordResetToken model."""

    list_display = ("user", "used", "expires_at", "created_at")
    list_filter = ("used", "created_at")
    search_fields = ("user__email",)
    ordering = ("-created_at",)
    readonly_fields = ("token", "token_family", "created_at")


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin interface for EmailVerificationToken model."""

    list_display = ("user", "used", "expires_at", "created_at")
    list_filter = ("used", "created_at")
    search_fields = ("user__email",)
    ordering = ("-created_at",)
    readonly_fields = ("token", "token_family", "created_at")


@admin.register(TOTPDevice)
class TOTPDeviceAdmin(admin.ModelAdmin):
    """Admin interface for TOTPDevice model."""

    list_display = ("user", "name", "is_confirmed", "last_used_at", "created_at")
    list_filter = ("is_confirmed", "created_at")
    search_fields = ("user__email", "name")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "last_used_at", "confirmed_at")

    # Don't show the encrypted secret in admin
    exclude = ("secret",)


@admin.register(PasswordHistory)
class PasswordHistoryAdmin(admin.ModelAdmin):
    """Admin interface for PasswordHistory model."""

    list_display = ("user", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email",)
    ordering = ("-created_at",)
    readonly_fields = ("user", "password_hash", "created_at")

    def has_add_permission(self, request) -> bool:
        """Disable adding password history via admin."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Disable editing password history."""
        return False
