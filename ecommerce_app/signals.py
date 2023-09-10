from django.shortcuts import get_object_or_404
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail

from .models import TicketPlay


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
	print(f"payment_notification called with sender {sender} and kwargs {kwargs}")
	ipn = sender
	print(ipn.payment_status)
	if ipn.payment_status == ST_PP_COMPLETED:
		print(ipn.receiver_email)
		if ipn.receiver_email != settings.PAYPAL_RECEIVER_EMAIL:
			# Not a valid payment
			print('PayPal returned an IPN with an incorrect receiver email address')
			return
			
		# payment was successful
		order = get_object_or_404(TicketPlay, pk=ipn.invoice)
		print(order)
		print(ipn.mc_gross)
		if ipn.mc_gross == order.bet_amount and ipn.mc_currency == 'USD':
			# mark the order as paid
			order.paid = True
			order.save()
			
			email_message = f"Here is your order invoice number: {ipn.invoice}\nWe will notify you by email or text message if your play is a winning one. Good luck!\n"
			email_message += f"\nSincerely,\n{settings.SITE_NAME}\n"
			
			try:
				send_mail(
					'Thanks for your payment!',
					email_message,
					settings.DEFAULT_FROM_EMAIL,
					[request.POST.get(email)],
					fail_silently=False,
				)
			except SMTPException:
				print(f"Warning: unable to send ticket payment receipt email to {order.email}")
		else:
			print('PayPal returned an IPN with a currency not measured in USD')
