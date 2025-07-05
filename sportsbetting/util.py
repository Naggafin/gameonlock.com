import logging

from django.conf import settings
from django.db.models import Count, ExpressionWrapper, F, FloatField, Value
from django.db.models.functions import Coalesce

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


def calculate_all_total_stakes(plays_qs):
	sports_cfg = settings.SPORTS

	annotated_qs = plays_qs.annotate(
		picks_count=Count("picks"),
		stake_factor=ExpressionWrapper(
			Value(sports_cfg["BASE_BET_STAKES"])
			+ ((F("picks_count") - sports_cfg["MIN_NUM_BETS"]) / sports_cfg["BET_STEP"])
			* sports_cfg["BET_MULTIPLIER"],
			output_field=FloatField(),
		),
		stake_amount=ExpressionWrapper(
			F("amount") * F("stake_factor"), output_field=FloatField()
		),
	)

	total_stake = annotated_qs.aggregate(
		total_stake_sum=Coalesce(Sum("stake_amount"), 0.0)
	)["total_stake_sum"]

	return int(total_stake)
