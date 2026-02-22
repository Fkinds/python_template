from config.settings.base import *  # noqa: F403
from config.settings.base import env

DEBUG = False

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS")

# lint-fixme: NoPositionalArgs: django-environ API
SECRET_KEY: str = env("SECRET_KEY")

# ---- Security hardening ----
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
