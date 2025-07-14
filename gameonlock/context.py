from django.conf import settings
from django.middleware import csrf
from django.urls import reverse


def site_vars(request):
	context = settings.SITE_VARS
	context["alert_config"]["SSE_URL"] = "/sse/notifications/"
	context["bet_slip_config"]["CSRF_TOKEN"] = csrf.get_token(request)
	context["bet_slip_config"]["LOGIN_URL"] = reverse("account_login")
	context["bet_slip_config"]["SUBMIT_URL"] = reverse("sportsbetting:play_create")
	context["bet_slip_config"]["IS_AUTHENTICATED"] = request.user.is_authenticated
	return context
