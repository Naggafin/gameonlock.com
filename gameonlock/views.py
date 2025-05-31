import logging

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django_tables2 import SingleTableMixin

from golpayment.models import Transaction
from sportsbetting.models import Game, Play
from sportsbetting.views import SportsBettingContextMixin

from .filters import BetHistoryFilter, TransactionHistoryFilter
from .tables import BetHistoryTable, TransactionHistoryTable

HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT = 5

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
            lambda: Game.objects.select_related("home_team", "away_team").filter(
                start_datetime__gt=timezone.now()
            )[:3]
        )
        return context


class DashboardView(SingleTableMixin, View):
    template_name = "peredion/dashboard/index.html"

    def get(self, request, *args, **kwargs):
        if request.htmx:  # Handle HTMX requests
            table_name = request.GET.get("table")  # e.g., 'bet_history'
            if table_name == "bet_history":
                queryset = Play.objects.filter(user=request.user)
                filterset = BetHistoryFilter(request.GET, queryset=queryset)
                table = BetHistoryTable(filterset.qs)
                table.paginate(page=request.GET.get("page", 1), per_page=10)
                return render(
                    request,
                    "peredion/dashboard/partials/bet_history_table.html",
                    {"table": table},
                )
            elif table_name == "transaction_history":
                queryset = Transaction.objects.filter(user=request.user)
                filterset = TransactionHistoryFilter(request.GET, queryset=queryset)
                table = TransactionHistoryTable(filterset.qs)
                table.paginate(page=request.GET.get("page", 1), per_page=10)
                return render(
                    request,
                    "peredion/dashboard/partials/transaction_history_table.html",
                    {"table": table},
                )
        else:  # Initial full page load
            bet_queryset = Play.objects.filter(user=request.user)
            bet_filter = BetHistoryFilter(request.GET, queryset=bet_queryset)
            bet_table = BetHistoryTable(bet_filter.qs)

            transaction_queryset = Transaction.objects.filter(user=request.user)
            transaction_filter = TransactionHistoryFilter(
                request.GET, queryset=transaction_queryset
            )
            transaction_table = TransactionHistoryTable(transaction_filter.qs)

            context = {
                "bet_table": bet_table,
                "transaction_table": transaction_table,
                # Add other context variables as needed (e.g., totals from previous TODOs)
            }
            return render(request, self.template_name, context)


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
