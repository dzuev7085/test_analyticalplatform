import os
import sys

import environ
from django.urls import reverse_lazy

# SETUP
# ----------------------------------------------------------------------------
# Load .env variables into OS Environment variables
env = environ.Env(
    DEBUG=(bool, False)
)
ROOT_DIR = environ.Path(__file__) - 3  #
BASE_DIR = str(environ.Path(__file__) - 3)

if 'ENV_FILE' in os.environ:
    env.read_env(str(environ.Path(os.environ['ENV_FILE'])))
else:
    env.read_env(str(ROOT_DIR.path('.env')))


# GENERAL
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env('DEBUG')
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
TIME_ZONE = 'Europe/Stockholm'
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = False
# https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True
# Misc
FIRST_DAY_OF_WEEK = 1
# Language
LANGUAGES = (
    ('en-gb', ('UK English')),
)
ENVIRONMENT_MODE = env.str('ENVIRONMENT_MODE', 'DEV')

# SUPER USER
# ----------------------------------------------------------------------------
SUPERUSER_USER = env.str('SUPERUSER_USER')
SUPERUSER_EMAIL = env.str('SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = env.str('SUPERUSER_PASSWORD')


# STATIC FILES (CSS, JavaScript, Images)
# ----------------------------------------------------------------------------
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join("/", "var", "www", env.str('ENVIRONMENT_MODE'),
                           "static")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

# STATIC URLs
# ----------------------------------------------------------------------------
LOGIN_REDIRECT_URL = reverse_lazy('dashboard')

# LOGGING
# ----------------------------------------------------------------------------
SERVER_EMAIL = 'no-reply@nordiccreditrating.com'
ADMINS = [
    ('Patrik Lindgren', 'patrik.lindgren@nordiccreditrating.com'),
]
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} '
                      '{message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'null': {
            'class': 'logging.NullHandler',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': 'django.log',
            'maxBytes': 1024000,
            'backupCount': 3,
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'py.warnings': {
            'handlers': ['console'],
        },
    }
}


# DATABASES
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
# Create a sqllite database when running tests locally
if 'test' in sys.argv and env.str('ENVIRONMENT_MODE') in ['DEV']:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

else:
    DATABASES = {
        'default': env.db('DATABASE_URL',
                          default='sqlite:////tmp/my-tmp-sqlite.db'),
    }


# URLS
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = 'config.urls'
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# APPS
# ----------------------------------------------------------------------------
# This has to be loaded first to work
LOAD_FIRST_APPS = [
    'suit',
]
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize'
]
INTEGRATIONS = [
    'integrations.norges_bank',
    'integrations.sveriges_riksbank',
    'integrations.bloomberg',
    'integrations.esma',
    'integrations.database.datalake',
]
THIRD_PARTY_APPS = [
    'tinymce',
    'storages',
    'crispy_forms',
    'material',
    'material.frontend',
    'bootstrap_datepicker_plus',
    'django_celery_beat',
    'celerybeat_status',
    'simple_history',
    'debug_toolbar'
]
HELPERS = [
    'a_helper.bootstrap',
    'a_helper.other',
    'a_helper.mail',
    'a_helper.modal_helper',
    'a_helper.static_database_table',
]
LOCAL_APPS = [
    'document_export',
    'gui',  # holds all html files
    'financial_data',  # view and manipulate financial statements
    'issuer',
    'issue',
    'methodology',
    'rating_process',
    'rating',
    'sector_overview',
    'upload',
    'user_profile',
    'credit_assessment',
]

# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = (
    LOAD_FIRST_APPS +
    DJANGO_APPS +
    THIRD_PARTY_APPS +
    HELPERS +
    INTEGRATIONS +
    LOCAL_APPS
)

# MIGRATIONS
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules

# MIDDLEWARE
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':
                   [os.path.join(BASE_DIR, 'gui', 'templates', 'core'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'config.processors.environment_settings',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]}
    },
    {
        'BACKEND': "django.template.backends.jinja2.Jinja2",
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            'environment': 'config.settings.jinja2.environment',
        }
    },

]
# pylint: disable=line-too-long
# http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# FIXTURES
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#fixture-dirs
FIXTURE_DIRS = (
    os.path.join(str(ROOT_DIR), 'fixtures'),
)

