from django.conf import settings


def site_vars(request):
	return settings.SITE_VARS
