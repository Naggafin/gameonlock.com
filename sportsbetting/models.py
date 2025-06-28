import logging

import auto_prefetch
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from model_utils import Choices
from slugify import slugify

logger = logging.getLogger(__name__)


class Sport(models.Model):
	key = models.CharField(
		max_length=100,
		blank=True,
		null=True,
		editable=False,
		help_text="An identifier for the sport, if provided.",
	)
	name = models.CharField(
		max_length=100,
		unique=True,
		help_text="The unique name of the sport.",
	)
	description = models.TextField(
		blank=True,
		null=True,
		help_text="Optional description of the sport.",
	)
	# is_active = models.BooleanField(default=False, help_text="Check/uncheck to show/hide this sport in the website.")
	slug_name = models.SlugField(
		blank=True,
		null=True,
		editable=False,
		help_text="A unique slug for the sport, if provided.",
	)

	def save(self, *args, **kwargs):
		if not self.slug_name:
			self.slug_name = slugify(self.name)
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.name

	class Meta:
		constraints = [
			models.UniqueConstraint(
				fields=["key"],
				condition=Q(key__isnull=False),
				name="unique_sport_key_when_not_null",
			),
			models.UniqueConstraint(
				fields=["slug_name"],
				condition=Q(slug_name__isnull=False),
				name="unique_slug_name_when_not_null",
			),
		]


class GoverningBody(auto_prefetch.Model):
	TYPES = Choices(
		("pro", "professional", _("Professional")),
		("col", "collegiate", _("Collegiate")),
		("ama", "amateur", _("Amateur")),
		("int", "international", _("International")),
		("clb", "club", _("Club")),
	)

	sport = auto_prefetch.ForeignKey(
		Sport, on_delete=models.CASCADE, related_name="governing_bodies"
	)
	key = models.CharField(
		max_length=100,
		blank=True,
		null=True,
		editable=False,
		help_text="A unique identifier for the governing body, if provided.",
	)
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)
	type = models.CharField(
		max_length=3,
		choices=TYPES,
		verbose_name=_("type of competition"),
	)

	@property
	def full_key(self):
		return f"{self.sport.key}_{self.key}"

	def __str__(self):
		return f"{self.name} ({self.sport.name})"

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("governing body")
		verbose_name_plural = _("governing bodies")
		constraints = [
			models.UniqueConstraint(
				fields=["sport", "key"],
				condition=Q(key__isnull=False),
				name="unique_governing_body_key_when_not_null",
			),
		]


class League(auto_prefetch.Model):
	REGIONS = Choices(
		("wd", "world", _("World-wide")),
		("eu", "europe", _("Europe")),
		("as", "asia", _("Asia")),
		("af", "africa", _("Africa")),
		("na", "north_america", _("North America")),
		("sa", "south_america", _("South America")),
		("oc", "oceania", _("Oceania")),
	)

	governing_body = auto_prefetch.ForeignKey(
		GoverningBody, on_delete=models.CASCADE, related_name="leagues"
	)
	name = models.CharField(max_length=100, unique=True)
	level_of_play = models.CharField(max_length=100, blank=True, null=True)
	season = models.CharField(max_length=50, blank=True, null=True)
	region = models.CharField(max_length=2, choices=REGIONS, blank=True, null=True)

	def __str__(self):
		return f"{self.name} ({self.governing_body.name})"

	class Meta(auto_prefetch.Model.Meta):
		constraints = [
			models.UniqueConstraint(
				fields=["name", "governing_body"],
				name="unique_league_per_governing_body",
			)
		]


"""
class Division(auto_prefetch.Model):
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="divisions"
	)
	name = models.CharField(max_length=100)
	hierarchy_level = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.name} ({self.league.name})"
"""


