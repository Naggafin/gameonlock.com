import datetime
from django.core import validators
from django.db import models
from django.db.models import Q, F, CheckConstraint, UniqueConstraint
from django.conf import settings



class Sport(models.Model):
	name = models.CharField(max_length=255, unique=True)
	short = models.CharField(max_length=32, blank= True, null=True)
	
	def __str__(self):
		return f"{self.name}"


class Participant(models.Model):
	TYPES = [
		('TM', 'Team'),
		('PL', 'Player'),
	]
	
	type = models.CharField(max_length=2, choices=TYPES, default='TM')
	sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='participants')
	name = models.CharField(max_length=255)
	short = models.CharField(max_length=32, blank=True, null=True)
	member_of = models.ForeignKey('self', on_delete=models.CASCADE, related_name='players', blank=True, null=True)
	
	def __str__(self):
		if not self.short:
			return f"{self.name}"
		else:
			return f"{self.name} - {self.short}"
	
	class Meta:
		pass


class Ticket(models.Model):
	name = models.CharField(max_length=255, default=settings.SPORTS['default_ticket_name'])
	pub_date = models.DateField(default=datetime.date.today, unique=True)
	end_date = models.DateField(default=datetime.date.today)
	sports = models.ManyToManyField(Sport, related_name="on_tickets")
	
	def __str__(self):
		return f"{self.name}"
	
	class Meta():
		get_latest_by = 'pub_date'


class SpreadEntry(models.Model):
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='spreads')
	sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='spreads')
	first_team = models.CharField(max_length=255)
	second_team = models.CharField(max_length=255)
	spread = models.IntegerField(blank=True, null=True)
	spreadIsPick = models.BooleanField(blank=True, null=True)
	isPreview = models.BooleanField(default=False)
	start_datetime = models.DateTimeField()
	winner = models.CharField(max_length=255, blank=True, null=True)
	
	def __str__(self):
		if self.spreadIsPick == True:
			return f"{self.sport.name} {self.first_team} P{self.spread} {self.second_team}"
		else:
			return f"{self.sport.name} {self.first_team} {self.spread} {self.second_team}"


class UnderOverEntry(models.Model):
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='under_overs')
	linked_spread = models.OneToOneField(SpreadEntry, on_delete=models.CASCADE, related_name='under_over')
	under = models.IntegerField(blank=True, null=True)
	over = models.IntegerField(blank=True, null=True)
	under_or_over = models.BooleanField(blank=True, null=True)
	
	def __str__(self):
		return f"{self.linked_spread.sport.name} : Un {self.under} - Ov {self.over}"


class TicketPlay(models.Model):
	ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='orders')
	purchaser_name = models.CharField(max_length=255)
	email = models.EmailField()
	phone = models.CharField(max_length=14, blank=True, null=True)
	bet_amount = models.DecimalField(max_digits=6, decimal_places=2, validators=[validators.MinValueValidator(limit_value=5)])
	date = models.DateTimeField(auto_now=True)
	paid = models.BooleanField(default=False)
	won = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.id} : {self.email} (Paid: {self.paid}; Won: {self.won})"


class SpreadPick(models.Model):
	play = models.ForeignKey(TicketPlay, on_delete=models.CASCADE, related_name="spread_picks")
	picked = models.CharField(max_length=255)
	spread_entry = models.ForeignKey(SpreadEntry, on_delete=models.CASCADE, related_name="picks")
	
	def __str__(self):
		return f"{self.spread_entry.first_team}/{self.spread_entry.second_team} - {self.picked}"
	
	class Meta:
		constraints = [
			UniqueConstraint(name='unique_spread_pick', fields=['play', 'spread_entry']),
		]


class UnderOverPick(models.Model):
	play = models.ForeignKey(TicketPlay, on_delete=models.CASCADE, related_name="under_over_picks")
	under_or_over = models.BooleanField()
	under_over_entry = models.ForeignKey(UnderOverEntry, on_delete=models.CASCADE, related_name="picks")
	
	def __str__(self):
		if self.under_or_over == False:
			return f"{self.under_over_entry.linked_spread.first_team}/{self.under_over_entry.linked_spread.second_team} - un{self.under_over_entry.under}"
		else:
			return f"{self.under_over_entry.linked_spread.first_team}/{self.under_over_entry.linked_spread.second_team} - ov{self.under_over_entry.over}"

	class Meta:
		constraints = [
			UniqueConstraint(name='unique_under_over_pick', fields=['play', 'under_over_entry']),
		]
