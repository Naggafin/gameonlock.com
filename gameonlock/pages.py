from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import models
from puput.abstracts import BlogAbstract
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

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
