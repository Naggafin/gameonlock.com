import os

from .base import *  # noqa: F403

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

DEBUG = False
SECRET_KEY = os.getenv("SECRET_KEY")
ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
	"default": {
		"ENGINE": "django.db.backends.postgresql",
		"NAME": os.environ.get("DB_NAME"),
		"USER": os.environ.get("DB_USER"),
		"PASSWORD": os.environ.get("DB_PASSWORD"),
		"HOST": os.environ.get("DB_HOST"),
		"PORT": os.environ.get("DB_PORT"),
		"ATOMIC_REQUESTS": True,
	},
}


# Cache
# https://docs.djangoproject.com/en/5.0/topics/cache

CACHES = {
	"default": {
		"BACKEND": "django_redis.cache.RedisCache",
		"LOCATION": os.environ.get("REDIS_URL"),
		"OPTIONS": {
			"CLIENT_CLASS": "django_redis.client.DefaultClient",
			"PARSER_CLASS": "redis.connection._HiredisParser",
		},
	},
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"


# channels

CHANNEL_LAYERS = {
	"default": {
		"BACKEND": "channels_redis.core.RedisChannelLayer",
		"CONFIG": {"hosts": [("127.0.0.1", 6379)]},
	},
}


# django-silk

INSTALLED_APPS.append("silk")  # noqa: F405
MIDDLEWARE.insert(0, "silk.middleware.SilkyMiddleware")  # noqa: F405


# oscar

OSCAR_URL_SCHEMA = "https"


# wagtail

WAGTAILADMIN_BASE_URL = OSCAR_URL_SCHEMA + "://www.gameonlock.com"


HAYSTACK_CONNECTIONS = {
	"default": {
		"ENGINE": "haystack.backends.solr_backend.SolrEngine",
		"URL": os.getenv("SOLR_URL"),
		"INCLUDE_SPELLING": True,
	},
}

# django-allauth

ACCOUNT_DEFAULT_HTTP_PROTOCOL = "HTTPS"
