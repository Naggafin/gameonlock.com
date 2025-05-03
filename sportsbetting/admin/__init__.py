from django.contrib import admin
from django.urls import path
from django.utils.translation import gettext_lazy as _

from ..models import (
	BettingLine,
	GoverningBody,
	League,
	Play,
	PlayPick,
	ScheduledGame,
	Sport,
	Team,
)
from .views import GenerateTicketView


class SportsbettingAdminSite(admin.AdminSite):
	def get_urls(self):
		urls = super().get_urls()
		custom_urls = [
			path(
				"sportsbetting/generate-ticket/",
				self.admin_view(GenerateTicketView.as_view()),
				name="sportsbetting_generate_ticket",
			),
		]
		return custom_urls + urls

	def get_app_list(self, request):
		app_list = super().get_app_list(request)
		sportsbetting_app = {
			"name": "Sportsbetting Tools",
			"app_label": "sportsbetting_tools",
			"models": [
				{
					"name": "Generate Ticket",
					"object_name": "generate_ticket",
					"admin_url": f"{self.name}:sportsbetting_generate_ticket",
					"perms": {"view": True},
				},
			],
		}
		app_list.append(sportsbetting_app)
		return app_list


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
	list_display = ("name", "slug_name")
	search_fields = ("name",)
	list_per_page = 25


@admin.register(GoverningBody)
class GoverningBodyAdmin(admin.ModelAdmin):
	list_display = ("name", "sport", "type_display")
	list_filter = ("sport", "type")
	search_fields = ("name", "sport__name")
	list_select_related = ("sport",)
	list_per_page = 25

	def type_display(self, obj):
		return obj.get_type_display()

	type_display.short_description = _("Type")


class LeagueInline(admin.TabularInline):
	model = League
	extra = 1
	show_change_link = True
	fields = ("name", "level_of_play", "season", "region")


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
	list_display = ("name", "governing_body", "region_display", "season")
	list_filter = ("governing_body__sport", "governing_body", "region")
	search_fields = ("name", "governing_body__name")
	list_select_related = ("governing_body", "governing_body__sport")
	list_per_page = 25

	def region_display(self, obj):
		return obj.get_region_display() if obj.region else "-"

	region_display.short_description = _("Region")


class TeamInline(admin.TabularInline):
	model = Team
	extra = 1
	show_change_link = True
	fields = ("name", "location", "founding_year", "logo", "brand")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
	list_display = (
		"name",
		"league",
		"location",
		"founding_year",
		"has_logo",
		"has_brand",
	)
	list_filter = ("league__governing_body__sport", "league", "downloaded")
	search_fields = ("name", "league__name", "location")
	list_select_related = (
		"league",
		"league__governing_body",
		"league__governing_body__sport",
	)
	list_per_page = 25
	fields = (
		"name",
		"league",
		"location",
		"founding_year",
		"logo",
		"brand",
		"website",
		"downloaded",
	)
	readonly_fields = ("downloaded",)

	def has_logo(self, obj):
		return bool(obj.logo)

	has_logo.boolean = True
	has_logo.short_description = _("Logo")

	def has_brand(self, obj):
		return bool(obj.brand)

	has_brand.boolean = True
	has_brand.short_description = _("Brand")


class BettingLineInline(admin.StackedInline):
	model = BettingLine
	extra = 0
	fields = ("spread", "is_pick", "over", "under", "start_datetime")
	show_change_link = True


@admin.register(ScheduledGame)
class ScheduledGameAdmin(admin.ModelAdmin):
	list_display = (
		"matchup",
		"sport",
		"league",
		"start_datetime",
		"is_finished",
		"score_display",
	)
	list_filter = ("sport", "league", "is_finished", "start_datetime")
	search_fields = ("home_team__name", "away_team__name", "league__name")
	list_select_related = ("sport", "league", "home_team", "away_team", "winner")
	list_per_page = 25
	inlines = [BettingLineInline]
	date_hierarchy = "start_datetime"
	fieldsets = (
		(
			None,
			{
				"fields": (
					"sport",
					"league",
					"home_team",
					"away_team",
					"start_datetime",
					"location",
				)
			},
		),
		(
			_("Game Outcome"),
			{"fields": ("home_team_score", "away_team_score", "winner", "is_finished")},
		),
	)

	def matchup(self, obj):
		return f"{obj.home_team} vs {obj.away_team}"

	matchup.short_description = _("Matchup")

	def score_display(self, obj):
		if obj.home_team_score is not None and obj.away_team_score is not None:
			return f"{obj.home_team_score} - {obj.away_team_score}"
		return "-"

	score_display.short_description = _("Score")


@admin.register(BettingLine)
class BettingLineAdmin(admin.ModelAdmin):
	list_display = (
		"game",
		"spread_display",
		"over_under_display",
		"game__start_datetime",
	)
	list_filter = ("game__sport", "game__league", "is_pick", "game__start_datetime")
	search_fields = ("game__home_team__name", "game__away_team__name")
	list_select_related = (
		"game",
		"game__sport",
		"game__league",
		"game__home_team",
		"game__away_team",
	)
	list_per_page = 25
	date_hierarchy = "game__start_datetime"

	def spread_display(self, obj):
		return f"P{obj.spread}" if obj.is_pick else obj.spread

	spread_display.short_description = _("Spread")

	def over_under_display(self, obj):
		if obj.over and obj.under:
			return f"O{obj.over}/U{obj.under}"
		return "-"

	over_under_display.short_description = _("Over/Under")


class PlayPickInline(admin.TabularInline):
	model = PlayPick
	extra = 0
	fields = ("betting_line", "type", "team", "is_over", "display_pick")
	readonly_fields = ("display_pick",)

	def display_pick(self, obj):
		return str(obj)

	display_pick.short_description = _("Pick Details")


@admin.register(Play)
class PlayAdmin(admin.ModelAdmin):
	list_display = ("id", "user", "amount", "placed_datetime", "paid", "won")
	list_filter = ("paid", "won", "placed_datetime", "user")
	search_fields = ("user__username", "user__email")
	list_select_related = ("user",)
	list_per_page = 25
	inlines = [PlayPickInline]
	date_hierarchy = "placed_datetime"
	fieldsets = (
		(None, {"fields": ("user", "amount", "placed_datetime")}),
		(_("Status"), {"fields": ("paid", "won")}),
	)


@admin.register(PlayPick)
class PlayPickAdmin(admin.ModelAdmin):
	list_display = ("play", "betting_line", "type_display", "team", "is_over_display")
	list_filter = ("type", "is_over", "play__user", "betting_line__game__sport")
	search_fields = (
		"play__user__username",
		"betting_line__game__home_team__name",
		"betting_line__game__away_team__name",
	)
	list_select_related = (
		"play",
		"play__user",
		"betting_line",
		"betting_line__game",
		"team",
	)
	list_per_page = 25

	def type_display(self, obj):
		return obj.get_type_display()

	type_display.short_description = _("Type")

	def is_over_display(self, obj):
		if obj.is_over is None:
			return "-"
		return "Over" if obj.is_over else "Under"

	is_over_display.short_description = _("Over/Under")


admin.site = SportsbettingAdminSite(name="sportsbetting_admin")