class TeamManager(models.Manager):
	"""Custom manager for Team model that queries an API for missing fields on create."""

	def create(self, **kwargs):
		"""Override create to fetch missing fields from API if not provided."""
		# Required fields
		name = kwargs.get("name")
		governing_body = kwargs.get("governing_body")

		if not name or not governing_body:
			raise ValidationError(
				_("Team creation requires 'name' and 'governing_body'.")
			)

		# Ensure governing_body is a GoverningBody instance
		if not isinstance(governing_body, GoverningBody):
			try:
				governing_body = GoverningBody.objects.get(pk=governing_body)
			except GoverningBody.DoesNotExist as e:
				raise ValidationError(
					_("Invalid governing_body: %s not found.") % governing_body
				) from e

		# Fields to fetch from API if missing
		optional_fields = {
			"logo": kwargs.get("logo"),
			"website": kwargs.get("website"),
			"short_name": kwargs.get("short_name"),
			"location": kwargs.get("location"),
			"founding_year": kwargs.get("founding_year"),
			"league": kwargs.get("league"),
		}

		# Only query API if any optional fields are missing
		if not all(optional_fields.values()):
			try:
				sport_name = governing_body.sport.name
				api_data = mock_team_api_lookup(name, sport_name)  # TODO

				# Map API data to model fields if not provided
				if not optional_fields["logo"] and api_data.get("logo_url"):
					kwargs["logo"] = api_data["logo_url"]
				if not optional_fields["website"] and api_data.get("website"):
					kwargs["website"] = api_data["website"]
				if not optional_fields["short_name"] and api_data.get("short_name"):
					kwargs["short_name"] = api_data["short_name"]
				if not optional_fields["location"] and api_data.get("city"):
					kwargs["location"] = api_data["city"]
				if not optional_fields["founding_year"] and api_data.get("founded"):
					kwargs["founding_year"] = api_data["founded"]
				if not optional_fields["league"] and api_data.get("league_name"):
					# Try to resolve or create League
					try:
						league = League.objects.get(
							name__iexact=api_data["league_name"],
							governing_body=governing_body,
						)
					except League.DoesNotExist:
						league = League.objects.create(
							name=api_data["league_name"], governing_body=governing_body
						)
					kwargs["league"] = league

				logger.info(f"Retrieved API data for team {name}: {api_data}")
			except Exception as e:
				logger.error(f"API lookup failed for team {name}: {str(e)}")
				# Proceed with provided fields if API fails
				messages.warning(
					kwargs.get("request"),
					_(
						f"Failed to fetch additional data for team {name}. Using provided fields."
					),
				)

		# Create Team instance with provided and API-fetched fields
		try:
			team = super().create(**kwargs)
			logger.info(
				f"Created team {team.name} for governing body {team.governing_body.name}"
			)
			return team
		except Exception as e:
			logger.error(f"Failed to create team {name}: {str(e)}")
			raise ValidationError(_(f"Team creation failed: {str(e)}")) from e


def save_uploaded_logos(instance, filename):
	return f"teams/logos/{slugify(instance.name)}_logo.jpg"


def save_uploaded_brands(instance, filename):
	return f"teams/brands/{slugify(instance.name)}_brand.jpg"


class Team(auto_prefetch.Model):
	logo = models.ImageField(upload_to=save_uploaded_logos, null=True, blank=True)
	brand = models.ImageField(upload_to=save_uploaded_brands, null=True, blank=True)
	website = models.URLField(null=True, blank=True)
	governing_body = auto_prefetch.ForeignKey(
		GoverningBody, on_delete=models.CASCADE, related_name="teams"
	)
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="teams", blank=True, null=True
	)
	# division = auto_prefetch.ForeignKey(Division, on_delete=models.CASCADE, related_name="teams", blank=True, null=True)
	name = models.CharField(max_length=100)
	short_name = models.CharField(max_length=20, blank=True)
	location = models.CharField(max_length=100, blank=True, null=True)
	founding_year = models.PositiveIntegerField(blank=True, null=True)
	downloaded = models.BooleanField(default=False, editable=False)
	objects = TeamManager()

	def __str__(self):
		# if self.division: return f"{self.name} ({self.division.name})";
		return self.name

	class Meta(auto_prefetch.Model.Meta):
		constraints = [
			models.UniqueConstraint(
				Lower("name"), "league", name="unique_team_per_league"
			),
			# models.UniqueConstraint(Lower("name"), "division", name="unique_team_per_division"),
		]


