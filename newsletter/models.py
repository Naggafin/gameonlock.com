from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail_newsletter.models import NewsletterCampaignMixin


class MonthlyNewsletterPage(Page, NewsletterCampaignMixin):
	intro = RichTextField(blank=True)

	content_panels = (
		Page.content_panels
		+ [
			# additional fields if needed
		]
	)

	# You can define custom methods to pull recent blog posts
	def get_recent_posts(self, since=None):
		from blog.models import BlogPage

		qs = BlogPage.objects.live()
		if since:
			qs = qs.filter(first_published_at__gt=since)
		return qs.order_by("-first_published_at")
