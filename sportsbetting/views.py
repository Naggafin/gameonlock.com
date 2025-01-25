from decimal import Decimal

from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, FormView, TemplateView
from django.views.generic.edit import FormMixin
from paypal.standard.forms import PayPalPaymentsForm

from .forms import SpreadPickFormSet, TicketPlayForm, UnderOverPickFormSet
from .models import Ticket, TicketPlay


class IndexView(FormView):
	template_name = "sportsbetting/index.html"
	form_class = TicketPlayForm

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		try:
			ticket = Ticket.objects.filter(
				pub_date__lte=timezone.now().date(), end_date__gte=timezone.now().date()
			).first()
			if not ticket:
				raise Ticket.DoesNotExist

			sports = []
			for sport in ticket.sports.all().order_by("name"):
				gamesets = []
				date = ticket.pub_date
				while date <= ticket.end_date:
					games = ticket.spreads.filter(
						start_datetime__date=date,
						start_datetime__gte=timezone.now(),
						sport=sport,
					)
					if games.exists():
						gamesets.append({"date": date, "games": games})
					date += timezone.timedelta(days=1)

				if gamesets:
					sports.append({"name": sport.name, "gamesets": gamesets})

			context["ticket"] = ticket
			context["sports"] = sports
		except Ticket.DoesNotExist:
			context["ticket"] = None
			context["sports"] = None

		return context

	def form_valid(self, form):
		ticket = get_object_or_404(
			Ticket,
			pk=self.request.POST.get("pk"),
			pub_date__lte=timezone.now().date(),
			end_date__gte=timezone.now().date(),
		)

		play = form.save(commit=False)
		play.ticket = ticket
		play.save()

		# Process formsets
		spread_formset = SpreadPickFormSet(
			self.request.POST, queryset=ticket.spreads.filter(isPreview=False)
		)
		under_over_formset = UnderOverPickFormSet(
			self.request.POST,
			queryset=ticket.under_overs.filter(linked_spread__isPreview=False),
		)

		if spread_formset.is_valid() and under_over_formset.is_valid():
			spread_formset.save(commit=False)
			under_over_formset.save(commit=False)
			spread_formset.save()
			under_over_formset.save()
		else:
			play.delete()
			messages.error(self.request, "Error processing picks.")
			return self.form_invalid(form)

		# Email notifications
		self.send_email_confirmation(play)
		self.send_admin_notification(play)

		self.request.session["play_pk"] = play.pk
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