"""
class Player(auto_prefetch.Model):
	icon = models.ImageField(blank=True, null=True)
	team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="players"
	)
	name = models.CharField(max_length=100)
	position = models.CharField(max_length=100, blank=True, null=True)
	jersey_number = models.PositiveIntegerField(blank=True, null=True)

	def __str__(self):
		return f"{self.name} ({self.team.name})"
"""


class Game(auto_prefetch.Model):
	governing_body = auto_prefetch.ForeignKey(
		GoverningBody, on_delete=models.CASCADE, related_name="games"
	)
	league = auto_prefetch.ForeignKey(
		League,
		on_delete=models.CASCADE,
		related_name="games",
		blank=True,
		null=True,
	)
	home_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="games_home_teams"
	)
	away_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="games_away_teams"
	)
	home_team_score = models.IntegerField(blank=True, null=True)
	away_team_score = models.IntegerField(blank=True, null=True)
	winner = auto_prefetch.ForeignKey(
		Team,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="game_wins",
	)
	location = models.CharField(max_length=100, blank=True)
	start_datetime = models.DateTimeField()
	is_finished = models.BooleanField(default=False)
	boxscore = models.CharField(max_length=100, null=True, editable=False)

	@cached_property
	def has_started(self):
		return timezone.now() > self.start_datetime

	@property
	def sport(self):
		return self.governing_body.sport

	class Meta(auto_prefetch.Model.Meta):
		constraints = [
			models.UniqueConstraint(
				fields=["home_team", "away_team", "start_datetime"],
				name="unique_game",
			),
			models.UniqueConstraint(
				fields=["boxscore"],
				condition=Q(boxscore__isnull=False),
				name="unique_game_boxscore_when_not_null",
			),
			models.CheckConstraint(
				condition=~Q(home_team=F("away_team")),
				name="game_home_team_not_away_team",
				violation_error_message="Home and away teams cannot be the same.",
			),
		]


class BettingLine(auto_prefetch.Model):
	game = auto_prefetch.OneToOneField(
		Game,
		on_delete=models.CASCADE,
		related_name="betting_line",
		unique=True,
	)
	spread = models.IntegerField(blank=True, null=True)
	is_pick = models.BooleanField(blank=True, default=False)
	over = models.IntegerField(blank=True, null=True)
	under = models.IntegerField(blank=True, null=True)
	is_draft = models.BooleanField(default=False)

	def __str__(self):
		_str = _("%(sport)s: %(home_team)s vs %(away_team)s (%(spread)s)") % {
			"sport": self.game.sport.name,
			"home_team": self.game.home_team,
			"away_team": self.game.away_team,
			"spread": self.spread if not self.is_pick else "P" + str(self.spread),
		}
		if self.under or self.over:
			_str += _(" - un%(under)d/%(over)dov") % {
				"under": self.under,
				"over": self.over,
			}
		return _str

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("betting line")
		verbose_name_plural = _("betting lines")
		constraints = [
			models.CheckConstraint(
				condition=(Q(under__isnull=True) & Q(over__isnull=True))
				| (Q(under__isnull=False) & Q(over__isnull=False)),
				name="betting_line_validate_under_over",
				violation_error_message="Must populate both under and over, or leave both blank.",
			),
		]


