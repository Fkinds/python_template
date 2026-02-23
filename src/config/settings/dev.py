from config.settings.base import *  # noqa: F403
from config.settings.base import LOGGING
from config.settings.base import env

DEBUG = True

ALLOWED_HOSTS: list[str] = env.list("ALLOWED_HOSTS", default=["*"])

# lint-fixme: NoPositionalArgs: django-environ API
SECRET_KEY: str = env("SECRET_KEY", default="django-insecure-dev-key")

# ---- Dev: 通知の DEBUG ログを有効化 ----
LOGGING["loggers"]["notifications"]["level"] = "DEBUG"
