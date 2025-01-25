from .base import *

DEBUG = False

PAYPAL_TEST = False
PAYPAL_RECEIVER_EMAIL = "gameonlockinc@gmail.com"

ALLOWED_HOSTS = [
	"www.gameonlock.com",
	"gameonlock.com",
]

try:
	from .local import *
except ImportError:
	pass
