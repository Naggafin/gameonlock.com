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
def get_pending_games(queryset):
	now = timezone.now()
	games = [game for game in queryset if game.start_datetime > now]
	return games


@register.filter
def chain(lists):
	return itertools.chain(lists)


@register.filter
def get(dict, value):
	return dict[value]


@register.filter(name="int")
def int_filter(value):
	return int(value)


@register.simple_tag
def num_betting_lines(obj, state=None):
	# NOTE: we do this in a prefetch_related() efficient manner
	if not state:
		lines = itertools.chain.from_iterable(
			[game.betting_lines.all() for game in obj.scheduled_games.all()]
		)
	elif state == "upcoming":
		lines = itertools.chain.from_iterable(
			[
				game.betting_lines.all()
				for game in obj.scheduled_games.all()
				if not game_has_started(game)
			]
		)
	elif state == "in_play":
		lines = itertools.chain.from_iterable(
			[
				game.betting_lines.all()
				for game in obj.scheduled_games.all()
				if game_has_started(game) and not game.is_finished
			]
		)
	elif state == "finished":
		lines = itertools.chain.from_iterable(
			[
				game.betting_lines.all()
				for game in obj.scheduled_games.all()
				if game.is_finished
			]
		)
	return len(list(lines))
