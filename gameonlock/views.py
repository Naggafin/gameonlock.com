import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sportsbetting.models import ScheduledGame, Sport

logger = logging.getLogger(__name__)


@csrf_exempt
def csp_report_view(request):
	if request.method == "POST":
		try:
			# Decode and log the CSP report
			report = request.body.decode("utf-8")
			logger.warning("CSP Violation Report: %s", report)
		except Exception as e:
			logger.error("Failed to process CSP report: %s", e)
	return JsonResponse({"status": "success"})


def home(request):
	context = {
		"sports": Sport.objects.prefetch_related(
			"scheduled_games__betting_lines",
			"governing_bodies__leagues__scheduled_games__betting_lines",
			"governing_bodies__leagues__scheduled_games__home_team",
			"governing_bodies__leagues__scheduled_games__away_team",
		).all(),
		"scheduled_games": ScheduledGame.objects.select_related(
			"home_team", "away_team"
		).all(),
	}
	return render(request, "peredion/index.html", context)
