import logging
from datetime import timedelta

from allauth.account.views import (
	LoginView as AllauthLoginView,
	SignupView as AllauthSignupView,
)
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.functional import SimpleLazyObject
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django_contact_form._akismet import _try_get_akismet_client
from django_contact_form.views import ContactFormView
from django_contact_form.forms import AkismetContactForm
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from honeypot.decorators import check_honeypot

from golpayment.filters import TransactionFilter
from golpayment.models import Transaction
from golpayment.tables import TransactionTable
from sportsbetting.filters import PlayFilter
from sportsbetting.models import Game, Play
from sportsbetting.tables import BetHistoryTable
from sportsbetting.util import get_plays_with_grouped_picks
from sportsbetting.views.mixins import SportsBettingContextMixin

from ..forms import get_all_region_choices
from .mixins import DashboardContextMixin, GameonlockMixin

HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT = 5

logger = logging.getLogger(__name__)


def serialize_form(form):
	form_data = {"errors": list(form.non_field_errors())}
	for field in form:
		form_data[field.name] = {"value": field.value(), "errors": list(field.errors)}
	return form_data


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


@method_decorator(check_honeypot, name="post")
class ContactView(GameonlockMixin, ContactFormView):
	title = _("Contact Us")
	subtitle = _("Get in touch by simply dropping a message")
	success_url = reverse_lazy("contact")
	template_name = "peredion/contact.html"

	def get_form_class(self):
		try:
			if not _try_get_akismet_client():
				raise ImproperlyConfigured
			return AkismetContactForm
		except ImproperlyConfigured:
			return super().get_form_class()

	def get_form(self, form_class=None):
		form = super().get_form(form_class=form_class)
		form.template_name = "peredion/forms/contact_form.html"
		return form

	def form_valid(self, form):
		response = super().form_valid(form)  # still send the email, etc.
		messages.success(self.request, _("Submission received!") + " &#x1F389;")
		if self.request.htmx:
			response = HttpResponse(status=204)
			response["HX-Trigger"] = "contactSuccess"
		return response

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("contact"))]


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

		form = context["form"]
		context["signup_config"] = {
			"REGIONS": dict(get_all_region_choices()),
			"SIGNUP_URL": reverse("account_signup"),
			"FORM": serialize_form(form),
		}
		return context


class DashboardView(
	LoginRequiredMixin, DashboardContextMixin, GameonlockMixin, TemplateView
):
	title = _("Dashboard")
	template_name = "peredion/dashboard/index.html"

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("dashboard"))]

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		user_plays = self.request.user.plays

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
			"wins": [],
			"losses": [],
			"profit": [],
		}

		for day in week_days:
			stats = stats_by_date.get(day, {})
			chart_data["wins"].append(stats.get("wins", 0))
			chart_data["losses"].append(stats.get("losses", 0))
			chart_data["profit"].append(float(stats.get("profit", 0) or 0))

		context["chart_data"] = chart_data
		return context


class PlayHistoryView(
	LoginRequiredMixin,
	DashboardContextMixin,
	GameonlockMixin,
	SingleTableMixin,
	FilterView,
):
	title = _("Bet History")
	model = Play
	table_class = BetHistoryTable
	filterset_class = PlayFilter
	table_pagination = {"per_page": 10}
	template_name = "peredion/dashboard/dashboard-bet-history.html"

	def get_template_names(self):
		if self.request.htmx:
			return ["django_tables2/table_fragment.html"]
		return super().get_template_names()

	def get_queryset(self):
		queryset = (
			super()
			.get_queryset()
			.filter(user=self.request.user)
			.prefetch_related(
				"picks__betting_line__game__home_team",
				"picks__betting_line__game__away_team",
			)
		)
		return queryset

	def get_table_data(self):
		data = super().get_table_data()
		return get_plays_with_grouped_picks(data)

	@property
	def crumbs(self):
		return [('<span class="text">%s</span>' % self.title, reverse("play_history"))]


class TransactionHistoryView(
	LoginRequiredMixin,
	DashboardContextMixin,
	GameonlockMixin,
	SingleTableMixin,
	FilterView,
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


class SettingsView(
	LoginRequiredMixin, DashboardContextMixin, GameonlockMixin, TemplateView
):
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