# TEMPLATES
# ----------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
)

# SECURITY
# ----------------------------------------------------------------------------
ALLOWED_HOSTS = tuple(env.list('ALLOWED_HOSTS', default=[]))

# OTHER UTILS
# ----------------------------------------------------------------------------
APP_DIR = str(environ.Path(__file__) - 4)
sys.path.insert(0, os.path.join(APP_DIR, "database"))

# S3 STORAGE
# ----------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = env.str('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_ACCESS_KEY = env.str('AWS_SECRET_ACCESS_KEY', '')
AWS_STORAGE_BUCKET_NAME = env.str('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_CUSTOM_DOMAIN = '%s.s3-accelerate.amazonaws.com' % \
                       AWS_STORAGE_BUCKET_NAME
AWS_S3_ENCRYPTION = True

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_ANALYTICAL_MEDIA_LOCATION = 'analytical'
ANALYTICAL_FILE_STORAGE = 'config.storage_backends.AnalyticalMediaStorage'

AWS_ESMA_FILE_LOCATION = 'ESMA'
ESMA_FILE_STORAGE = 'config.storage_backends.ESMAMediaStorage'

AWS_COMMERCIAL_MEDIA_LOCATION = 'commercial'
COMMERCIAL_FILE_STORAGE = 'config.storage_backends.CommercialMediaStorage'

# TINY MCE
# ----------------------------------------------------------------------------
TINYMCE_INCLUDE_JQUERY = False  # Must be set to true for the form to work
TINYMCE_COMPRESSOR = True
TINYMCE_SPELLCHECKER = True
TINYMCE_JS_URL = os.path.join(STATIC_URL, "js", "tinymce", "tinymce.min.js")
TINYMCE_JS_ROOT = os.path.join(STATIC_URL, "js", "tinymce")
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': 800,
    'plugins': "table,spellchecker,paste,searchreplace",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'modern',
    'contextmenu': 'formats | link image',
    'toolbar': 'undo redo | bold italic underline | spellchecker',
    'menubar': True,
    'statusbar': True,
}

# MAIL
# ----------------------------------------------------------------------------
# Don't send out emails when we're testing
if env.str('ENVIRONMENT_MODE') in ['DEV']:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = env.str('EMAIL_HOST', 'notset')
EMAIL_HOST_USER = env.str('EMAIL_HOST_USER', 'notset')
EMAIL_HOST_PASSWORD = env.str('EMAIL_HOST_PASSWORD', 'notset')
EMAIL_PORT = '587'
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

# CELERY
# ----------------------------------------------------------------------------
# CELERY STUFF
CELERY_BROKER_URL = env.str('CELERY_BROKER_URL', 'redis://localhost:6379')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND',
                                'redis://localhost:6379')
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'
CELERY_ACKS_LATE = True
DJANGO_CELERY_BEAT_TZ_AWARE = True

if env.str('ENVIRONMENT_MODE') in ['DEV']:
    # Debug
    CELERY_ALWAYS_EAGER = True

# ESMA
# ----------------------------------------------------------------------------
ESMA_HOST = env.str('ESMA_HOST', False)
ESMA_USER_RATING = env.str('ESMA_USER_RATING', False)
ESMA_USER_FEE = env.str('ESMA_USER_FEE', False)
ESMA_PASSWORD_RATING = env.str('ESMA_PASSWORD_RATING', False)
ESMA_PASSWORD_FEE = env.str('ESMA_PASSWORD_FEE', False)
ESMA_CRA_CODE = env.str('ESMA_CRA_CODE', False)

# Django-toolbar
# ----------------------------------------------------------------------------
INTERNAL_IPS = ALLOWED_HOSTS

# MailChimp
# ----------------------------------------------------------------------------
MC_USER = env.str('MC_USER', False)
MC_API_KEY = env.str('MC_API_KEY', False)

# Mattermost
# ----------------------------------------------------------------------------
MATTERMOST_WEBHOOK = env.str('MATTERMOST_WEBHOOK', False)
