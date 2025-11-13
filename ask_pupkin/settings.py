from pathlib import Path
import os
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'QN1CyJYZIJoYrpN8kdYwnmgWXeHtwiT0mpFt7Z-GOtBSj-dj5rjYjUa7-yDzjXFkFQs'
DEBUG = True
ALLOWED_HOSTS = ['*']
INSTALLED_APPS = [
    'django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions',
    'django.contrib.messages','django.contrib.staticfiles','app',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'ask_pupkin.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'templates'],'APP_DIRS':True,
'OPTIONS':{'context_processors':[
'django.template.context_processors.debug','django.template.context_processors.request',
'django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages',],},},]
WSGI_APPLICATION = 'ask_pupkin.wsgi.application'
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("PG_NAME", "ask_pupkin"),
        "USER": os.getenv("PG_USER", "ask_pupkin"),
        "PASSWORD": os.getenv("PG_PASSWORD", "ask_pupkin"),
        "HOST": os.getenv("PG_HOST", "127.0.0.1"),
        "PORT": os.getenv("PG_PORT", "5432"),
    }
}
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'ru-ru'; TIME_ZONE = 'UTC'; USE_I18N = True; USE_TZ = True
STATIC_URL = '/static/'; STATICFILES_DIRS = [BASE_DIR/'static']
MEDIA_URL = '/uploads/'; MEDIA_ROOT = BASE_DIR/'uploads'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
