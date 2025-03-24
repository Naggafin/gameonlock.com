import csv
import logging
from io import StringIO
from typing import Optional

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import (
	BettingLine,
	GoverningBody,
	Play,
	ScheduledGame,
	Sport,
	Team,
)

logger = logging.getLogger(__name__)


def calculate_play_stakes(obj: Play) -> int:
	num_picks = len(obj.picks.all())
	return obj.amount * int(
		settings.SPORTS["BASE_BET_STAKES"]
		+ ((num_picks - settings.SPORTS["MIN_NUM_BETS"]) / settings.SPORTS["BET_STEP"])
		* settings.SPORTS["BET_MULTIPLIER"]
	)


def get_sport(sport_id_or_name: str, request: HttpRequest) -> Optional[Sport]:
	"""Retrieve a Sport instance by ID or name."""
	try:
		return Sport.objects.filter(
			Q(id=sport_id_or_name) | Q(name__iexact=sport_id_or_name)
		).get()
	except Sport.DoesNotExist:
		messages.error(
			request,
			_("Error: Could not find sport '%s' in the database.") % sport_id_or_name,
		)
		logger.error("Sport '%s' not found", sport_id_or_name)
		raise


def get_governing_body(
	governing_body_id_or_name: str, request: HttpRequest
) -> Optional[GoverningBody]:
	"""Retrieve a GoverningBody instance by ID or name."""
	try:
		return GoverningBody.objects.filter(
			Q(id=governing_body_id_or_name) | Q(name__iexact=governing_body_id_or_name)
		).get()
	except GoverningBody.DoesNotExist:
		messages.error(
			request,
			_("Error: Could not find governing body '%s' in the database.")
			% governing_body_id_or_name,
		)
		logger.error("GoverningBody '%s' not found", governing_body_id_or_name)
		raise


def parse_commence_time(
	commence_time_str: str, line: int, request: HttpRequest
) -> Optional[timezone.datetime]:
	"""Parse the commence_time string into a datetime object."""
	try:
		return timezone.datetime.fromisoformat(commence_time_str)
	except ValueError:
		messages.error(
			request,
			_(
				"Error: Invalid commence_time on line %d (got '%s', expected ISO format like '2011-11-04T00:05:23')."
			)
			% (line, commence_time_str),
		)
		logger.error("Invalid commence_time '%s' on line %d", commence_time_str, line)
		raise


def parse_spread(
	spread: str, line: int, request: HttpRequest
) -> tuple[Optional[int], bool]:
	"""Parse the spread value and determine if it's a pick."""
	if not spread:
		return None, False  # Default if no spread provided
	try:
		if spread.lower().startswith("p"):
			return int(spread[1:]), True
		return int(spread), False
	except ValueError:
		messages.error(
			request,
			_(
				"Error: Invalid spread on line %d (got '%s', expected integer or 'P' followed by integer)."
			)
			% (line, spread),
		)
		logger.error("Invalid spread '%s' on line %d", spread, line)
		raise


def parse_over_under(
	over: str, under: str, line: int, request: HttpRequest
) -> tuple[Optional[int], Optional[int]]:
	"""Parse over and under values."""
	try:
		over_value = int(over) if over else None
		under_value = int(under) if under else None
		if bool(over_value) != bool(under_value):
			raise ValueError(_("Both over and under must be provided or neither."))
		if (over_value and under_value) and under_value > over_value:
			raise ValueError(_("Over value is less than the under value."))
		return over_value, under_value
	except ValueError:
		messages.error(
			request,
			_(
				"Error: Invalid over/under on line %d (got over='%s', under='%s', expected integers)."
			)
			% (line, over, under),
		)
		logger.error("Invalid over/under '%s'/'%s' on line %d", over, under, line)
		raise


@transaction.atomic
def process_uploaded_ticket(request: HttpRequest) -> None:
	"""
	Process a CSV file uploaded via request to create or update ScheduledGame and BettingLine records.

	Args:
		request: The HTTP request containing the uploaded CSV file.
	"""
	uploaded_file = request.FILES.get("file")
	if not uploaded_file:
		messages.error(request, _("No file uploaded."))
		return

	try:
		# Read the uploaded file into memory as a string
		file_content = uploaded_file.read().decode("utf-8")

		# Parse CSV using StringIO
		with StringIO(file_content) as source:
			reader = csv.DictReader(source)
			for line, row in enumerate(reader, start=1):
				try:
					# Extract and validate required fields
					sport_id_or_name = row["sport"].strip()
					governing_body_id_or_name = row["governing_body"].strip()
					home_team_name = row["home_team"].strip().title()
					away_team_name = row["away_team"].strip().title()
					spread = row.get("spread", "").strip()
					over = row.get("over", "").strip()
					under = row.get("under", "").strip()
					commence_time_str = row["commence_time"].strip()

					# Validate critical fields
					if not all(
						[
							sport_id_or_name,
							governing_body_id_or_name,
							home_team_name,
							away_team_name,
							commence_time_str,
						]
					):
						raise KeyError("Missing required field")
					if not (spread or (over and under)):
						raise ValueError("Spread or over/under must be provided")

					sport = get_sport(sport_id_or_name, request)
					governing_body = get_governing_body(
						governing_body_id_or_name, request
					)

					home_team = Team.objects.get_or_create(
						name=home_team_name, governing_body=governing_body
					)[0]
					away_team = Team.objects.get_or_create(
						name=away_team_name, governing_body=governing_body
					)[0]

					commence_time = parse_commence_time(
						commence_time_str, line, request
					)

					scheduled_game = ScheduledGame.objects.update_or_create(
						sport=sport,
						governing_body=governing_body,
						home_team=home_team,
						away_team=away_team,
						start_datetime__date=commence_time.date(),
						defaults={"start_datetime": commence_time},
					)[0]

					spread_value, is_pick = parse_spread(spread, line, request)
					over_value, under_value = parse_over_under(
						over, under, line, request
					)

					# Create or update BettingLine
					BettingLine.objects.update_or_create(
						game=scheduled_game,
						defaults={
							"spread": spread_value,
							"is_pick": is_pick,
							"over": over_value,
							"under": under_value,
							"start_datetime": commence_time,
						},
					)

				except KeyError as e:
					messages.error(
						request,
						_("Error: Missing '%s' on line %d.") % (e.args[0], line),
					)
					logger.error("Missing field %s on line %d", e.args[0], line)
					raise
				except ValueError as e:
					messages.error(request, str(e))
					logger.error("Validation error on line %d: %s", line, str(e))
					raise

	except UnicodeDecodeError:
		messages.error(request, _("Error: File must be a valid UTF-8 encoded CSV."))
		logger.exception("UnicodeDecodeError while processing uploaded file")
		raise
	except Exception as e:
		messages.error(request, _("Error: Unable to process the uploaded file."))
		logger.exception("Unexpected error processing uploaded file: %s", str(e))
		raise
