"""
Django settings for CSchoolSite project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

import CSchoolSite.personalsettings as psettings

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HOST = 'https://olimp-nw.ru'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')1ji)&$y2qxf3!d(_$9vauea=35-6yb=x1(-1h%cx+)(zflku4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = psettings.DEBUG

if DEBUG:
    ALLOWED_HOSTS = ['192.168.30.10', '127.0.0.1', 'localhost'] # need for vagrant
else:
    ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'admin_tools',
    'admin_tools.theming',
    'admin_tools.menu',
    'admin_tools.dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bootstrap3',
    'registration',
    'tinymce',
    'social_django',

    'main',
    'news',
    'applications',
    'userprofile',

    'django_cleanup'
]

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
]

ROOT_URLCONF = 'CSchoolSite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'main/../templates')]
        ,
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
                'admin_tools.template_loaders.Loader',
            ],
        },
    },
]

WSGI_APPLICATION = 'CSchoolSite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.' + psettings.DATABASE_ENGINE,
        'NAME': os.path.join(BASE_DIR, psettings.DATABASE_NAME) if psettings.DATABASE_ENGINE == "sqlite3" else psettings.DATABASE_NAME,
        'USER': psettings.DATABASE_USER,
        'PASSWORD': psettings.DATABASE_PASSWORD,
        'HOST': psettings.DATABASE_HOST,
        'PORT': psettings.DATABASE_PORT
    }
}

# for notifications
NOTIFICATIONS_USE_JSONFIELD=True

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS':
        {
            'min_length': 5,
        }
    }
]

AUTHENTICATION_BACKENDS = [
    'social_core.backends.vk.VKOAuth2',

    'django.contrib.auth.backends.ModelBackend'
]

SOCIAL_AUTH_VK_OAUTH2_KEY = ''
SOCIAL_AUTH_VK_OAUTH2_SECRET = ''
SOCIAL_AUTH_VK_OAUTH2_SCOPE = ['email']

SOCIAL_AUTH_PIPELINE = [
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'main.social.vkpipeline.get_user_vk_info',
    'social_core.pipeline.user.user_details'
]

AUTH_USER_MODEL = 'userprofile.User'
ADMIN_TOOLS_MENU = 'menu.CustomMenu'
ADMIN_TOOLS_INDEX_DASHBOARD = 'dashboard.CustomIndexDashboard'

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace,link",
    'cleanup_on_startup': True
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = psettings.STATIC_URL

# media files

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = psettings.MEDIA_URL

# registration

LOGIN_REDIRECT_URL = 'index'

# ejudge integration

EJUDGE_CONTEST_ID = psettings.EJUDGE_CONTEST_ID
EJUDGE_USER_LOGIN = psettings.EJUDGE_USER_LOGIN
EJUDGE_USER_PASSWORD = psettings.EJUDGE_USER_PASSWORD
EJUDGE_BIN = psettings.EJUDGE_BIN
EJUDGE_SESSION_TIMEOUT = 43200 # ejudge sets expiry to 24 hours, half that time just in case
EJUDGE_CONTESTS_CMD_PATH = os.path.join(EJUDGE_BIN, 'ejudge-contests-cmd')

# file serving

FILESERVE_METHOD = psettings.FILESERVE_METHOD
FILESERVE_MEDIA_URL = psettings.FILESERVE_MEDIA_URL

# telegram bot

TELEGRAM_TOKEN = 'your-token-here'

# celery
BROKER_URL = 'amqp://cschool:cschool@localhost:5672//'
