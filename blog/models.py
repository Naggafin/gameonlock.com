from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from taggit.models import TaggedItemBase
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.models import Page
from wagtail.snippets.models import register_snippet


class BlogIndexPage(Page):
	template = "peredion/blog-posts.html"

	subpage_types = ["blog.BlogPage"]  # only allows BlogPages under it
	parent_page_types = ["wagtailcore.Page"]

	def get_context(self, request, *args, **kwargs):
		context = super().get_context(request, *args, **kwargs)
		posts = BlogPage.objects.child_of(self).live().order_by("-date")

		# Category filtering
		category_slug = request.GET.get("category")
		if category_slug:
			posts = posts.filter(category__slug=category_slug)

		# Tag filtering
		tag = request.GET.get("tag")
		if tag:
			posts = posts.filter(tags__name=tag)

		# Search filtering
		search_query = request.GET.get("q")
		if search_query:
			posts = posts.search(search_query)

		context["search_query"] = search_query

		# Pagination
		paginator = Paginator(posts, 10)
		page = request.GET.get("page")
		try:
			posts = paginator.page(page)
		except PageNotAnInteger:
			posts = paginator.page(1)
		except EmptyPage:
			posts = paginator.page(paginator.num_pages)

		# window size
		current = posts.number
		total = paginator.num_pages
		window = 2  # how many pages to show above/below current

		# Build range
		start = max(current - window, 1)
		end = min(current + window, total) + 1
		page_range = range(start, end)

		context.update(
			{
				"posts": posts,
				"page_range": page_range,
			}
		)

		# Faceted categories
		categories = BlogCategory.objects.annotate(
			post_count=Count("blogpage", filter=models.Q(blogpage__live=True))
		)[:5]
		context["categories"] = categories

		# Faceted tags
		tags = (
			Tag.objects.filter(blogpage__isnull=False)
			.annotate(
				post_count=Count("blogpage", filter=models.Q(blogpage__live=True))
			)
			.order_by("-post_count")[:20]
		)
		context["tags"] = tags

		return context


class BlogPageTag(TaggedItemBase):
	content_object = ParentalKey(
		"BlogPage", related_name="tagged_items", on_delete=models.CASCADE
	)


@register_snippet
class BlogCategory(models.Model):
	name = models.CharField(max_length=255, unique=True)
	slug = models.SlugField(max_length=80, unique=True)

	panels = [FieldPanel("name"), FieldPanel("slug")]

	def __str__(self):
		return self.name


class BlogPage(Page):
	template = "peredion/blog-details.html"

	author = models.CharField(max_length=255)
	category = models.CharField(max_length=100, blank=True)
	date = models.DateField(_("post date"))
	intro = models.TextField(blank=True)
	body = RichTextField(features=["bold", "italic", "link", "image", "ul", "ol", "hr"])
	header_image = models.ForeignKey(
		"wagtailimages.Image",
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="+",
	)
	categories = ParentalManyToManyField("blog.BlogCategory", blank=True)
	tags = ParentalManyToManyField("taggit.Tag", blank=True)

	content_panels = Page.content_panels + [
		FieldPanel("author"),
		FieldPanel("category"),
		FieldPanel("date"),
		FieldPanel("intro"),
		FieldPanel("body"),
		FieldPanel("categories", widget=models.CheckboxSelectMultiple),
		FieldPanel("tags"),
		ImageChooserPanel("header_image"),
	]
