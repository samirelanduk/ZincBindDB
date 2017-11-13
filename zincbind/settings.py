import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from .secrets import SECRET_KEY

DEBUG = True

ROOT_URLCONF = "zincbind.urls"

ALLOWED_HOSTS = []

DATABASES = {"default": {
 "ENGINE": "django.db.backends.sqlite3",
 "NAME": os.path.join(BASE_DIR, "data", "zinc.sqlite3")
}}

INSTALLED_APPS = [
 "django.contrib.contenttypes",
 "django.contrib.staticfiles",
 "zincbind"
]

TIME_ZONE = "UTC"

STATIC_URL = "/static/"
STATIC_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../static"))

TEMPLATES = [{
 "BACKEND": "django.template.backends.django.DjangoTemplates",
 "APP_DIRS": True
}]
