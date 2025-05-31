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
        entries = defaultdict(lambda: defaultdict(dict))

        for line in self.betting_lines:
            game = line.game
            sport = game.sport
            league = game.league or ""
            governing_body = game.governing_body

            line.picked_team = None
            line.picked_uo = None
            picks = self.picks.get(line.pk)
            if picks:
                if pick := picks.get("team"):
                    line.picked_team = pick.team_id
                elif pick := picks.get("uo"):
                    line.picked_uo = "over" if pick.is_over else "under"

            if not game.has_started:
                entries["upcoming"][sport].setdefault(
                    (governing_body, league), []
                ).append(line)
            elif game.is_finished:
                entries["finished"][sport].setdefault(
                    (governing_body, league), []
                ).append(line)
            else:
                entries["in_play"][sport].setdefault(
                    (governing_body, league), []
                ).append(line)

        # Sort games within each bucket and maintain date order
        for segment in entries:
            entries[segment] = dict(
                sorted(entries[segment].items(), key=lambda pair: len(pair[1].values()))
            )
            for sport in entries[segment]:
                entries[segment][sport] = dict(
                    sorted(
                        entries[segment][sport].items(),
                        key=lambda pair: (str(pair[0][0]), str(pair[0][1])),
                    )
                )
                for key in entries[segment][sport]:
                    entries[segment][sport][key].sort(
                        key=lambda line: line.game.start_datetime
                    )

        return (
            dict(entries["upcoming"]),
            dict(entries["in_play"]),
            dict(entries["finished"]),
        )
