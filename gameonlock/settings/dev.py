import os

from dotenv import load_dotenv

from .base import *

load_dotenv()


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

PAYPAL_TEST = True
PAYPAL_RECEIVER_EMAIL = os.environ.get("DEBUG_PAYPAL_RECEIVER_EMAIL")

try:
	from .local import *
except ImportError:
	pass
