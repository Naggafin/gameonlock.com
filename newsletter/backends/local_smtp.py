from django.core.mail import EmailMultiAlternatives
from wagtail_newsletter.backends.base import BaseCampaignBackend


class LocalSMTPBackend(BaseCampaignBackend):
	"""
	Simple backend to send newsletters via Django's EmailBackend (self-hosted SMTP)
	"""

	def send_message(self, subject, from_email, to_list, html_message, text_message):
		for recipient in to_list:
			msg = EmailMultiAlternatives(
				subject=subject,
				body=text_message,
				from_email=from_email,
				to=[recipient],
			)
			msg.attach_alternative(html_message, "text/html")
			msg.send()
