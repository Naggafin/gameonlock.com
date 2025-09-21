from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from django.template.loader import render_to_string
from django.utils import timezone
from puput.abstracts import BlogAbstract, EntryAbstract
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page
from wagtailnewsletter.models import NewsletterPageMixin

from sportsbetting.models import Game, Sport


class HomePage(Page):
	template = "peredion/index.html"

	about_title = models.CharField(
		blank=True,
		default="About us",
		max_length=255,
		help_text="Write a title for the about section",
	)
	about_subtitle = models.CharField(
		blank=True,
		default="We provide the most reliable & legal betting",
		max_length=255,
		help_text="Write a subtitle for the about section",
	)
	about_content = RichTextField(
		blank=True, max_length=255, help_text="Write content for the about section"
	)

	bet_title = models.CharField(
		blank=True,
		default="Available Bets",
		max_length=255,
		help_text="Write a title for the bet section",
	)
	bet_subtitle = models.CharField(
		blank=True,
		default="Choose Your Match & Place A Bet",
		max_length=255,
		help_text="Write a subtitle for the bet section",
	)

	schedule_title = models.CharField(
		blank=True,
		default="Next Schedule",
		max_length=255,
		help_text="Write a title for the schedule section",
	)
	schedule_subtitle = models.CharField(
		blank=True,
		default="All Upcoming Matches",
		max_length=255,
		help_text="Write a subtitle for the schedule section",
	)

	content_panels = Page.content_panels + [
		MultiFieldPanel(
			[
				FieldPanel("about_title"),
				FieldPanel("about_subtitle"),
				FieldPanel("about_content"),
			],
			heading="About section",
		),
		MultiFieldPanel(
			[
				FieldPanel("bet_title"),
				FieldPanel("bet_subtitle"),
			],
			heading="Bet previews section",
		),
		MultiFieldPanel(
			[
				FieldPanel("schedule_title"),
				FieldPanel("schedule_subtitle"),
			],
			heading="Schedule preview section",
		),
	]

	def get_context(self, request):
		context = super().get_context(request)
		context["sports"] = Sport.objects.prefetch_related(
			"governing_bodies__leagues__games__betting_lines",
			"governing_bodies__leagues__games__betting_lines__home_team",
			"governing_bodies__leagues__games__betting_lines__away_team",
		).all()
		context["games"] = Game.objects.prefetch_related("home_team", "away_team").all()
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


class NewsletterEntryAbstract(NewsletterPageMixin, EntryAbstract):
	class Meta:
		abstract = True


class MonthlyDigestPage(NewsletterPageMixin, Page):
	"""
	A digest page that aggregates all blog posts for a given month
	and can be sent as a newsletter via wagtail-newsletter.
	"""

	month = models.PositiveSmallIntegerField()
	year = models.PositiveSmallIntegerField()

	# Auto-populated field with rendered HTML (optional)
	compiled_html = models.TextField(blank=True, editable=False)

	parent_page_types = [
		"wagtailnewsletter.NewsletterIndexPage"
	]  # or your own index page

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
