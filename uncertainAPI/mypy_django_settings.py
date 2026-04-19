"""Minimal Django settings for django-stubs / mypy only (not used at runtime)."""

SECRET_KEY = "mypy-django-stubs-only-not-for-production"
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "rest_framework",
    "uncertainAPI",
]
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}
