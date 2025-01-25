from datetime import datetime

from django import template

register = template.Library()


@register.filter
def game_has_started(ticket_entry):
	if not ticket_entry.start_datetime:
		return False
	return datetime.now().time() > ticket_entry.start_datetime.time()


@register.simple_tag
def num_entries(ticket, sport):
	entries = [
		ticket_entry.league.sport_id == sport.pk
		for ticket_entry in ticket.entries.all()
	]
	return len(entries)
