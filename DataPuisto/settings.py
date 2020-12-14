"""
Django settings for DataPuisto project.

"""
import os
import posixpath

import environ

# import google.auth
# from google.cloud import secretmanager_v1beta1 as sm

import google.cloud.logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DataPuisto.settings')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ************* snippet starts, copied from Google Codelabs **************
# env_file = os.path.join(BASE_DIR,  ".env")

# SETTINGS_NAME = "application_settings"

# if not os.path.isfile(env_file):
    # _, project = google.auth.default()

    # if project:
        # client = sm.SecretManagerServiceClient()
        # name = f"projects/{project}/secrets/{SETTINGS_NAME}/versions/latest"
        # payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

        # with open(env_file, "w") as f:
            # f.write(payload)
# ************* snippet ends, copied from Google Codelabs **************

env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False),
    GAE_APPLICATION=(str, ''),
    DATABASE_HOST=(str, ''),
    LOG_FILE=(str, ''),
)
# reading .env file
# GAE_APPLICATION is automatically set by Google App Engine
if not env('GAE_APPLICATION'):
    environ.Env.read_env()

# False if not in os.environ
DEBUG = env('DEBUG')

# Raises django's ImproperlyConfigured exception if SECRET_KEY not in
# os.environ
SECRET_KEY = env('SECRET_KEY')

ALLOWED_HOSTS = ['*']

WSGI_APPLICATION = 'DataPuisto.wsgi.application'

# Application definition

INSTALLED_APPS = [
    'NavigantAnalyzer',
    'StravaAnalyzer',
    #
    #'app',
    # Add your apps here to enable them
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    MIDDLEWARE.insert(
            0,
            'debug_toolbar.middleware.DebugToolbarMiddleware'
            )

ROOT_URLCONF = 'DataPuisto.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

#
# ********** Database ********** 
#

# Parse database connection url strings like psql://user:pass@127.0.0.1:8458/db

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises 
    # ImproperlyConfigured exception if not found
    'default': env.db(),
    # read os.environ['SQLITE_URL']
    # 'extra': env.db('SQLITE_URL')
    # 'default': env.db('SQLITE_URL')
}

# Line written by Riku on 2020-11-28
# ---- has been made obsolete on 2020-11-30
# DATABASES['default']['OPTIONS'] = env('DATABASE_OPTIONS')

# Line written by Riku on 2020-11-30 to support Google App Engine socket def
if env('DATABASE_HOST'):
    DATABASES['default']['HOST'] = env('DATABASE_HOST')

#
# ********** Static files and media ********** 
#

# Media root is not meaningful in Google App Engine, used in other platforms
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
MEDIA_URL = '/uploads/'

STATIC_ROOT = posixpath.join(*(BASE_DIR.split(os.path.sep) + ['static']))
STATIC_URL = '/static/'

# GAE_APPLICATION is automatically set by Google App Engine
if env('GAE_APPLICATION'):
    # Define static storage via django-storages[google]
    GS_BUCKET_NAME = env('GS_BUCKET_NAME')
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    # For now the plan is to keep Static files among code
    # STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_DEFAULT_ACL = 'publicRead'

#
# ********** Authentication ********** 
#

LOGIN_URL = '/login'

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
]


#
# ********** Local settings ********** 
#

LOCALE_NAME = 'fi_FI'
LANGUAGE_CODE = 'fi'
TIME_ZONE = 'Europe/Helsinki'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#
# ********** Logging settings ********** 
#

handler_name = 'file'

# GAE_APPLICATION is automatically set by Google App Engine
if env('GAE_APPLICATION'):
    LOGGING_CONFIG = 'DataPuisto.logging_gc_datapuisto.configure'
    handler_name = 'gc_datapuisto'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'normal': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
            },
        },
    'handlers': {
        # If GAE_APPLICATION, the logging config will NOT create this file
        # handler. It is for the benefit of the default logging config.
        handler_name: {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'formatter': 'normal',
            'filename': env('LOG_FILE'),
            },
        },
    'loggers': {
        'django': {
            'handlers': [handler_name],
            'level': 'INFO',
            'propagate': True,
            },
        'NavigantAnalyzer.views': {
            'handlers': [handler_name],
            'level': 'INFO',
            'propagate': True,
            },
        'NavigantAnalyzer.downloaders': {
            'handlers': [handler_name],
            'level': 'INFO',
            'propagate': True,
            }, 
        'NavigantAnalyzer.analyzers': {
            'handlers': [handler_name],
            'level': 'INFO',
            'propagate': True,
            }, 
        'StravaAnalyzer.views': {
            'handlers': [handler_name],
            'level': 'INFO',
            'propagate': True,
            },
        }
    }


INTERNAL_IPS = [
    '127.0.0.1',
]
