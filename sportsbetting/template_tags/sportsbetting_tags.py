import itertools

from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def game_has_started(game):
	if not game.start_datetime:
		return False
	return timezone.now().time() > game.start_datetime.time()


@register.simple_tag
def num_betting_lines_for_sport(sport):
	lines = itertools.chain.from_iterable(
		[
			game.betting_lines.all()
			for game in sport.schedule_games.all()
			if not game_has_started(game)
		]
	)
	return len(lines)
