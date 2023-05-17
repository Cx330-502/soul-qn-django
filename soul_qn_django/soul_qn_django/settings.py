"""
Django settings for soul_qn_django project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import rest_framework

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-z#h=5ip&=e*kr2bt1iq#5-=w4nf#1blq@sk=*a2j_vm=bc)o*&"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',  # 跨域请求
    'user_about.apps.UserAboutConfig',  # 处理用户信息，包括登陆注册、群组管理等
    'analyse_qn.apps.AnalyseQnConfig',  # 处理问卷分析
    'answer_qn.apps.AnswerQnConfig',  # 处理问卷答题
    'edit_qn.apps.EditQnConfig',  # 处理问卷编辑
    'mainpage.apps.MainpageConfig',  # 处理主页
    'Qn.apps.QnConfig',  # 处理问卷数据 （所有表都放在Qn下的models文件中）
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # 跨域请求
    "django.middleware.common.CommonMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "soul_qn_django.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates']
        ,
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "soul_qn_django.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# MySQL数据库配置
mysql_ENGINE = 'django.db.backends.mysql'  # 这个不需要修改
mysql_NAME = 'soul_qn'  # 这个自己创建的数据库的名称
mysql_USER = 'root'  # 数据库的账户，如果是本地的数据库一般为 root
mysql_PASSWORD = 'zhouxiao123!'  # 数据库账户对应的密码
mysql_HOST = 'bj-cynosdbmysql-grp-rc5v68qm.sql.tencentcdb.com'  # 一般购买的云数据库对应路由和这个很类似，这是阿里云数据库的路由，
# 如果是本地的mysql一般默认为 127.0.0.1
# 如果是自己的服务器安装的mysql一般默认为服务器的公网IP
mysql_PORT = '21656'  # 这个除非自己特别设置过，否则本地mysql和购买的云数据库端口都是默认3306，当然如果是自己在服务器上安装的mysql可以修改端口，
# 但是务必保证该端口对应的防火墙是打开的

DATABASES = {
    'default': {
        'ENGINE': mysql_ENGINE,
        'NAME': mysql_NAME,
        'USER': mysql_USER,
        'PASSWORD': mysql_PASSWORD,
        'HOST': mysql_HOST,
        'PORT': mysql_PORT,
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"
MEDIA_ROOT = "D:/static/media/"


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
