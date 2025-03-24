from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMessage, send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from .models import Play, TicketPlay


@receiver(post_save, sender=Play)
def send_email_confirmation(sender, instance, created, **kwargs):
	if not created or not instance.user.email:
		return

	# Prepare context for the template
	picks = sorted(list(instance.picks.all()), key=lambda obj: obj.type)
	context = {"user": instance.user, "picks": picks}

	# Render the email body from the template
	email_body = render_to_string("emails/play_confirmation.txt", context)

	# Send the email
	EmailMessage(
		subject=_("Your Bets Confirmation"),
		body=email_body,
		to=[instance.user.email],
		from_email=settings.DEFAULT_FROM_EMAIL,
	).send(fail_silently=True)


@receiver(post_save, sender=Play)
def send_admin_notification(sender, instance, created, **kwargs):
	if not created:
		return

	# Prepare context for the template
	picks = sorted(list(instance.picks.all()), key=lambda obj: obj.type)
	context = {"play": instance, "picks": picks}

	# Render the email body from the template
	email_body = render_to_string("emails/admin_play_notification.txt", context)

	# Send the email
	EmailMessage(
		subject=_("New Play"),
		body=email_body,
		to=settings.NOTIFY_EMAILS,
		from_email=settings.DEFAULT_FROM_EMAIL,
	).send(fail_silently=True)


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
	ipn = sender
	if ipn.payment_status == ST_PP_COMPLETED:
		if ipn.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
			# Not a valid payment
			print("PayPal returned an IPN with an incorrect receiver email address")
			return

		# payment was successful
		order = get_object_or_404(TicketPlay, pk=ipn.invoice)
		print(order)
		print(ipn.mc_gross)
		if ipn.mc_gross == order.bet_amount and ipn.mc_currency == "USD":
			# mark the order as paid
			order.paid = True
			order.save()

			email_message = f"Here is your order invoice number: {ipn.invoice}\nWe will notify you by email or text message if your play is a winning one. Good luck!\n"
			email_message += f"\nSincerely,\n{settings.SITE_NAME}\n"

			try:
				send_mail(
					subject="Thanks for your payment!",
					message=email_message,
					from_email=settings.SALES_EMAIL,
					recipient_list=[
						ipn.payer_email,
					],
					fail_silently=False,
					auth_user=settings.SALES_EMAIL_USER,
					auth_password=settings.SALES_EMAIL_PASSWORD,
				)
			except SMTPException:
				print(
					f"Warning: unable to send ticket payment receipt email to {order.email}"
				)
		else:
			print("PayPal returned an IPN with a currency not measured in USD")
