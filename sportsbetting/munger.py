from collections import defaultdict
from typing import Dict, Tuple

from django.utils import timezone


class BettingLineMunger:
	def __init__(self, betting_lines, plays):
		self.betting_lines = betting_lines
		self.picks = defaultdict(dict)
		self.current_time = timezone.now()

		for play in plays:
			for pick in play.picks.all():
				self.picks[pick.betting_line_id][pick.type] = pick

	def categorize_and_sort(self) -> Tuple[Dict, Dict, Dict]:
		entries = defaultdict(lambda: defaultdict())

		for line in self.betting_lines:
			game = line.game
			sport = game.sport
			league = game.league or ""
			governing_body = game.governing_body

			game_date = game.start_datetime.date()
			game_time = game.start_datetime

			line.picked_team = None
			line.picked_uo = None
			picks = self.picks.get(line.pk)
			if picks:
				if pick := picks.get("team"):
					line.picked_team = pick.team_id
				elif pick := picks.get("uo"):
					line.picked_uo = "over" if pick.is_over else "under"

			if game_time > self.current_time:
				entries["upcoming"][sport].setdefault(
					(governing_body, league), []
				).append(line)
			elif game.is_finished or game_date < self.current_time.date():
				entries["finished"][sport].setdefault(
					(governing_body, league), []
				).append(line)
			else:
				entries["in_play"][sport].setdefault(
					(governing_body, league), []
				).append(line)

		# Sort games within each bucket and maintain date order
		for segment in entries:
			_entries = entries[segment]
			for sport in _entries:
				_entries[sport] = dict(sorted(_entries[sport].items()))
				for key in _entries[sport]:
					_entries[sport][key].sort(key=lambda line: line.game.start_datetime)

		return entries["upcoming"], entries["in_play"], entries["finished"]
