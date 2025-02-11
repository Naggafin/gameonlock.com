import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from sportsbetting.models import Sport

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
		"sports": Sport.objects.all(),
	}
	return render(request, "peredion/index.html", context)
