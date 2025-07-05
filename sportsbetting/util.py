import logging

from django.conf import settings

from .models import Play

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
