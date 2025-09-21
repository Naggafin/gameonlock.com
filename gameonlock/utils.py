# blog/utils.py
from wagtail.models import Site

from .models import NewsletterIndexPage


def get_or_create_newsletter_index():
	index = NewsletterIndexPage.objects.first()
	if index:
		return index

	# Find root page for the default site
	site = Site.objects.get(is_default_site=True)
	root_page = site.root_page

	# Create the index under the root
	index = NewsletterIndexPage(
		title="Newsletters",
		slug="newsletters",
	)
	root_page.add_child(instance=index)
	index.save_revision().publish()

	return index
