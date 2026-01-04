from datetime import date, timedelta

from django.db.models import Case, CharField, Value, When
from django.utils import timezone

from ..models import BettingLine, Pick
from ..munger import BettingLineMunger


class SportsBettingContextMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		now = timezone.now()
		yesterday = date.today() - timedelta(days=1)
		betting_lines = (
			BettingLine.objects.select_related(
				"game__governing_body__sport",
				"game__governing_body",
				"game__league",
				"game__home_team",
				"game__away_team",
			)
			.annotate(
				segment=Case(
					When(game__start_datetime__gt=now, then=Value("upcoming")),
					When(game__is_finished=True, then=Value("finished")),
					default=Value("in_play"),
					output_field=CharField(),
				)
			)
			.order_by(
				"segment",
				"game__governing_body__sport__name",
				"game__governing_body__name",
				"game__league__name",
				"game__start_datetime",
			)
			.filter(game__start_datetime__date__gte=yesterday)
		)
		picks = Pick.objects.filter(
			betting_line__in=betting_lines,
			play__user_id=self.request.user.pk,
		).only(
			"betting_line_id",
			"type",
			"team_id",
			"is_over",
		)
		munger = BettingLineMunger(betting_lines, picks)
		upcoming_entries, in_play_entries, finished_entries = (
			munger.categorize_and_sort()
		)
		context["upcoming_entries"] = upcoming_entries
		context["in_play_entries"] = in_play_entries
		context["finished_entries"] = finished_entries
		return context
