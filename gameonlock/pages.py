from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page

from sportsbetting.models import ScheduledGame, Sport


class HomePage(Page):
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
		# TODO: optimize later
		context["sports"] = Sport.objects.prefetch_related(
			"governing_bodies__leagues__ticket_entries"
		).prefetch_related(
			"governing_bodies__leagues__ticket_entries__home_team",
			"governing_bodies__leagues__ticket_entries__away_team",
		)
		context["scheduled_games"] = ScheduledGame.objects.all()
		return context
