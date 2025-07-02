import json
import logging
from datetime import timedelta

from allauth.account.views import (
	LoginView as AllauthLoginView,
	SignupView as AllauthSignupView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import (
	Case,
	Count,
	DecimalField,
	IntegerField,
	Q,
	Sum,
	When,
)
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django_tables2.views import SingleTableMixin

from golpayment.filters import TransactionFilter
from golpayment.models import Transaction
from golpayment.tables import TransactionTable
from sportsbetting.filters import PlayFilter
from sportsbetting.models import Game, Play
from sportsbetting.tables import PlayTable
from sportsbetting.views.mixins import SportsBettingContextMixin

from ..forms import get_all_region_choices
from .mixins import GameonlockMixin

HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT = 5

logger = logging.getLogger(__name__)


class HomeView(SportsBettingContextMixin, GameonlockMixin, TemplateView):
	title = _("Home")
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


class LoginView(GameonlockMixin, AllauthLoginView):
	title = _("Sign In")

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("account_login"))]


class SignupView(GameonlockMixin, AllauthSignupView):
	title = _("Sign Up")

	@property
	def crumbs(self):
		return [
			('<span class="text">%s</span>' % self.title, reverse("account_signup"))
		]

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["subtitle"] = _("Sign up to create an account")
		context["region_choices"] = json.dumps(dict(get_all_region_choices()))
		return context


class DashboardView(LoginRequiredMixin, GameonlockMixin, TemplateView):
	title = _("Dashboard")
	template_name = "peredion/dashboard/index.html"

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("dashboard"))]

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		user_plays = self.request.user.plays

		# Aggregate totals
		totals = user_plays.aggregate(
			total_bets=Count("id"),
			total_wins=Count(Case(When(won=True, then=1), output_field=IntegerField())),
			total_payout=Sum(
				Case(When(won=True, then="amount"), output_field=DecimalField())
			),
		)

		context.update(
			{
				"total_bets": totals["total_bets"],
				"total_wins": totals["total_wins"],
				"total_payout": totals["total_payout"] or "0.00",
			}
		)

		# Prepare week range
		today = timezone.now().date()
		week_start = today - timedelta(days=today.weekday())
		week_days = [week_start + timedelta(days=i) for i in range(7)]

		# Weekly grouped stats in one query
		weekly_stats = (
			user_plays.filter(
				placed_datetime__date__range=(week_start, week_days[-1]),
				status=Play.STATES.completed,
			)
			.values("placed_datetime__date")
			.annotate(
				wins=Count("id", filter=Q(won=True)),
				losses=Count("id", filter=Q(won=False)),
				profit=Sum("amount", filter=Q(won=True)),
			)
		)

		# Map stats by date for O(1) lookup
		stats_by_date = {
			entry["placed_datetime__date"]: entry for entry in weekly_stats
		}

		# Fill chart data
		chart_data = {
			"chart_wins": [],
			"chart_losses": [],
			"chart_profit": [],
		}

		for day in week_days:
			stats = stats_by_date.get(day, {})
			chart_data["chart_wins"].append(stats.get("wins", 0))
			chart_data["chart_losses"].append(stats.get("losses", 0))
			chart_data["chart_profit"].append(float(stats.get("profit", 0) or 0))

		context["chart_data"] = json.dumps(chart_data)
		return context


class PlayHistoryView(
	LoginRequiredMixin, GameonlockMixin, SingleTableMixin, FilterView
):
	title = _("Bet History")
	model = Play
	table_class = PlayTable
	filterset_class = PlayFilter
	table_pagination = {"per_page": 10}
	template_name = "peredion/dashboard/dashboard-bet-history.html"

	def get_template_names(self):
		if self.request.htmx:
			return ["django_tables2/table_fragment.html"]
		return super().get_template_names()

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("play_history"))]


class TransactionHistoryView(
	LoginRequiredMixin, GameonlockMixin, SingleTableMixin, FilterView
):
	title = _("Transaction History")
	model = Transaction
	table_class = TransactionTable
	filterset_class = TransactionFilter
	table_pagination = {"per_page": 10}
	template_name = "peredion/dashboard/dashboard-transaction-history.html"

	def get_template_names(self):
		if self.request.htmx:
			return ["django_tables2/table_fragment.html"]
		return super().get_template_names()

	@property
	def crumbs(self):
		return [
			(
				'<span class="text">%s</span>' % self.title,
				reverse("transaction_history"),
			)
		]


class SettingsView(LoginRequiredMixin, GameonlockMixin, TemplateView):
	title = _("Settings")
	template_name = "peredion/dashboard/dashboard-settings.html"

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("settings"))]


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
