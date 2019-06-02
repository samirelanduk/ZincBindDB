import os
from .secrets import SECRET_KEY

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = []

DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "django.contrib.staticfiles",
 "graphene_django",
 "core"
]

DATE_FORMAT = "D j M, Y"
USE_TZ = True
TIME_ZONE = "UTC"

MIDDLEWARE = [
 "django.middleware.common.CommonMiddleware",
]

DATABASES = {"default": {
 "ENGINE": "django.db.backends.sqlite3",
 "NAME": os.path.join(BASE_DIR, "data", "db.sqlite3")
}}

STATIC_URL = "/static/"
