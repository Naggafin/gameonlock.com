import datetime

import auto_prefetch
from django.conf import settings
from django.core.functional import cached_property
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from djmoney.money import Money
from model_utils import Choices
from slugify import slugify


class Sport(models.Model):
	icon = models.ImageField()
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True, null=True)

	@cached_property
	def slug_name(self):
		return slugify(self.name)

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

	icon = models.ImageField(blank=True, null=True)
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

	icon = models.ImageField(blank=True, null=True)
	governing_body = auto_prefetch.ForeignKey(
		GoverningBody, on_delete=models.CASCADE, related_name="leagues"
	)
	name = models.CharField(max_length=100)
	level_of_play = models.CharField(max_length=100, blank=True, null=True)
	season = models.CharField(max_length=50, blank=True, null=True)
	region = models.CharField(max_length=2, choices=REGIONS, blank=True, null=True)

	def __str__(self):
		return f"{self.name} ({self.governing_body.name})"


class Division(auto_prefetch.Model):
	icon = models.ImageField(blank=True, null=True)
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="divisions"
	)
	name = models.CharField(max_length=100)
	hierarchy_level = models.PositiveIntegerField(default=1)

	def __str__(self):
		return f"{self.name} ({self.league.name})"


class Team(auto_prefetch.Model):
	icon = models.ImageField()
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="teams", blank=True, null=True
	)
	division = auto_prefetch.ForeignKey(
		Division, on_delete=models.CASCADE, related_name="teams", blank=True, null=True
	)
	name = models.CharField(max_length=100)
	location = models.CharField(max_length=100, blank=True, null=True)
	founding_year = models.PositiveIntegerField(blank=True, null=True)

	def __str__(self):
		if self.division:
			return f"{self.name} ({self.division.name})"
		return self.name


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


class ScheduledGame(auto_prefetch.Model):
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="schedule_games"
	)
	home_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="schedule_games_home_team"
	)
	away_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="schedule_games_away_team"
	)
	location = models.CharField(max_length=100)
	datetime = models.DateTimeField()


class Ticket(models.Model):
	pub_date = models.DateField(default=datetime.date.today, unique=True)
	end_date = models.DateField()

	def save(self, *args, **kwargs):
		if self.end_date is None:
			self.end_date = self.pub_date + datetime.timedelta(days=1)
		return super().save(*args, **kwargs)

	class Meta:
		verbose_name = _("ticket")
		verbose_name_plural = _("tickets")
		get_latest_by = "pub_date"


class TicketPlay(auto_prefetch.Model):
	ticket = auto_prefetch.ForeignKey(
		Ticket, on_delete=models.CASCADE, related_name="plays"
	)
	purchaser = auto_prefetch.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ticket_plays"
	)
	amount = MoneyField(
		max_digits=10, decimal_places=2, validators=[MinMoneyValidator(Money("USD", 5))]
	)
	date = models.DateTimeField(auto_now=True)
	paid = models.BooleanField(default=False)
	won = models.BooleanField(default=False)

	def __str__(self):
		return _("Play %(id)d : %(email)s (Paid: %(paid)s; Won: %(won)s)") % {
			"id": self.id,
			"email": self.email,
			"paid": self.paid,
			"won": self.won,
		}

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("play")
		verbose_name_plural = _("plays")


class TicketEntry(auto_prefetch.Model):
	ticket = auto_prefetch.ForeignKey(
		Ticket, on_delete=models.CASCADE, related_name="entries"
	)
	league = auto_prefetch.ForeignKey(
		League, on_delete=models.CASCADE, related_name="ticket_entries"
	)
	home_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="ticket_entry_home_team"
	)
	away_team = auto_prefetch.ForeignKey(
		Team, on_delete=models.CASCADE, related_name="ticket_entry_away_team"
	)
	spread = models.DecimalField(max_digits=5, decimal_places=2)
	is_pick = models.BooleanField(blank=True, default=False)
	over = models.IntegerField(blank=True, null=True)
	under = models.IntegerField(blank=True, null=True)
	start_datetime = models.DateTimeField()
	winner = auto_prefetch.ForeignKey(
		Team,
		on_delete=models.SET_NULL,
		null=True,
		blank=True,
		related_name="ticket_entry_wins",
	)

	def __str__(self):
		return _(
			"%(sport)s: %(home_team)s vs %(away_team)s (%(spread)s) - un%(under)d/%(over)dov"
		) % {
			"sport": self.sport.name,
			"home_team": self.home_team,
			"away_team": self.away_team,
			"spread": self.spread if not self.is_pick else "P" + str(self.spread),
			"under": self.under,
			"over": self.over,
		}

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("ticket entry")
		verbose_name_plural = _("ticket entries")


class TicketEntryPick(auto_prefetch.Model):
	TYPES = Choices(
		("sp", "spread", _("Spread")),
		("uo", "under_over", _("Under/Over")),
		("pl", "player", _("Player")),
	)

	play = auto_prefetch.ForeignKey(
		TicketPlay, on_delete=models.CASCADE, related_name="picks"
	)
	ticket_entry = auto_prefetch.ForeignKey(
		TicketEntry, on_delete=models.CASCADE, related_name="picks"
	)
	type = models.CharField(max_length=2, choices=TYPES)
	team = auto_prefetch.ForeignKey(
		Team,
		on_delete=models.SET_NULL,
		related_name="ticket_entry_picks",
		null=True,
		blank=True,
	)
	player = auto_prefetch.ForeignKey(
		Player,
		on_delete=models.SET_NULL,
		related_name="ticket_entry_picks",
		null=True,
		blank=True,
	)
	stat_type = None  # TODO
	target_value = None  # TODO
	is_over = models.BooleanField(null=True, blank=True)

	def __str__(self):
		if self.type == type(self).TYPES.spread:
			return _("%(home_team)s/%(away_team)s - %(picked)s") % {
				"home_team": self.ticket_entry.home_team,
				"away_team": self.ticket_entry.away_team,
				"picked": self.team,
			}
		elif self.type == type(self).TYPES.under_over:
			if self.is_over:
				return _("%(home_team)s/%(away_team)s - ov%(over)s") % {
					"home_team": self.ticket_entry.spread.home_team,
					"away_team": self.ticket_entry.spread.away_team,
					"over": self.ticket_entry.over,
				}
			else:
				return _("%(home_team)s/%(away_team)s - un%(under)s") % {
					"home_team": self.ticket_entry.spread.home_team,
					"away_team": self.ticket_entry.spread.away_team,
					"under": self.ticket_entry.under,
				}
		elif self.type == type(self).TYPES.player:
			return f"{self.player.name} - {self.stat_type} ({'Over' if self.is_over else 'Under'} {self.target_value})"

	class Meta(auto_prefetch.Model.Meta):
		verbose_name = _("pick")
		verbose_name_plural = _("picks")
		constraints = [
			UniqueConstraint(
				name="unique_ticket_entry_pick", fields=["play", "ticket_entry", "type"]
			),
		]
