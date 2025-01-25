import datetime

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from djmoney.models.validators import MinMoneyValidator
from djmoney.money import Money
from model_utils import Choices
from phonenumber_field.modelfields import PhoneNumberField


class Sport(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short_name = models.CharField(max_length=32, blank=True, null=True)

	def __str__(self):
		return _("%(name)s") % {"name": self.name}


class Participant(models.Model):
	TYPES = Choices(
		("TM", "team", _("Team")),
		("PL", "player", _("Player")),
	)

	type = models.CharField(max_length=2, choices=TYPES, default=TYPES.team)
	sport = models.ForeignKey(
		Sport, on_delete=models.CASCADE, related_name="participants"
	)
	name = models.CharField(max_length=255)
	short_name = models.CharField(max_length=32, blank=True, null=True)
	member_of = models.ForeignKey(
		"self", on_delete=models.CASCADE, related_name="players", blank=True, null=True
	)

	def __str__(self):
		if not self.short_name:
			return _("%(name)s") % {"name": self.name}
		else:
			return _("%(name)s - %(short_name)s") % {
				"name": self.name,
				"short_name": self.short_name,
			}


class Ticket(models.Model):
	name = models.CharField(
		max_length=255, default=settings.SPORTS["default_ticket_name"]
	)
	pub_date = models.DateField(default=datetime.date.today, unique=True)
	end_date = models.DateField(default=datetime.date.today)
	sports = models.ManyToManyField(Sport, related_name="tickets")

	def __str__(self):
		return _("%(name)s") % {"name": self.name}

	class Meta:
		get_latest_by = "pub_date"


class SpreadEntry(models.Model):
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="spreads")
	sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name="spreads")
	first_team = models.CharField(max_length=255)
	second_team = models.CharField(max_length=255)
	spread = models.IntegerField(blank=True, null=True)
	spread_is_pick = models.BooleanField(blank=True, null=True)
	is_preview = models.BooleanField(default=False)
	start_datetime = models.DateTimeField()
	winner = models.CharField(max_length=255, blank=True, null=True)

	def __str__(self):
		if self.spread_is_pick:
			return _("%(sport_name)s %(first_team)s P%(spread)s %(second_team)s") % {
				"sport_name": self.sport.name,
				"first_team": self.first_team,
				"spread": self.spread,
				"second_team": self.second_team,
			}
		else:
			return _("%(sport_name)s %(first_team)s %(spread)s %(second_team)s") % {
				"sport_name": self.sport.name,
				"first_team": self.first_team,
				"spread": self.spread,
				"second_team": self.second_team,
			}


class UnderOverEntry(models.Model):
	ticket = models.ForeignKey(
		Ticket, on_delete=models.CASCADE, related_name="under_overs"
	)
	spread = models.OneToOneField(
		SpreadEntry, on_delete=models.CASCADE, related_name="under_over"
	)
	under = models.IntegerField()
	over = models.IntegerField()
	under_or_over = models.BooleanField(blank=True, null=True)

	def __str__(self):
		return _("%(sport_name)s : Un %(under)s - Ov %(over)s") % {
			"sport_name": self.spread.sport.name,
			"under": self.under,
			"over": self.over,
		}


class TicketPlay(models.Model):
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="plays")
	purchaser_name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = PhoneNumberField(blank=True, null=True)
	bet_amount = MoneyField(
		max_digits=10, decimal_places=2, validators=[MinMoneyValidator(Money("USD", 5))]
	)
	date = models.DateTimeField(auto_now=True)
	paid = models.BooleanField(default=False)
	won = models.BooleanField(default=False)

	def __str__(self):
		return _("%(id)d : %(email)s (Paid: %(paid)s; Won: %(won)s)") % {
			"id": self.id,
			"email": self.email,
			"paid": self.paid,
			"won": self.won,
		}


class SpreadPick(models.Model):
	play = models.ForeignKey(
		TicketPlay, on_delete=models.CASCADE, related_name="spread_picks"
	)
	picked = models.CharField(max_length=255)
	spread_entry = models.ForeignKey(
		SpreadEntry, on_delete=models.CASCADE, related_name="picks"
	)

	def __str__(self):
		return _("%(first_team)s/%(second_team)s - %(picked)s") % {
			"first_team": self.spread_entry.first_team,
			"second_team": self.spread_entry.second_team,
			"picked": self.picked,
		}

	class Meta:
		constraints = [
			UniqueConstraint(
				name="unique_spread_pick", fields=["play", "spread_entry"]
			),
		]


class UnderOverPick(models.Model):
	play = models.ForeignKey(
		TicketPlay, on_delete=models.CASCADE, related_name="under_over_picks"
	)
	under_or_over = models.BooleanField()
	under_over_entry = models.ForeignKey(
		UnderOverEntry, on_delete=models.CASCADE, related_name="picks"
	)

	def __str__(self):
		if self.under_or_over is False:
			return _("%(first_team)s/%(second_team)s - un%(under)s") % {
				"first_team": self.under_over_entry.spread.first_team,
				"second_team": self.under_over_entry.spread.second_team,
				"under": self.under_over_entry.under,
			}
		else:
			return _("%(first_team)s/%(second_team)s - ov%(over)s") % {
				"first_team": self.under_over_entry.spread.first_team,
				"second_team": self.under_over_entry.spread.second_team,
				"over": self.under_over_entry.over,
			}

	class Meta:
		constraints = [
			UniqueConstraint(
				name="unique_under_over_pick", fields=["play", "under_over_entry"]
			),
		]
