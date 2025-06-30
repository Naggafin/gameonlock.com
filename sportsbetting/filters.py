from django_filters import FilterSet

from .models import Play


class PlayFilter(FilterSet):
	class Meta:
		model = Play
		fields = ["placed_datetime", "status", "won"]
