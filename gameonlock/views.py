import logging

from django.http import JsonResponse
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from sportsbetting.models import ScheduledGame
from sportsbetting.views import SportsBettingContextMixin

HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT = 10

logger = logging.getLogger(__name__)


class HomeView(SportsBettingContextMixin, TemplateView):
	template_name = "peredion/index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		upcoming_entries = context["upcoming_entries"]
		for sport, lines_dict in upcoming_entries.items():
			count = HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT
			tmp = {}
			for key, lines in lines_dict.items():
				tmp[key] = lines[:count]
				count -= len(tmp[key])
				if count == 0:
					break
			upcoming_entries[sport] = tmp
		context["upcoming_entries"] = upcoming_entries
		context["upcoming_games"] = SimpleLazyObject(
			lambda: ScheduledGame.objects.select_related(
				"home_team", "away_team"
			).filter(start_datetime__gt=timezone.now())[:3]
		)
		return context


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
