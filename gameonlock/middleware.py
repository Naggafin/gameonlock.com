from debug_toolbar.middleware import show_toolbar
from django.contrib.auth.middleware import get_user


def show_toolbar_superuser(request):
	user = get_user(request)
	return show_toolbar(request) or user.is_superuser
