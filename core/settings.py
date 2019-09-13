import os
try:
    from .secrets import SECRET_KEY
except:
    import binascii
    SECRET_KEY = binascii.hexlify(os.urandom(24)).decode()

VERSION = "1.0.1"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = []

DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "corsheaders",
 "django.contrib.staticfiles",
 "graphene_django",
 "core"
]

CORS_ORIGIN_ALLOW_ALL = True

DATE_FORMAT = "D j M, Y"
USE_TZ = True
TIME_ZONE = "UTC"

MIDDLEWARE = [
 "django.middleware.common.CommonMiddleware",
 "corsheaders.middleware.CorsMiddleware",
]

DATABASES = {"default": {
 "ENGINE": "django.db.backends.sqlite3",
 "NAME": os.path.join(BASE_DIR, "data", "db.sqlite3")
}}

STATIC_URL = "/static/"
STATIC_ROOT = os.path.abspath(f"{BASE_DIR}/../static")

TEMPLATES = [{
 "BACKEND": "django.template.backends.django.DjangoTemplates",
 "APP_DIRS": True
}]

GRAPHENE = {
 "SCHEMA": "core.schema.schema"
}
