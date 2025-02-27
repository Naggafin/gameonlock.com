import itertools

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def game_has_started(game):
	if not game.start_datetime:
		return False
	return timezone.now().time() > game.start_datetime.time()


@register.filter
def game_start_datetime(game):
	format = "%d %b %Y %I:%M:%S %Z%z"
	dt = game.start_datetime
	return dt.strftime(format)


@register.filter
def num_betting_lines(sport):
	lines = itertools.chain.from_iterable(
		[
			game.betting_lines.all()
			for game in sport.scheduled_games.all()
			if not game_has_started(game)
		]
	)
	return len(list(lines))
