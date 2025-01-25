import datetime

from cachetools import TTLCache
from django.conf import settings

_cache = TTLCache(maxsize=10000, ttl=datetime.timedelta(days=1).total_seconds())


def site_ui(request):
	return settings.SITE_UI_VARS
