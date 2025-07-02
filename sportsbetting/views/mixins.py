from ..models import BettingLine, Play
from ..munger import BettingLineMunger


class SportsBettingContextMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		betting_lines = BettingLine.objects.select_related(
			"game__governing_body__sport",
			"game__league",
			"game__home_team",
			"game__away_team",
		).all()  # .filter(game__sport__is_active=True)
		plays = Play.objects.prefetch_related("picks").filter(user=self.request.user.pk)
		munger = BettingLineMunger(betting_lines, plays)
		upcoming_entries, in_play_entries, finished_entries = (
			munger.categorize_and_sort()
		)
		context["upcoming_entries"] = upcoming_entries
		context["in_play_entries"] = in_play_entries
		context["finished_entries"] = finished_entries
		return context
