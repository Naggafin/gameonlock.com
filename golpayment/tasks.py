from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def process_payment_confirmation(txn_id, amount, user_email):
    """
    Task to process payment confirmation and notify admin/user.
    """
    subject = "Payment Confirmation"
    message = f"Payment of {amount} has been confirmed with transaction ID {txn_id}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email, settings.ADMIN_EMAIL]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)

    return f"Payment confirmation sent for transaction {txn_id}"
