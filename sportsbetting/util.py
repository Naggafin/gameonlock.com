import logging

from django.conf import settings

from .models import Play

logger = logging.getLogger(__name__)


def calculate_play_stakes(obj: Play) -> int:
	num_picks = len(obj.picks.all())
	return obj.amount * int(
		settings.SPORTS["BASE_BET_STAKES"]
		+ ((num_picks - settings.SPORTS["MIN_NUM_BETS"]) / settings.SPORTS["BET_STEP"])
		* settings.SPORTS["BET_MULTIPLIER"]
	)
