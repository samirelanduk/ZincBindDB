import os
import binascii

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = binascii.hexlify(os.urandom(24)).decode()

VERSION = "0.5.1"

ALLOWED_HOSTS = []

DEBUG = True

ROOT_URLCONF = "core.urls"

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "django.contrib.staticfiles",
 "django.contrib.humanize",
 "sass_processor",
 "rest_framework",
 "core",
 "zinc"
]

MIDDLEWARE = [
 "django.middleware.common.CommonMiddleware",
 "django.middleware.csrf.CsrfViewMiddleware",
]

STATIC_URL = "/static/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../static"))
SASS_PROCESSOR_ROOT = os.path.abspath(os.path.join(BASE_DIR, "core", "static"))

USE_TZ = False
DATE_FORMAT = "j F, Y"

TEMPLATES = [{
 "BACKEND": "django.template.backends.django.DjangoTemplates",
 "APP_DIRS": True,
 "OPTIONS": {
  "context_processors": [
   "django.template.context_processors.request"
  ],
  "builtins": ["zinc.templatetags"],
 },
}]

DATABASES = {"default": {
 "ENGINE": "django.db.backends.sqlite3",
 "NAME": os.path.join(BASE_DIR, "data/zinc.sqlite3")
}}

REST_FRAMEWORK = {
 "DEFAULT_AUTHENTICATION_CLASSES": [],
 "DEFAULT_PERMISSION_CLASSES": [],
 "UNAUTHENTICATED_USER": None,
 "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
 "PAGE_SIZE": 5
}
