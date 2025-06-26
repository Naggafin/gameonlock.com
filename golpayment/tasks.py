from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from gameonlock.models import Transaction
from sportsbetting.models import Play


@shared_task
def process_payment_confirmation(txn_id, amount, user_email):
	"""
	Task to process payment confirmation, create transaction record, update play status, and notify admin/user.
	"""
	subject = "Payment Confirmation"
	message = f"Payment of {amount} has been confirmed with transaction ID {txn_id}."
	from_email = settings.DEFAULT_FROM_EMAIL
	recipient_list = [user_email, settings.ADMIN_EMAIL]

	send_mail(subject, message, from_email, recipient_list, fail_silently=False)

	# Create a Transaction record
	try:
		play = Play.objects.get(txn_id=txn_id)
		transaction = Transaction.objects.create(
			transaction_id=txn_id,
			date_time=timezone.now(),
			type="payment",
			amount=amount,
			status="completed",
			user=play.user,  # Link to the user from Play
		)

		# Update the Play status
		play.status = "paid"
		play.save()
	except Play.DoesNotExist:
		# Log or handle the error if the play doesn't exist
		pass

	return f"Payment confirmation sent, transaction created, and play marked as paid for transaction {txn_id}"
