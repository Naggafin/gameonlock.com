from django.conf import settings
from django.middleware import csrf
from django.urls import reverse
from puput.models import BlogPage


def site_vars(request):
	context = {}
	context["blog"] = (
		BlogPage.objects.first()
	)  # TODO: there must be a better way to reverse url this w/o a lookup every time
	context["alert_config"] = {"SSE_URL": "/sse/notifications/"}
	context["bet_slip_config"] = {
		"minBet": float(settings.SPORTS["MIN_BET"].amount),
		"minNumBets": settings.SPORTS["MIN_NUM_BETS"],
		"baseBetStakes": settings.SPORTS["BASE_BET_STAKES"],
		"betMultiplier": settings.SPORTS["BET_MULTIPLIER"],
		"betStep": settings.SPORTS["BET_STEP"],
		"csrfToken": csrf.get_token(request),
		"loginUrl": reverse("account_login"),
		"submitUrl": reverse("sportsbetting:play_create"),
		"isAuthenticated": request.user.is_authenticated,
	}
	return context
