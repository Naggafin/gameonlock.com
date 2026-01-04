from collections import defaultdict
from typing import Dict, Tuple


class BettingLineMunger:
	def __init__(self, betting_lines, picks):
		self.betting_lines = betting_lines

		# Map: { betting_line_id: { pick_type: pick } }
		self.picks = defaultdict(dict)
		for pick in picks:
			self.picks[pick.betting_line_id][pick.type] = pick

	def categorize_and_sort(self) -> Tuple[Dict, Dict, Dict]:
		entries = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

		for line in self.betting_lines:
			game = line.game
			sport = game.governing_body.sport
			governing_body = game.governing_body
			league = game.league or ""

			# Resolve picks (pure Python, no branching explosion)
			picks = self.picks.get(line.pk)
			line.picked_team = None
			line.picked_uo = None

			if picks:
				team_pick = picks.get("team")
				if team_pick:
					line.picked_team = team_pick.team_id
				else:
					uo_pick = picks.get("uo")
					if uo_pick:
						line.picked_uo = "over" if uo_pick.is_over else "under"

			entries[line.segment][sport][(governing_body, league)].append(line)

			# Sort sports by total number of betting_lines
			for segment, sports in entries.items():
				entries[segment] = dict(
					sorted(
						sports.items(),
						key=lambda pair: sum(len(lines) for lines in pair[1].values()),
						reverse=True,
					)
				)

		return (
			entries["upcoming"],
			entries["in_play"],
			entries["finished"],
		)
