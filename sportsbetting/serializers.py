from rest_framework import serializers

from .models import BettingLine, Game, Pick, Play, Team


class TeamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = ["id", "name"]


class GameSerializer(serializers.ModelSerializer):
	home_team = TeamSerializer()
	away_team = TeamSerializer()
	sport = serializers.SerializerMethodField()

	class Meta:
		model = Game
		fields = [
			"id",
			"home_team",
			"away_team",
			"start_datetime",
			"is_finished",
			"home_team_score",
			"away_team_score",
			"league",
			"governing_body",
			"sport",
		]

	def get_sport(self, obj):
		return obj.governing_body.sport.pk


class BettingLineSerializer(serializers.ModelSerializer):
	game = GameSerializer()

	class Meta:
		model = BettingLine
		fields = ["id", "spread", "is_pick", "over", "under", "game"]


class PickSerializer(serializers.ModelSerializer):
	is_over = serializers.BooleanField(allow_null=True)

	class Meta:
		model = Pick
		fields = ["id", "type", "is_over", "team", "betting_line"]


class PlaySerializer(serializers.ModelSerializer):
	picks = PickSerializer(many=True)
	amount = serializers.SerializerMethodField()
	stakes = serializers.SerializerMethodField()

	class Meta:
		model = Play
		fields = [
			"id",
			"amount",
			"stakes",
			"won",
			"status",
			"placed_datetime",
			"paid",
			"picks",
		]

	def get_amount(self, obj):
		return str(obj.amount) if obj.amount else None

	def get_stakes(self, obj):
		return str(obj.stakes) if obj.stakes else None
