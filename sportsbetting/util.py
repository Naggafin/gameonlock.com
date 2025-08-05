import json
import logging

from django.conf import settings

from .models import Play
from .serializers import PickSerializer

logger = logging.getLogger(__name__)


def calculate_play_stakes(obj: Play) -> int:
	picks_count = obj.picks.count()
	sports_cfg = settings.SPORTS

	stakes = (
		sports_cfg["BASE_BET_STAKES"]
		+ ((picks_count - sports_cfg["MIN_NUM_BETS"]) / sports_cfg["BET_STEP"])
		* sports_cfg["BET_MULTIPLIER"]
	)

	return int(obj.amount * stakes)


def get_plays_with_grouped_picks(plays):
	for play in plays:
		grouped_picks = {}
		for pick in play.picks.all():
			betting_line = pick.betting_line
			if betting_line.pk not in grouped_picks:
				grouped_picks[betting_line.pk] = {
					"betting_line": betting_line,
					"picks": [],
				}
			grouped_picks[betting_line.pk]["picks"].append(PickSerializer(pick).data)
		grouped_picks[betting_line.pk]["picks"] = json.dumps(
			grouped_picks[betting_line.pk]["picks"]
		)
		play.grouped_picks = grouped_picks
	return plays
