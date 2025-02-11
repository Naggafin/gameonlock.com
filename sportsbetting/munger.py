from collections import defaultdict
from typing import Dict


class BettingLineMunger:
	def __init__(self, betting_lines, plays):
		self.betting_lines = betting_lines
		self.picks = defaultdict(list)
		for play in plays:
			for pick in play.picks.all():
				self.picks[pick.betting_line_id].append(pick)

	def categorize_and_sort(self) -> Dict:
		categorized_entries = defaultdict(lambda: defaultdict(list))

		for line in self.betting_lines:
			sport = line.game.sport
			game_date = line.game.start_datetime.date()
			categorized_entries[sport][game_date].append(
				(line, self.picks.get(line.pk, []))
			)

		# Sort entries within each date bucket and maintain sorted date order
		for sport in categorized_entries:
			for game_date in categorized_entries[sport]:
				categorized_entries[sport][game_date].sort(
					key=lambda line, picks: line.game.start_datetime
				)
			# Sort dates
			categorized_entries[sport] = dict(
				sorted(categorized_entries[sport].items())
			)

		# Convert to regular dict for better template handling
		return dict(categorized_entries)
