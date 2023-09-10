from django.db import models

from modelcluster.fields import ParentalKey

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index


class SportsPage(Page):
	body = RichTextField(blank=True)
	
	content_panels = Page.content_panels + [
		FieldPanel('body', classname='full')
	]

class TicketOrderPage(Page):
	body = RichTextField(blank=True)
	
	content_panels = Page.content_panels + [
		FieldPanel('body', classname='full')
	]
