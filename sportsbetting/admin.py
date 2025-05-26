from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Team, Game, BettingLine, Play, Pick


class TeamResource(resources.ModelResource):
    class Meta:
        model = Team
        fields = ('id', 'name', 'external_id', 'website', 'location', 'founding_year', 'downloaded')
        export_order = ('id', 'name', 'external_id')


class GameResource(resources.ModelResource):
    class Meta:
        model = Game
        fields = ('id', 'external_id', 'home_team', 'away_team', 'start_time', 'status', 'home_score', 'away_score', 'updated_at')
        export_order = ('id', 'external_id', 'start_time', 'status')


class BettingLineResource(resources.ModelResource):
    class Meta:
        model = BettingLine
        fields = ('id', 'game', 'home_spread', 'over_under', 'updated_at')
        export_order = ('id', 'game', 'home_spread', 'over_under', 'updated_at')


class PlayResource(resources.ModelResource):
    class Meta:
        model = Play
        fields = ('id', 'user', 'amount', 'status', 'payout', 'created_at', 'resolved_at')
        export_order = ('id', 'user', 'amount', 'status', 'created_at')


class PickResource(resources.ModelResource):
    class Meta:
        model = Pick
        fields = ('id', 'play', 'game', 'betting_line', 'pick_type', 'team', 'is_over')
        export_order = ('id', 'play', 'game', 'pick_type')


@admin.register(Team)
class TeamAdmin(ImportExportModelAdmin):
    resource_class = TeamResource
    list_display = ('name', 'external_id', 'location', 'founding_year', 'downloaded')
    search_fields = ('name', 'external_id')
    list_filter = ('downloaded', 'location')


@admin.register(Game)
class GameAdmin(ImportExportModelAdmin):
    resource_class = GameResource
    list_display = ('external_id', 'home_team', 'away_team', 'start_time', 'status', 'home_score', 'away_score')
    search_fields = ('external_id', 'home_team__name', 'away_team__name')
    list_filter = ('status', 'start_time')


@admin.register(BettingLine)
class BettingLineAdmin(ImportExportModelAdmin):
    resource_class = BettingLineResource
    list_display = ('game', 'home_spread', 'over_under', 'updated_at')
    search_fields = ('game__external_id', 'game__home_team__name', 'game__away_team__name')
    list_filter = ('updated_at',)


@admin.register(Play)
class PlayAdmin(ImportExportModelAdmin):
    resource_class = PlayResource
    list_display = ('id', 'user', 'amount', 'status', 'payout', 'created_at', 'resolved_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('status', 'created_at', 'resolved_at')


@admin.register(Pick)
class PickAdmin(ImportExportModelAdmin):
    resource_class = PickResource
    list_display = ('play', 'game', 'pick_type', 'team', 'is_over')
    search_fields = ('play__id', 'game__external_id')
    list_filter = ('pick_type',)