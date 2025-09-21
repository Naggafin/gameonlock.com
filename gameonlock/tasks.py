# blog/tasks.py
from celery import shared_task
from django.utils import timezone
from wagtail.models import Page
from wagtailnewsletter.utils import send_campaign

from .models import MonthlyDigestPage


@shared_task
def generate_and_send_monthly_digest():
	today = timezone.now()
	year = today.year
	month = today.month - 1 or 12
	if month == 12:
		year -= 1

	digest, entries = MonthlyDigestPage.generate_for_month(year, month)
	if not digest:
		return "No entries to include in digest."

	# Render and save digest
	html = digest.render_digest(entries)

	# Publish under a NewsletterIndexPage
	parent = Page.objects.type(MonthlyDigestPage.parent_page_types[0]).first()
	parent.add_child(instance=digest)
	digest.save_revision().publish()

	# Send newsletter campaign
	send_campaign(digest, subject=digest.title, content=html)

	return f"Digest for {month}/{year} sent with {entries.count()} entries."
