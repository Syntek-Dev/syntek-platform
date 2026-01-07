"""Health check views for monitoring and container orchestration.

This module provides health check endpoints used by Docker, Kubernetes,
load balancers, and monitoring services to verify application health.
"""

from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views import View


class HealthCheckView(View):
    """Health check endpoint for container orchestration and monitoring.

    Returns application health status including database connectivity.
    Used by Docker health checks, load balancers, and monitoring tools.

    Endpoints:
        GET /health/ - Returns health status as JSON

    Response format:
        {
            "status": "healthy" | "unhealthy",
            "version": "x.y.z",
            "checks": {
                "database": "ok" | "error: <message>"
            }
        }

    HTTP Status codes:
        200 - All checks passed
        503 - One or more checks failed
    """

    def get(self, request):
        """Perform health checks and return status.

        Args:
            request: HTTP request object.

        Returns:
            JsonResponse with health status and HTTP 200 or 503.
        """
        checks = {}
        healthy = True

        # Database check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            checks["database"] = "ok"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            healthy = False

        # Build response
        response_data = {
            "status": "healthy" if healthy else "unhealthy",
            "version": getattr(settings, "VERSION", "unknown"),
            "checks": checks,
        }

        status_code = 200 if healthy else 503
        return JsonResponse(response_data, status=status_code)
