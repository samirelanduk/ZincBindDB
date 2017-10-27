import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = "nwb9(%k2_gljo=x-q=o=qz*qy&nqs%$#73s=pqynj!fhlbmtpl"

DEBUG = True

ROOT_URLCONF = "zincbind.urls"

DATABASES = {"default": {
 "ENGINE": "django.db.backends.sqlite3",
 "NAME": os.path.join(BASE_DIR, "data", "zinc.sqlite3")
}}
