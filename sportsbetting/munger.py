from collections import OrderedDict, defaultdict
from typing import Dict, Tuple

from django.utils import timezone


class BettingLineMunger:
	def __init__(self, betting_lines, plays):
		self.betting_lines = betting_lines
		self.picks = defaultdict(dict)
		self.current_time = timezone.now()
		self.sports = set()

		for play in plays:
			for pick in play.picks.all():
				self.picks[pick.betting_line_id][pick.type] = pick

	def categorize_and_sort(self) -> Tuple[Dict, Dict, Dict]:
		upcoming_entries = defaultdict(lambda: defaultdict(lambda: OrderedDict()))
		in_play_entries = defaultdict(lambda: defaultdict(lambda: OrderedDict()))
		finished_entries = defaultdict(lambda: defaultdict(lambda: OrderedDict()))

		for line in self.betting_lines:
			game = line.game
			sport = game.sport
			league = game.league
			governing_body = league.governing_body
			self.sports.add(sport)

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
				upcoming_entries[sport][governing_body][league].setdefault(
					game_date, []
				).append(line)
			elif game.is_finished or game_date < self.current_time.date():
				finished_entries[sport][governing_body][league].setdefault(
					game_date, []
				).append(line)
			else:
				in_play_entries[sport][governing_body][league].setdefault(
					game_date, []
				).append(line)

		# Sort upcoming games within each date bucket and maintain date order
		for sport in self.sports:
			if sport in upcoming_entries:
				for governing_body in upcoming_entries[sport]:
					for league in upcoming_entries[sport][governing_body]:
						for game_date in upcoming_entries[sport][league]:
							upcoming_entries[sport][league][game_date].sort(
								key=lambda item: item[0].game.start_datetime
							)
						# Sort the dates and reassign to OrderedDict to maintain order
						upcoming_entries[sport][league] = OrderedDict(
							sorted(upcoming_entries[sport][league].items())
						)

			# Sort in-play games by datetime
			if sport in in_play_entries:
				for governing_body in in_play_entries[sport]:
					for league in in_play_entries[sport][governing_body]:
						for game_date in in_play_entries[sport][league]:
							in_play_entries[sport][league][game_date].sort(
								key=lambda item: item[0].game.start_datetime
							)
						# Sort the dates and reassign to OrderedDict to maintain order
						in_play_entries[sport][league] = OrderedDict(
							sorted(in_play_entries[sport][league].items())
						)

			# Sort finished games by datetime (newest first)
			if sport in finished_entries:
				for governing_body in finished_entries[sport]:
					for league in finished_entries[sport][governing_body]:
						for game_date in finished_entries[sport][league]:
							finished_entries[sport][league][game_date].sort(
								key=lambda item: item[0].game.start_datetime
							)
						# Sort the dates and reassign to OrderedDict to maintain order
						finished_entries[sport][league] = OrderedDict(
							sorted(finished_entries[sport][league].items())
						)

		return upcoming_entries, in_play_entries, finished_entries
