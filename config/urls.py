"""URL configuration for backend_template project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpRequest, HttpResponse
from django.urls import include, path

urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),
    # GraphQL API
    path("graphql/", include("api.urls")),
    # Core utilities (health check, etc.)
    path("", include("apps.core.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # type: ignore[arg-type]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # type: ignore[arg-type]

    # Debug toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]

    # Sentry debug endpoint - triggers an error to verify Sentry is working
    # Only available in DEBUG mode for security
    def trigger_sentry_error(request: HttpRequest) -> HttpResponse:
        """Trigger a test error to verify Sentry integration.

        Visit /sentry-debug/ to trigger a ZeroDivisionError that will be
        captured by Sentry if configured correctly.

        Returns:
            Never returns - always raises ZeroDivisionError
        """
        _ = 1 / 0
        return HttpResponse("This will never be reached")

    urlpatterns += [path("sentry-debug/", trigger_sentry_error)]
