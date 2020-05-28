"""
Django settings for jeugdzorg project.

Generated by 'django-admin startproject' using Django 2.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""
import os
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ENV = os.getenv("ENV", "develop")
DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")
# SOURCE_COMMIT = os.getenv("SOURCE_COMMIT", "no-build-number")
POSTGRES_DB = os.getenv("POSTGRES_DB", "jeugdzorg")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "notset")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
SECRET_KEY = os.getenv("SECRET_KEY", "default-secret")
SITE_ID = os.getenv("SITE_ID ", 1)

# swift storage
SWIFT_USERNAME = os.getenv("SWIFT_USERNAME")
SWIFT_PASSWORD = os.getenv("SWIFT_PASSWORD")
SWIFT_AUTH_URL = os.getenv("SWIFT_AUTH_URL")
SWIFT_TENANT_ID = os.getenv("SWIFT_TENANT_ID")
SWIFT_TENANT_NAME = os.getenv("SWIFT_TENANT_NAME")
SWIFT_REGION_NAME = os.getenv("SWIFT_REGION_NAME")

# mail settings
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", 'notset')

TEST = os.getenv("TEST", False)

DEBUG = SECRET_KEY == 'default-secret'

# DEBUG = ENV != 'production'

#f = open('/opt/git_rev', 'r')
#SOURCE_COMMIT = f.read()
SOURCE_COMMIT = 1

# SECURITY WARNING: don't run with debug turned on in production!
#DEBUG = True

ALLOWED_HOSTS = [
    '*',
]


# Application definition

INSTALLED_APPS = [
    'jeugdzorg',

    'adminsortable',
    'adminsortable2',
    'sortedm2m',
    'requests',
    'django_crontab',
    'storages',
    'import_export',
    'phonenumber_field',
    'rest_framework',
    'easy_thumbnails',
    'django_markup',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'jeugdzorg.middleware.CreateSessionKeyMiddleware',
]

ROOT_URLCONF = 'jeugdzorg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        # 'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'jeugdzorg.context_processors.app_settings',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

WSGI_APPLICATION = 'jeugdzorg.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

if not TEST and POSTGRES_HOST != 'notset':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': POSTGRES_DB,
            'USER': POSTGRES_USER,
            'PASSWORD': POSTGRES_PASSWORD,
            'HOST': POSTGRES_HOST,  # <-- this is new
            'PORT': '5432',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'jeugdzorg.validators.CustomPasswordValidator',
    },
]

AUTH_USER_MODEL = 'jeugdzorg.User'
USERNAME_FIELD = 'email'

LOGIN_REDIRECT_URL = '/profiel/bewerken/'
LOGIN_URL = '/login/'

PASSWORD_RESET_TIMEOUT_DAYS = 7

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'nl-NL'

TIME_ZONE = 'Europe/Amsterdam'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LANGUAGES = (
    ('nl-NL', 'Nederlands'),
)

DEFAULT_LANGUAGE = 0
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]


# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.join(BASE_DIR, 'static'))
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_FROM_EMAIL = 'info@fixxx7.amsterdam.nl'

# djangorestframework
REST_FRAMEWORK = {
    'DEFAULT_MODEL_SERIALIZER_CLASS':
            'rest_framework.serializers.HyperlinkedModelSerializer',
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [],
}

# easy_thumbnails settings
THUMBNAIL_ALIASES = {
    '': {
        'avatar_xx': {'size': (210, 210), 'crop': True},
        'avatar_x': {'size': (160, 160), 'crop': True},
        'avatar': {'size': (80, 80), 'crop': True},
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'jeugdzorg_cache_table',
    }
}

# login lockout after 3 attempts
AXES_COOLOFF_TIME = timedelta(minutes=20)
AXES_LOCKOUT_TEMPLATE = 'snippets/login_lockout.html'
AXES_FAILURE_LIMIT = 10


SEARCH_MODELS = [
    'Profiel',
    'Thema',
    'Regeling',
]


