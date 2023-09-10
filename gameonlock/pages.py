from django.db import models

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailmetadata.models import MetadataPageMixin

from blog.models import BlogPage


class HomePage(MetadataPageMixin, Page):
	body = RichTextField(blank=True)
	background = models.ForeignKey(
		'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+', blank=True, null=True
	)
	
	content_panels = Page.content_panels + [
		FieldPanel('body', classname='full'),
		ImageChooserPanel('background'),
	]
	
	def get_context(self, request):
		context = super().get_context(request)
		blogpages = BlogPage.objects.all().live().order_by('-first_published_at')[:3]
		context['blogpages'] = blogpages
		return context


class GenericPage(MetadataPageMixin, Page):
	body = RichTextField(blank=True)
	background = models.ForeignKey(
		'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+', blank=True, null=True
	)
	
	content_panels = Page.content_panels + [
		FieldPanel('body', classname='full'),
		ImageChooserPanel('background'),
	]


class SportsbookLoginPage(MetadataPageMixin, Page):
	background = models.ForeignKey(
		'wagtailimages.Image', on_delete=models.SET_NULL, related_name='+', blank=True, null=True
	)
	
	content_panels = Page.content_panels + [
		ImageChooserPanel('background'),
	]
