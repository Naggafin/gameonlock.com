from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, TemplateView, UpdateView
from view_breadcrumbs.generic import ListBreadcrumbMixin

from .forms import PlayForm, PlayPickFormSet
from .models import BettingLine, Play, PlayPick, ScheduledGame
from .munger import BettingLineMunger
from .util import calculate_play_stakes


class SportsBettingContextMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		betting_lines = BettingLine.objects.select_related("game__sport").filter(
			start_datetime__gt=timezone.now()
		)
		plays = Play.objects.prefetch_related("picks").get(
			purchaser=self.request.user, date__gte=localdate()
		)
		munger = BettingLineMunger(betting_lines, plays)
		upcoming_entries, in_play_entries, finished_entries = (
			munger.categorize_and_sort()
		)
		context["upcoming_entries"] = upcoming_entries
		context["in_play_entries"] = in_play_entries
		context["finished_entries"] = finished_entries
		return context


class HomeView(SportsBettingContextMixin, TemplateView):
	template_name = "peredion/index.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["upcoming_games"] = ScheduledGame.objects.select_related(
			"home_team", "away_team"
		).filter(start_datetime__gt=timezone.now())
		return context


class BettingView(SportsBettingContextMixin, ListBreadcrumbMixin, TemplateView):
	model = BettingLine
	template_name = "peredion/playing-bet.html"
	list_view_url = reverse_lazy("sportsbetting:bet")


class PlayCreateUpdateView(UpdateView):
	model = Play
	form_class = PlayForm
	success_url = reverse_lazy("sportsbetting:play_list")

	def get(self, request, *args, **kwargs):
		return redirect("sportsbetting:bet")

	def get_object(self, queryset=None):
		try:
			return super().get_object(queryset=queryset)
		except AttributeError:
			return None

	def form_valid(self, form):
		formset = PlayPickFormSet(
			self.request.POST,
			queryset=PlayPick.objects.filter(
				play__user_id=self.request.user.pk,
				betting_line__game__start_datetime__gt=timezone.now(),
			)
			if self.object
			else PlayPick.objects.none(),
		)

		if formset.is_valid():
			play = form.save(commit=False)
			play.user = self.request.user
			play.save()

			picks = formset.save(commit=False)
			for pick in picks:
				pick.play = play
			formset.save()

			play.stakes = calculate_play_stakes(play)
			play.save()

			return redirect("sportsbetting:play")
		return self.form_invalid(form, formset)

	def form_invalid(self, form, formset=None):
		messages.error(self.request, _("Error processing picks."))
		return super().form_invalid(form)


class PlayListView(ListBreadcrumbMixin, ListView):
	model = Play


"""
class PlayDetailView(FormMixin, DetailView):
	model = TicketPlay
	form_class = PayPalPaymentsForm
	template_name = "sportsbetting/ticket_order_page.html"
	context_object_name = "play"

	def get_initial(self):
		return {
			"business": settings.PAYPAL_RECEIVER_EMAIL,
			"amount": self.object.bet_amount.quantize(Decimal(".01")),
			"currency_code": "USD",
			"item_name": "GOL Sports Ticket",
			"invoice": self.object.pk,
			"notify_url": self.request.build_absolute_uri(
				reverse_lazy("sportsbetting:paypal-ipn")
			),
			"return_url": self.request.build_absolute_uri(
				reverse_lazy("sportsbetting:payment_complete")
			),
			"cancel_return": self.request.build_absolute_uri(
				reverse_lazy("sportsbetting:payment_cancelled")
			),
			"lc": "EN",
			"no_shipping": "1",
		}


class PaymentCompleteView(TemplateView):
	template_name = "sportsbetting/payment_complete.html"


class PaymentCancelledView(TemplateView):
	template_name = "sportsbetting/payment_cancelled.html"
"""
