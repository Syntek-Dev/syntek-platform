"""Base Django settings for backend_template project.

Shared configuration across all environments.
Environment-specific settings should extend this file.
"""

from pathlib import Path

import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Environment variables
env = environ.Env(
    DEBUG=(bool, False),
)

# Read .env file if it exists
env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(str(env_file))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-CHANGE-ME-IN-PRODUCTION",
)

# Application definition
INSTALLED_APPS = [
    # Django core apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "corsheaders",
    "strawberry.django",
    # Project apps (add your apps here)
    "apps.core",
]

# Custom user model
AUTH_USER_MODEL = "core.User"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Custom security middleware
    "config.middleware.ip_allowlist.IPAllowlistMiddleware",
    "config.middleware.security.SecurityHeadersMiddleware",
    "config.middleware.ratelimit.RateLimitMiddleware",
    "config.middleware.audit.SecurityAuditMiddleware",
    # GraphQL middleware (C4 - CSRF, Authentication)
    "api.middleware.csrf.GraphQLCSRFMiddleware",
    "api.middleware.auth.GraphQLAuthenticationMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3"),
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "email", "first_name", "last_name"),
            "max_similarity": 0.7,
        },
    },
    {
        "NAME": "config.validators.password.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 12,
        },
    },
    {
        "NAME": "config.validators.password.MaximumLengthValidator",
        "OPTIONS": {
            "max_length": 128,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "config.validators.password.PasswordComplexityValidator",
        "OPTIONS": {
            "min_uppercase": 1,
            "min_lowercase": 1,
            "min_digits": 1,
            "min_special": 1,
        },
    },
    {
        "NAME": "config.validators.password.NoSequentialCharactersValidator",
        "OPTIONS": {
            "max_sequence_length": 3,
        },
    },
    {
        "NAME": "config.validators.password.NoRepeatedCharactersValidator",
        "OPTIONS": {
            "max_repeated": 3,
        },
    },
    {
        "NAME": "config.validators.password.HIBPPasswordValidator",
        "OPTIONS": {
            "threshold": 1,
            "timeout": 2,
        },
    },
    {
        "NAME": "config.validators.password.PasswordHistoryValidator",
        "OPTIONS": {
            "history_count": 5,
        },
    },
]

# Password hashing configuration
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

# Token signing key for HMAC-SHA256 hashing - C1 security requirement
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"
# This key is separate from SECRET_KEY for defense-in-depth
TOKEN_SIGNING_KEY = env(
    "TOKEN_SIGNING_KEY",
    default="",  # Must be set in production
)

# TOTP encryption key (Fernet) - C2 security requirement
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
TOTP_ENCRYPTION_KEY = env(
    "TOTP_ENCRYPTION_KEY",
    default="",  # Must be set in production
)

# IP address encryption key (Fernet) - for audit logs and session tracking
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
IP_ENCRYPTION_KEY = env(
    "IP_ENCRYPTION_KEY",
    default="",  # Must be set in production
)

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework settings
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=["http://localhost:3000"],
)
CORS_ALLOW_CREDENTIALS = True

# Cache settings
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/0"),
    }
}

# Email settings (overridden in environment-specific settings)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Rate limiting settings (requests per minute)
RATELIMIT_ENABLE_IN_DEBUG = env.bool("RATELIMIT_ENABLE_IN_DEBUG", default=False)
RATELIMIT_AUTH_REQUESTS_PER_MINUTE = env.int("RATELIMIT_AUTH_REQUESTS_PER_MINUTE", default=5)
RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE = env.int(
    "RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE", default=30
)
RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE = env.int(
    "RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE", default=100
)
RATELIMIT_API_REQUESTS_PER_MINUTE = env.int("RATELIMIT_API_REQUESTS_PER_MINUTE", default=60)
RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE = env.int(
    "RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE", default=120
)

# GraphQL security settings
GRAPHQL_MAX_QUERY_DEPTH = env.int("GRAPHQL_MAX_QUERY_DEPTH", default=10)
GRAPHQL_MAX_QUERY_COMPLEXITY = env.int("GRAPHQL_MAX_QUERY_COMPLEXITY", default=1000)
GRAPHQL_ENABLE_INTROSPECTION = env.bool("GRAPHQL_ENABLE_INTROSPECTION", default=False)

# Session security settings
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=1209600)  # 2 weeks

# CSRF security settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_USE_SESSIONS = False  # Store CSRF token in cookie for API compatibility
