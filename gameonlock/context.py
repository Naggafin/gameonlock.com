from django.conf import settings
from django.middleware import csrf
from django.urls import reverse


def site_vars(request):
	context = settings.SITE_VARS
	context["alert_config"] = {"SSE_URL": "/sse/notifications/"}
	context["bet_slip_config"] = {
		"CSRF_TOKEN": csrf.get_token(request),
		"LOGIN_URL": reverse("account_login"),
		"SUBMIT_URL": reverse("sportsbetting:play_create"),
		"IS_AUTHENTICATED": request.user.is_authenticated,
	}
	return context