class Play(auto_prefetch.Model):
	user = auto_prefetch.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="plays"
	)
	amount = MoneyField(
		max_digits=10,
		decimal_places=2,
		default_currency="USD",
		validators=[MinMoneyValidator(settings.SPORTS["MIN_BET"])],
	)
	stakes = models.IntegerField(blank=True, null=True, editable=False)
	placed_datetime = models.DateTimeField(auto_now=True)
	paid = models.BooleanField(default=False, editable=False)
	won = models.BooleanField(default=False)
	# TODO: Add choices for the status field.
	status = models.CharField(
		max_length=50,
		blank=True,
		null=True,
		help_text=_("Status of the play, e.g., 'pending', 'completed'"),
	)

	def __str__(self):
		return _("Play %(id)d : %(user)s (Paid: %(paid)s; Won: %(won)s)") % {
			"id": self.id,
			"user": self.user,
			"paid": self.paid,
			"won": self.won,
		}

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("play")
		verbose_name_plural = _("plays")


class Pick(auto_prefetch.Model):
	TYPES = Choices(
		("sp", "spread", _("Spread")),
		("uo", "under_over", _("Under/Over")),
		# ("pl", "player", _("Player")),
	)

	play = auto_prefetch.ForeignKey(
		Play, on_delete=models.CASCADE, related_name="picks"
	)
	betting_line = auto_prefetch.ForeignKey(
		BettingLine, on_delete=models.CASCADE, related_name="picks"
	)
	type = models.CharField(max_length=2, choices=TYPES)
	team = auto_prefetch.ForeignKey(
		Team,
		on_delete=models.SET_NULL,
		related_name="picks",
		null=True,
		blank=True,
	)
	# player = auto_prefetch.ForeignKey(Player, on_delete=models.SET_NULL, related_name="picks", null=True, blank=True)
	# stat_type = None  # TODO
	# target_value = None  # TODO
	is_over = models.BooleanField(null=True, blank=True)

	@cached_property
	def won(self):
		# Return None if the game isn’t finished
		if not self.betting_line.game.is_finished:
			return None

		# Get game scores
		home_score = self.betting_line.game.home_team_score
		away_score = self.betting_line.game.away_team_score

		# Ensure scores are available
		if home_score is None or away_score is None:
			return None

		if self.type == self.TYPES.spread:
			# Spread bet: team must win by more than the spread
			spread = self.betting_line.spread
			is_pick = self.betting_line.is_pick
			picked_team = self.team

			if picked_team == self.betting_line.game.home_team:
				return (
					(home_score - away_score) > spread
					if is_pick
					else (home_score + spread) > away_score
				)
			elif picked_team == self.betting_line.game.away_team:
				return (
					(away_score - home_score) > spread
					if is_pick
					else (home_score + spread) < away_score
				)
			return False  # Team not in game (shouldn’t happen due to constraints)

		elif self.type == self.TYPES.under_over:
			# Over/Under bet: compare total score to over/under value
			total_score = home_score + away_score
			if self.is_over:
				return total_score > self.betting_line.over
			else:
				return total_score < self.betting_line.under

		return None  # Default for unhandled types (e.g., future 'player' type)

	def __str__(self):
		if self.type == self.TYPES.spread:
			return _("%(home_team)s/%(away_team)s - %(picked)s") % {
				"home_team": self.betting_line.home_team,
				"away_team": self.betting_line.away_team,
				"picked": self.team,
			}
		elif self.type == self.TYPES.under_over:
			if self.is_over:
				return _("%(home_team)s/%(away_team)s - ov%(over)s") % {
					"home_team": self.betting_line.spread.home_team,
					"away_team": self.betting_line.spread.away_team,
					"over": self.betting_line.over,
				}
			else:
				return _("%(home_team)s/%(away_team)s - un%(under)s") % {
					"home_team": self.betting_line.spread.home_team,
					"away_team": self.betting_line.spread.away_team,
					"under": self.betting_line.under,
				}
		# elif self.type == self.TYPES.player: return f"{self.player.name} - {self.stat_type} ({'Over' if self.is_over else 'Under'} {self.target_value})";

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("pick")
		verbose_name_plural = _("picks")
		constraints = [
			models.UniqueConstraint(
				name="unique_pick", fields=["play", "betting_line", "type"]
			),
		]
