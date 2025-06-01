import itertools
from functools import cache

from django import template
from django.utils import timezone

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
@cache
def num_betting_lines(obj, state=None):
    # NOTE: we do this in a prefetch_related() efficient manner
    if not state:
        lines = [game.betting_line for game in obj.games.all()]
    else:
        if state == "upcoming":
            lines = [
                game.betting_line for game in obj.games.all() if not game.has_started
            ]
        elif state == "in_play":
            lines = [
                game.betting_line
                for game in obj.games.all()
                if game.has_started and not game.is_finished
            ]
        elif state == "finished":
            lines = [game.betting_line for game in obj.games.all() if game.is_finished]
    return len(list(lines))
