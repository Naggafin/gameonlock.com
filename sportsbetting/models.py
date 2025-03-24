import auto_prefetch
from django.conf import settings
from django.db import models
from django.db.models import F, Q
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from model_utils import Choices
from slugify import slugify


class Sport(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)
	slug_name = models.SlugField(unique=True, blank=True, editable=False)

	def save(self, *args, **kwargs):
		if not self.slug_name:
			self.slug_name = slugify(self.name)
		return super().save(*args, **kwargs)

	def __str__(self):
		return self.name


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
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)
	type = models.CharField(
		max_length=3,
		choices=TYPES,
		verbose_name=_("type of competition"),
	)

	def __str__(self):
		return f"{self.name} ({self.sport.name})"

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("governing body")
		verbose_name_plural = _("governing bodies")


class League(auto_prefetch.Model):
	REGIONS = Choices(
		("wd", "world", _("World-wide")),
		("eu", "europe", _("Europe")),
		("as", "asia", _("Asia")),
		("af", "africa", _("Africa")),
		("na", "north_merica", _("North America")),
		("sa", "south_america", _("South America")),
		("oc", "oceania", _("Oceania")),
	)

	governing_body = auto_prefetch.ForeignKey(
		GoverningBody, on_delete=models.CASCADE, related_name="leagues"
	)
	name = models.CharField(max_length=100)
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


def save_uploaded_logos(instance, filename):
	return f"teams/logos/{slugify(instance.name)}_logo.jpg"


def save_uploaded_brands(instance, filename):
	return f"teams/brands/{slugify(instance.name)}_brand.jpg"


class Team(auto_prefetch.Model):
	logo = models.ImageField(upload_to=save_uploaded_logos, null=True, blank=True)
	brand = models.ImageField(upload_to=save_uploaded_brands, null=True, blank=True)
	website = models.URLField(null=True, blank=True)
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="teams"
	)
	# division = auto_prefetch.ForeignKey(Division, on_delete=models.CASCADE, related_name="teams", blank=True, null=True)
	name = models.CharField(max_length=100)
	location = models.CharField(max_length=100, blank=True, null=True)
	founding_year = models.PositiveIntegerField(blank=True, null=True)
	downloaded = models.BooleanField(default=False, editable=False)

	def __str__(self):
		# if self.division: return f"{self.name} ({self.division.name})";
		return self.name

	class Meta(auto_prefetch.Model.Meta):
		constraints = [
			models.UniqueConstraint(
				fields=["name", "league"], name="unique_team_per_league"
			),
			# models.UniqueConstraint(fields=["name", "division"], name="unique_team_per_division"),
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


class ScheduledGame(auto_prefetch.Model):
	sport = auto_prefetch.ForeignKey(
		Sport, on_delete=models.CASCADE, related_name="scheduled_games"
	)
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="scheduled_games"
	)
	home_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="scheduled_games_home_team"
	)
	away_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="scheduled_games_away_team"
	)
	home_team_score = models.IntegerField(blank=True, null=True)
	away_team_score = models.IntegerField(blank=True, null=True)
	winner = auto_prefetch.ForeignKey(
		Team,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="schedule_game_wins",
	)
	location = models.CharField(max_length=100)
	start_datetime = models.DateTimeField()
	is_finished = models.BooleanField(default=False)

	class Meta(auto_prefetch.Model.Meta):
		constraints = [
			models.UniqueConstraint(
				fields=["home_team", "away_team", "start_datetime"],
				name="unique_scheduled_game",
			),
			models.CheckConstraint(
				condition=~Q(home_team=F("away_team")),
				name="scheduled_game_home_team_not_away_team",
				violation_error_message="Home and away teams cannot be the same.",
			),
		]


class BettingLine(auto_prefetch.Model):
	game = auto_prefetch.OneToOneField(
		ScheduledGame,
		on_delete=models.CASCADE,
		related_name="betting_line",
		unique=True,
	)
	spread = models.IntegerField()
	is_pick = models.BooleanField(blank=True, default=False)
	over = models.IntegerField(blank=True, null=True)
	under = models.IntegerField(blank=True, null=True)
	start_datetime = models.DateTimeField()

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


class PlayPick(auto_prefetch.Model):
	TYPES = Choices(
		("sp", "spread", _("Spread")),
		("uo", "under_over", _("Under/Over")),
		# ("pl", "player", _("Player")),
	)

	play = auto_prefetch.ForeignKey(
		Play, on_delete=models.CASCADE, related_name="picks"
	)
	betting_line = auto_prefetch.ForeignKey(
		BettingLine, on_delete=models.CASCADE, related_name="play_picks"
	)
	type = models.CharField(max_length=2, choices=TYPES)
	team = auto_prefetch.ForeignKey(
		Team,
		on_delete=models.SET_NULL,
		related_name="play_picks",
		null=True,
		blank=True,
	)
	# player = auto_prefetch.ForeignKey(Player, on_delete=models.SET_NULL, related_name="play_picks", null=True, blank=True)
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
				name="unique_play_pick", fields=["play", "betting_line", "type"]
			),
		]
