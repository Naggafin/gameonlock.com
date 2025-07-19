import itertools

from cache_memoize import cache_memoize
from django import template
from django.utils import timezone

from ..models import BettingLine

register = template.Library()


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
@cache_memoize(
	None, args_rewrite=lambda obj, state: f"{obj._meta.model_name}_{obj.pk}_{state}"
)
def num_betting_lines(obj, state=None):
	lines = BettingLine.objects.filter(game__governing_body__sport=obj)
	if state:
		if state == "upcoming":
			lines = lines.filter(game__start_datetime__gt=timezone.now())
		elif state == "in_play":
			lines = lines.filter(
				game__start_datetime__lte=timezone.now(), game__is_finished=False
			)
		elif state == "finished":
			lines = lines.filter(game__is_finished=True)
	return lines.count()
