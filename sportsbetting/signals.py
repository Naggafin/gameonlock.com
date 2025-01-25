from smtplib import SMTPException

from django.conf import settings
from django.core.mail import send_mail
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED

from .models import TicketPlay


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
