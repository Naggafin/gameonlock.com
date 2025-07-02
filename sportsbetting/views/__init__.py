from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView
from view_breadcrumbs.generic import ListBreadcrumbMixin

from gameonlock.views.mixins import GameonlockMixin

from ..forms import PickFormSet, PlayForm
from ..models import BettingLine, Pick, Play
from ..munger import BettingLineMunger
from ..util import calculate_play_stakes
from .mixins import SportsBettingContextMixin


class BettingView(
	LoginRequiredMixin,
	SportsBettingContextMixin,
	ListBreadcrumbMixin,
	GameonlockMixin,
	TemplateView,
):
	title = _("Betting")
	model = BettingLine
	template_name = "peredion/playing-bet.html"
	list_view_url = reverse_lazy("sportsbetting:bet")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["tabs"] = [
			{
				"id": "upcoming",
				"name": "upcoming",
				"num": 1,
				"entries": context["upcoming_entries"],
			},
			{
				"id": "inplay",
				"name": "in-play",
				"num": 2,
				"entries": context["in_play_entries"],
			},
			{
				"id": "finished",
				"name": "finished",
				"num": 3,
				"entries": context["finished_entries"],
			},
		]
		return context


class PlayCreateUpdateView(LoginRequiredMixin, UpdateView):
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
		formset = PickFormSet(
			self.request.POST,
			queryset=Pick.objects.filter(
				play__user_id=self.request.user.pk,
				betting_line__game__start_datetime__gt=timezone.now(),
			)
			if self.object
			else Pick.objects.none(),
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


"""
class PlayDetailView(LoginRequiredMixin, FormMixin, DetailView):
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


class PaymentCompleteView(LoginRequiredMixin, TemplateView):
	template_name = "sportsbetting/payment_complete.html"


class PaymentCancelledView(LoginRequiredMixin, TemplateView):
	template_name = "sportsbetting/payment_cancelled.html"
"""
