from collections import defaultdict
from typing import Dict, Tuple

from django.utils import timezone


class BettingLineMunger:
	def __init__(self, betting_lines, plays):
		self.betting_lines = betting_lines
		self.picks = defaultdict(list)
		self.current_time = timezone.now()
		self.sports = set()

		for play in plays:
			for pick in play.picks.all():
				self.picks[pick.betting_line_id].append(pick)

	def categorize_and_sort(self) -> Tuple[Dict, Dict, Dict]:
		upcoming_entries = defaultdict(lambda: defaultdict(list))
		in_play_entries = defaultdict(list)
		finished_entries = defaultdict(list)

		for line in self.betting_lines:
			game = line.game
			sport = game.sport
			self.sports.add(sport)

			game_date = game.start_datetime.date()
			game_time = game.start_datetime

			if game_time > self.current_time:
				# Future games (upcoming)
				upcoming_entries[sport][game_date].append(
					(line, self.picks.get(line.pk, []))
				)
			elif game.is_finished or game_date < self.current_time.date():
				# Past or finished games
				finished_entries[sport].append((line, self.picks.get(line.pk, [])))
			else:
				# Ongoing games (in-play)
				in_play_entries[sport].append((line, self.picks.get(line.pk, [])))

		# Sorting
		for sport in self.sports:
			# Sort upcoming games by date and then time
			if sport in upcoming_entries:
				for game_date in upcoming_entries[sport]:
					upcoming_entries[sport][game_date].sort(
						key=lambda item: item[0].game.start_datetime
					)
				# Sort dates in ascending order
				upcoming_entries[sport] = dict(sorted(upcoming_entries[sport].items()))

			# Sort in-play games by time
			if sport in in_play_entries:
				in_play_entries[sport].sort(
					key=lambda item: item[0].game.start_datetime
				)

			# Sort finished games by time (newest first)
			if sport in finished_entries:
				finished_entries[sport].sort(
					key=lambda item: item[0].game.start_datetime, reverse=True
				)

		# Convert to regular dict for better template handling
		return dict(upcoming_entries), dict(in_play_entries), dict(finished_entries)
