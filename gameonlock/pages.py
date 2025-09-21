from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from puput.abstracts import BlogAbstract, EntryAbstract
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtail_newsletter.models import NewsletterPageMixin
from wagtailmetadata.models import MetadataPageMixin, WagtailImageMetadataMixin

from gameonlock.views.mixins import GameonlockMixin
from sportsbetting.models import Game
from sportsbetting.views.mixins import SportsBettingContextMixin

HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT = 5


class HomePage(SportsBettingContextMixin, GameonlockMixin, MetadataPageMixin, Page):
	about_title = models.CharField(max_length=255, default="About us", blank=True)
	about_subtitle = models.CharField(
		max_length=255,
		default="We provide the most reliable & legal betting",
		blank=True,
	)
	about_content = RichTextField(
		features=["bold", "italic", "link"], blank=True, default=""
	)

	bet_title = models.CharField(max_length=255, default="Available Bets", blank=True)
	bet_subtitle = models.CharField(
		max_length=255, default="Choose Your Match & Place A Bet", blank=True
	)

	schedule_title = models.CharField(
		max_length=255, default="Next Schedule", blank=True
	)
	schedule_subtitle = models.CharField(
		max_length=255, default="All Upcoming Matches", blank=True
	)

	content_panels = Page.content_panels + [
		# About section
		FieldPanel("about_title"),
		FieldPanel("about_subtitle"),
		FieldPanel("about_content"),
		# Bet section
		FieldPanel("bet_title"),
		FieldPanel("bet_subtitle"),
		# Schedule section
		FieldPanel("schedule_title"),
		FieldPanel("schedule_subtitle"),
	]

	template = "peredion/index.html"

	def get_context(self, request, *args, **kwargs):
		context = super().get_context(request, *args, **kwargs)

		upcoming_entries = context.get("upcoming_entries", {})
		for sport, lines_dict in upcoming_entries.items():
			count = HOMEPAGE_MAX_LINE_ENTRIES_PER_SPORT
			tmp = {}
			for key, lines in lines_dict.items():
				tmp[key] = lines[:count]
				count -= len(tmp[key])
				if count == 0:
					break
			upcoming_entries[sport] = tmp

		context.update(
			{
				"home_page": self,
				"upcoming_entries": upcoming_entries,
				"upcoming_games": SimpleLazyObject(
					lambda: Game.objects.select_related(
						"home_team", "away_team"
					).filter(start_datetime__gt=timezone.now())[:3]
				),
			}
		)

		return context


class BlogPageAbstract(BlogAbstract):
	def get_context(self, request, *args, **kwargs):
		context = super().get_context(*args, **kwargs)

		paginator = Paginator(self.entries, 10)
		page = request.GET.get("page")
		try:
			page_obj = paginator.page(page)
		except PageNotAnInteger:
			page_obj = paginator.page(1)
		except EmptyPage:
			page_obj = paginator.page(paginator.num_pages)

		# window size
		current = page_obj.number
		total = paginator.num_pages
		window = 3  # how many pages to show above/below current

		# Build range
		start = max(current - window, 1)
		end = min(current + window, total) + 1
		page_range = range(start, end)

		context.update(
			{
				"page_obj": page_obj,
				"page_range": page_range,
			}
		)

		return context

	class Meta:
		abstract = True


class EntryPageAbstract(NewsletterPageMixin, WagtailImageMetadataMixin, EntryAbstract):
	class Meta:
		abstract = True


class NewsletterIndexPage(Page):
	"""
	An index page to hold all newsletter (digest) pages.
	"""

	subpage_types = ["gameonlock.MonthlyDigestPage"]  # only allow digests inside

	parent_page_types = ["wagtailcore.Page"]  # can live at the root, or under HomePage

	# Optionally, add some context if you want a frontend listing
	def get_context(self, request):
		context = super().get_context(request)
		context["digests"] = self.get_children().live().order_by("-first_published_at")
		return context


class MonthlyDigestPage(NewsletterPageMixin, Page):
	"""
	A digest page that aggregates all blog posts for a given month
	and can be sent as a newsletter via wagtail-newsletter.
	"""

	month = models.PositiveSmallIntegerField()
	year = models.PositiveSmallIntegerField()

	# Auto-populated field with rendered HTML (optional)
	compiled_html = models.TextField(blank=True, editable=False)

	parent_page_types = ["gameonlock.NewsletterIndexPage"]

	@classmethod
	def generate_for_month(cls, year, month):
		"""
		Factory method that builds a MonthlyDigestPage for the given month.
		"""
		from puput.models import EntryPage

		start = timezone.datetime(year, month, 1, tzinfo=timezone.utc)
		if month == 12:
			end = timezone.datetime(year + 1, 1, 1, tzinfo=timezone.utc)
		else:
			end = timezone.datetime(year, month + 1, 1, tzinfo=timezone.utc)

		entries = EntryPage.objects.live().filter(
			first_published_at__gte=start, first_published_at__lt=end
		)

		if not entries.exists():
			return None, entries

		# Create digest page
		title = f"Monthly Digest - {start.strftime('%B %Y')}"
		digest = cls(
			title=title,
			slug=f"digest-{year}-{month}",
			month=month,
			year=year,
		)
		return digest, entries

	def render_digest(self, entries):
		"""
		Render digest MJML template with given entries into HTML.
		"""
		html = render_to_string(
			"newsletters/digest.mjml",
			{
				"digest": self,
				"entries": entries,
			},
		)
		self.compiled_html = html
		return html
