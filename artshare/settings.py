from pathlib import Path
import os
import dj_database_url
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: read sensitive/production values from environment variables.
# Provide safe defaults for local development only.
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-on&=dp4ti1@m5tm&=ppws)6)%vv^+-%ydqe&4ii_q((3g54tq6'
)

# DEBUG should be False in production; set the environment variable
# DEBUG=False on Render to enable production mode.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# ALLOWED_HOSTS can be provided as a comma-separated env var for Render.
ALLOWED_HOSTS = [h for h in os.environ.get('ALLOWED_HOSTS', 'art-share.onrender.com,localhost,127.0.0.1').split(',') if h]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # your app
    'rest_framework',
    'corsheaders',
    'cloudinary_storage',
    'cloudinary'
]
# Cloudinary configuration
# Prefer a single CLOUDINARY_URL (cloudinary://<key>:<secret>@<cloud_name>)
# or set individual env vars. If credentials are not present, Django will
# fall back to the default FileSystemStorage (local media) which is useful
# for local development.
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')

# Use the standard Render-provided individual env vars when CLOUDINARY_URL is
# not present. Render and many PaaS providers set these exact variable names.
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    'API_KEY': os.environ.get('CLOUDINARY_API_KEY', ''),
    'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET', ''),
}

# True when either CLOUDINARY_URL is set or the individual creds are present
CLOUDINARY_CONFIGURED = bool(
    CLOUDINARY_URL or (
        CLOUDINARY_STORAGE.get('CLOUD_NAME') and CLOUDINARY_STORAGE.get('API_KEY') and CLOUDINARY_STORAGE.get('API_SECRET')
    )
)

# Enable Cloudinary storage only when we have credentials
if CLOUDINARY_CONFIGURED:
    # Optional: allow putting uploads into a specific Cloudinary folder via env var
    CLOUDINARY_UPLOAD_FOLDER = os.environ.get('CLOUDINARY_UPLOAD_FOLDER')
    if CLOUDINARY_UPLOAD_FOLDER:
        CLOUDINARY_STORAGE['UPLOAD_OPTIONS'] = {'folder': CLOUDINARY_UPLOAD_FOLDER}
    # Use Cloudinary storage backend when credentials are present. The
    # cloudinary and django-cloudinary-storage packages must be installed in
    # the runtime environment (e.g. via requirements.txt on Render).
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    # Explicitly use FileSystemStorage in non-cloud environments so MEDIA_ROOT works
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = os.environ.get('CORS_ALLOW_ALL_ORIGINS', 'False') == 'True'
# Allow a comma-separated list of origins, or default to the current frontend.
default_cors = os.environ.get('CORS_ALLOWED_ORIGINS', 'https://art-shar.netlify.app')
CORS_ALLOWED_ORIGINS = [o for o in default_cors.split(',') if o]

# CSRF trusted origins (comma-separated env var).
CSRF_TRUSTED_ORIGINS = [u for u in os.environ.get('CSRF_TRUSTED_ORIGINS', 'https://art-share.onrender.com').split(',') if u]

ROOT_URLCONF = 'artshare.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'artshare.wsgi.application'

DATABASES = {
    # Parse DATABASE_URL from environment (set by Render). Defaults to local sqlite.
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
        # Allow overriding SSL requirement with DB_SSL env var (True/False). If
        # not set, require SSL when DEBUG is False.
        ssl_require=(os.environ.get('DB_SSL', 'True' if not DEBUG else 'False') == 'True')
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",  # or "IsAuthenticated" for protected APIs
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'core.Artist'

if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'