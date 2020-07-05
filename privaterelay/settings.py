"""
Django settings for privaterelay project.

Generated by 'django-admin startproject' using Django 2.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import ipaddress
import os

from decouple import config
import markus
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# defaulting to blank to be production-broken by default
SECRET_KEY = config('SECRET_KEY', None, cast=str)

ALPHA_INVITE_TOKEN = config('ALPHA_INVITE_TOKEN', default=None)
MAX_ACTIVE_ACCOUNTS = config('MAX_ACTIVE_ACCOUNTS', default=1500, cast=int)
WAITLIST_OPEN = config('WAITLIST_OPEN', default=False, cast=bool)

DEBUG = config('DEBUG', False, cast=bool)
if DEBUG:
    INTERNAL_IPS = config(
        'DJANGO_INTERNAL_IPS', default=[]
    )

# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_HOST = config('DJANGO_SECURE_SSL_HOST', None)
SECURE_SSL_REDIRECT = config('DJANGO_SECURE_SSL_REDIRECT', False)
SECURE_REDIRECT_EXEMPT = [
    r'^__version__',
    r'^__heartbeat__',
    r'^__lbheartbeat__',
]
SECURE_HSTS_SECONDS = config('DJANGO_SECURE_HSTS_SECONDS', None)
SECURE_CONTENT_TYPE_NOSNIFF = config('DJANGO_SECURE_CONTENT_TYPE_NOSNIFF',
                                     True)
SECURE_BROWSER_XSS_FILTER = config('DJANGO_SECURE_BROWSER_XSS_FILTER', True)
SESSION_COOKIE_SECURE = config(
    'DJANGO_SESSION_COOKIE_SECURE', False, cast=bool
)
# maps fxa profile hosts to respective avatar hosts for CSP
AVATAR_IMG_SRC_MAP = {
    'https://stable.dev.lcip.org/profile/v1':   'stable.dev.lcip.org',
    'https://profile.stage.mozaws.net/v1':      'mozillausercontent.com',
    'https://profile.accounts.firefox.com/v1':  'firefoxusercontent.com',
}
AVATAR_IMG_SRC = AVATAR_IMG_SRC_MAP[config(
    'FXA_PROFILE_ENDPOINT', 'https://profile.accounts.firefox.com/v1'
)]
CSP_CONNECT_SRC = (
    "'self'",
    'https://www.google-analytics.com/',
    'https://accounts.firefox.com',
)
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = (
    "'self'",
    'https://www.google-analytics.com/',
)
CSP_STYLE_SRC = ("'self'",)
CSP_IMG_SRC = (
    "'self'",
    AVATAR_IMG_SRC,
)
REFERRER_POLICY = 'strict-origin-when-cross-origin'

ALLOWED_HOSTS = []
DJANGO_ALLOWED_HOST = config('DJANGO_ALLOWED_HOST', None)
if DJANGO_ALLOWED_HOST:
    ALLOWED_HOSTS += [DJANGO_ALLOWED_HOST]
DJANGO_ALLOWED_SUBNET = config('DJANGO_ALLOWED_SUBNET', None)
if DJANGO_ALLOWED_SUBNET:
    ALLOWED_HOSTS += [
        str(ip) for ip in ipaddress.IPv4Network(DJANGO_ALLOWED_SUBNET)
    ]


# Get our backing resource configs to check if we should install the app
ADMIN_ENABLED = config('ADMIN_ENABLED', None)


AWS_REGION = config('AWS_REGION', None)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', None)
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', None)
AWS_SNS_TOPIC = config('AWS_SNS_TOPIC', None)
AWS_SNS_KEY_CACHE = config('AWS_SNS_KEY_CACHE', 'default')
AWS_SES_CONFIGSET = config('AWS_SES_CONFIGSET', None)
SOCKETLABS_SERVER_ID = config('SOCKETLABS_SERVER_ID', 0, cast=int)
SOCKETLABS_API_KEY = config('SOCKETLABS_API_KEY', None)
SOCKETLABS_SECRET_KEY = config('SOCKETLABS_SECRET_KEY', None)
SOCKETLABS_VALIDATION_KEY = config('SOCKETLABS_VALIDATION_KEY', None)

RELAY_FROM_ADDRESS = config('RELAY_FROM_ADDRESS', None)
SITE_ORIGIN = config('SITE_ORIGIN', None)
GOOGLE_ANALYTICS_ID = config('GOOGLE_ANALYTICS_ID', None)

TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID', None)
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN', None)

STATSD_ENABLED = config('DJANGO_STATSD_ENABLED', False, cast=bool)
STATSD_HOST = config('DJANGO_STATSD_HOST', '127.0.0.1')
STATSD_PORT = config('DJANGO_STATSD_PORT', '8125')
STATSD_PREFIX = config('DJANGO_STATSD_PREFIX', 'fx-private-relay')

SERVE_ADDON = config('SERVE_ADDON', None)

# Application definition
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'dockerflow.django',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.fxa',

    'privaterelay.apps.PrivateRelayConfig',
]

if DEBUG:
    INSTALLED_APPS += [
        'debug_toolbar',
    ]

if ADMIN_ENABLED:
    INSTALLED_APPS += [
        'django.contrib.admin',
    ]

if AWS_SNS_TOPIC or SOCKETLABS_API_KEY:
    INSTALLED_APPS += [
        'emails.apps.EmailsConfig',
    ]

if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    INSTALLED_APPS += [
        'phones.apps.PhonesConfig',
    ]


def download_xpis(headers, path, url):
    if path.endswith('.xpi'):
        headers['Content-Disposition'] = 'attachment'

WHITENOISE_ADD_HEADERS_FUNCTION = download_xpis

def _get_initial_middleware():
    if STATSD_ENABLED:
        return [
            'privaterelay.middleware.ResponseMetrics',
        ]
    return []

MIDDLEWARE = _get_initial_middleware()

if DEBUG:
    MIDDLEWARE += [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ]

MIDDLEWARE += [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'csp.middleware.CSPMiddleware',
    'django_referrer_policy.middleware.ReferrerPolicyMiddleware',
    'dockerflow.django.middleware.DockerflowMiddleware',
    'privaterelay.middleware.FxAToRequest',
]

ROOT_URLCONF = 'privaterelay.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'privaterelay', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'emails.context_processors.relay_from_domain',
                'privaterelay.context_processors.django_settings',
            ],
        },
    },
]

MAX_NUM_BETA_ALIASES = 5

WSGI_APPLICATION = 'privaterelay.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default="sqlite:///%s" % os.path.join(BASE_DIR, 'db.sqlite3')
    )
}
MONITOR_DATABASE_URL = config('MONITOR_DATABASE_URL', None)
if MONITOR_DATABASE_URL:
    DATABASES['monitor'] = dj_database_url.parse(MONITOR_DATABASE_URL)


# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

SOCIALACCOUNT_PROVIDERS = {
    'fxa': {
        # Note: to request "profile" scope, must be a trusted Mozilla client
        'SCOPE': ['profile'],
        'AUTH_PARAMS': {'access_type': 'offline'},
        'OAUTH_ENDPOINT': config('FXA_OAUTH_ENDPOINT', 'https://oauth.accounts.firefox.com/v1'),
        'PROFILE_ENDPOINT': config('FXA_PROFILE_ENDPOINT', 'https://profile.accounts.firefox.com/v1'),
    }
}

SOCIALACCOUNT_EMAIL_VERIFICATION = 'none'

FXA_SETTINGS_URL = config('FXA_SETTINGS_URL', 'https://accounts.firefox.com/settings')

LOGGING = {
    'version': 1,
    'formatters': {
        'json': {
            '()': 'dockerflow.logging.JsonLogFormatter',
            'logger_name': 'fx-private-relay'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json'
        },
    },
    'loggers': {
        'request.summary': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'events': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }
}

sentry_sdk.init(
    dsn=config('SENTRY_DSN', None),
    integrations=[DjangoIntegration()],
)

markus.configure(
    backends=[
        {
            'class': 'markus.backends.datadog.DatadogMetrics',
            'options': {
                'statsd_host': STATSD_HOST,
                'statsd_port': STATSD_PORT,
                'statsd_prefix': STATSD_PREFIX,
            }
        }
    ]
)
