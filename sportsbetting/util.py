import json
import logging
from collections import defaultdict

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


def get_plays_with_grouped_picks(plays_queryset):
	for play in plays_queryset:
		grouped_picks = defaultdict(lambda: {"betting_line": None, "picks": []})

		for pick in play.picks.all():
			bl_id = pick.betting_line_id
			if grouped_picks[bl_id]["betting_line"] is None:
				grouped_picks[bl_id]["betting_line"] = pick.betting_line
			grouped_picks[bl_id]["picks"].append(PickSerializer(pick).data)

		for group in grouped_picks.values():
			group["picks"] = json.dumps(group["picks"])

		play.grouped_picks = dict(grouped_picks)

	return plays_queryset
