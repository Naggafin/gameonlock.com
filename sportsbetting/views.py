from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import localdate
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, ListView
from view_breadcrumbs.generic import ListBreadcrumbMixin

from .forms import PlayForm, PlayPickFormSet
from .models import BettingLine, Play, PlayPick
from .munger import BettingLineMunger


class BettingFormView(ListBreadcrumbMixin, FormView):
	model = BettingLine
	template_name = "peredion/playing-bet.html"
	form_class = PlayForm
	list_view_url = reverse_lazy("sportsbetting:betting")

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

	def form_valid(self, form):
		play = form.save(commit=False)
		play.user = self.request.user
		play.save()

		play_picks_formset = PlayPickFormSet(
			self.request.POST,
			queryset=PlayPick.objects.filter(
				play__user_id=self.request.user.pk,
				betting_line__game__start_datetime__gt=timezone.now(),
			),
		)

		if play_picks_formset.is_valid():
			picks = play_picks_formset.save(commit=False)
			for pick in picks:
				pick.play = play
			play_picks_formset.save()
		else:
			messages.error(self.request, _("Error processing picks."))
			return self.form_invalid(form)

		self.send_email_confirmation(play)
		self.send_admin_notification(play)
		return redirect("sportsbetting:play")

	def send_email_confirmation(self, play):
		email_message = f"Dear {play.purchaser_name},\n\nYour picks:\n"
		for pick in play.spread_picks.all():
			email_message += f"{pick}\n"
		for pick in play.under_over_picks.all():
			email_message += f"{pick}\n"
		email_message += "\nPlease complete your payment via PayPal."
		EmailMessage(
			subject="Your Bets Confirmation", body=email_message, to=[play.email]
		).send(fail_silently=True)

	def send_admin_notification(self, play):
		email_message = f"New Play Submitted:\n\n{play}"
		EmailMessage(
			subject=f"New Play for {play.ticket.name}",
			body=email_message,
			to=settings.NOTIFY_EMAILS,
		).send(fail_silently=True)


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
