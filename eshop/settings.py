"""
Django settings for eshop project.

Generated by 'django-admin startproject' using Django 4.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
from datetime import timedelta
import os
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4@n)$5u8*l6vr!r$q7!gf1i2e0)ucdx+jvie02&x@!81b!=ymc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'djoser',
    'debug_toolbar',
    'store',
    'core',
    'tags',
    'likes',
    #'playground'
]


MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# if DEBUG:
#     MIDDLEWARE += ['silk.middleware.SilkyMiddleware']

INTERNAL_IPS = [
    '127.0.0.1',
]

ROOT_URLCONF = 'eshop.urls'

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

WSGI_APPLICATION = 'eshop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

# 设置完可使用python manage.py collectstatic

# 设置static地址
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 设置media地址
MEDIA_URL = '/media/' 
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,  #防止Decimal转化为String
    '''
    全局设置
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination' ，
    'PAGE_SIZE': 10

    '''
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

AUTH_USER_MODEL = 'core.User' #设置专属User


DJOSER = {
    'SERIALIZERS': {
        'user_create': 'core.serializers.UserCreateSerializer',
        'current_user': 'core.serializers.UserSerializer',
    }
}

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
   'ACCESS_TOKEN_LIFETIME': timedelta(days=1)
}

CELERY_BROKER_URL = 'redis://localhost: 6379/1' # 其中6379为指定的docker端口， 1为DB的名字

CELERY_BEAT_SCHECHE = {
    'notify_customers': {
        'task': 'playground.tasks.notify_customers', # 给出路径
        'schedule': 5, #5s循环一次 或者celery.schedules.crontab(day_of_week=1, hour=7,minute=30)周一7：30开始执行
        'args': ['hello ll'],
    }
}

# celery -A eshop beat开启
# celery -A eshop flower监视celery工作
#localhost:5555即可见
LOGGING = {
    'version': 1,   # 识别配置为 'dictConfig 版本 1' 格式。目前，这是唯一的 dictConfig 格式版本。
    'disable_existing_loggers': False,  # 我们希望其他的loggers仍然能正常运转
    'handlers': {   # console或file……进行处理
    
        #'console':{
        #   'class ': 'logging.StreamHandler'
        #},
    
        'file':{
            'class': 'logging.FileHandler',
            'filename': 'general.log' # 存放日志的文件名
        }
    },
    'loggers': {
        
        #'playground' 则只捕获来自playground的log信息
        #'playground.views'则只捕获来自playground.views的log信息
        '': {    # 针对所有应用
            'handlers': ['file'],
            #'level': ‘ERROR’  则只捕获error级别以上的message
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO') # 默认为INFO
        }
    },
    'formatters':{
        # 'simple' 则只有message
        'verbose': {
            'format': '{asctime} ({levelname}) - {name} - {message}',
            'style': '{' #str.format / '$' -> string.Template
        }
    }
       
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/2',
        'TIMEOUT': 10 * 60,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}