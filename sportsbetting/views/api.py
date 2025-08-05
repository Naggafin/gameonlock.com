from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Play
from ..serializers import PlaySerializer


class UserBetSlipsView(APIView):
	permission_classes = [IsAuthenticated]

	def get(self, request):
		plays = (
			Play.objects.filter(user=request.user)
			.prefetch_related(
				"picks__betting_line__game__home_team",
				"picks__betting_line__game__away_team",
				"picks__team",
				"picks__betting_line__game__league",
				"picks__betting_line__game__governing_body__sport",
			)
			.order_by("-placed_datetime")
		)
		serializer = PlaySerializer(plays, many=True)
		return Response(serializer.data)
