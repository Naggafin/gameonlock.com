from celery import shared_task
from django.utils import timezone
from wagtail_newsletter.models import NewsletterCampaign

from newsletter.models import MonthlyNewsletterPage


@shared_task
def create_and_send_monthly_newsletter():
	# Example: pick the latest newsletter page
	newsletter_page = MonthlyNewsletterPage.objects.live().last()
	if not newsletter_page:
		return "No newsletter page found"

	# Collect posts since last sent
	last_campaign = (
		NewsletterCampaign.objects.filter(page=newsletter_page)
		.order_by("-created_at")
		.first()
	)
	since = last_campaign.sent_at if last_campaign else None
	posts = newsletter_page.get_recent_posts(since=since)

	if not posts.exists():
		return "No new posts since last issue"

	# Create a campaign
	campaign = newsletter_page.create_campaign()
	campaign.subject = f"Monthly Digest - {timezone.now():%B %Y}"
	campaign.save()

	# Attach posts data to campaign context for template rendering
	campaign.extra_context = {"featured": posts.first(), "posts": posts[1:]}
	campaign.save()

	# Send campaign
	campaign.send()
	return f"Newsletter sent to {campaign.recipients.count()} subscribers"
