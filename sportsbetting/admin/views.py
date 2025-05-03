import csv
import datetime
import io
from typing import Optional

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import FormView

from ..models import Sport, Team
from . import admin
from .forms import GenerateTicketForm


class GenerateTicketView(FormView):
	"""A standalone admin view to display and generate a ticket spreadsheet."""

	template_name = "admin/sportsbetting/generate_ticket.html"
	form_class = GenerateTicketForm

	def form_valid(self, form):
		selected_keys = form.get_selected_keys()
		if not selected_keys:
			messages.warning(
				self.request, "No sports selected. Please choose at least one option."
			)
			return self.form_invalid(form)

		# Generate CSV in memory
		csv_buffer = io.StringIO()
		pair_prominence = settings.SPORTS["PAIR_PROMINENCE"]
		fields = self._get_csv_fields(pair_prominence)
		spreadsheet = csv.DictWriter(csv_buffer, fieldnames=fields)
		spreadsheet.writeheader()

		# Fetch and process data for each selected key
		for key in selected_keys:
			params = {
				"apiKey": settings.SPORTS["SPORTS_API_KEY"],
				"regions": "us",
				"markets": "spreads,totals",
				"oddsFormat": "american",
			}
			if settings.SPORTS.get("UNIX_TIME"):
				params["dateFormat"] = "unix"

			try:
				api_url = f"{settings.SPORTS['SPORTS_API_PROVIDER_URL']}/{key}/odds"
				response = requests.get(url=api_url, params=params)
				remaining = response.headers.get("X-Requests-Remaining")
				data = response.json()
			except requests.RequestException as e:
				messages.error(self.request, f"Error fetching sports data: {str(e)}")
				return self.form_invalid(form)

			for game_data in data:
				spread, totals = self._extract_markets(game_data)
				if spread is None or totals is None:
					messages.warning(
						self.request,
						f"Skipping game (api_id: {game_data.get('id')}) due to missing spread or totals.",
					)
					continue

				sport = Sport.objects.get_or_create(name=game_data.get("sport_title"))[
					0
				]
				home_team = self._get_or_create_team(sport, game_data.get("home_team"))
				away_team = self._get_or_create_team(sport, game_data.get("away_team"))
				commence_time = self._parse_commence_time(
					game_data.get("commence_time")
				)

				row = {
					"sport": game_data.get("sport_title"),
					"under": totals - settings.SPORTS.get("TOTALS_SPREAD", 0),
					"over": totals + settings.SPORTS.get("TOTALS_SPREAD", 0),
					"commence_time": commence_time,
					"api_id": game_data.get("id"),
				}
				self._populate_team_fields(
					row, pair_prominence, spread, home_team, away_team
				)
				spreadsheet.writerow(row)

		# Prepare CSV response
		csv_buffer.seek(0)
		response = HttpResponse(
			csv_buffer.getvalue(),
			content_type="text/csv",
			headers={"Content-Disposition": 'attachment; filename="ticket.csv"'},
		)
		csv_buffer.close()

		if remaining:
			messages.info(self.request, f"You have {remaining} sports data pulls left")
		return response

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		sports = Sport.objects.prefetch_related("governing_bodies").all()
		choices = [
			{
				"type": sport.name,
				"games": [
					{"title": gb.name, "key": gb.full_key}
					for gb in sport.governing_bodies.all()
					if sport.key and gb.key
				],
			}
			for sport in sports
		]

		context.update(
			{
				"title": "Generate Ticket",
				"site_title": admin.site.site_title,
				"site_header": admin.site.site_header,
				"site_url": admin.site.site_url,
				"has_permission": admin.site.has_permission(self.request),
				"available_apps": admin.site.get_app_list(self.request),
				"is_popup": False,
				"is_nav_sidebar_enabled": True,
				"form_url": self.request.path,
				"sports": choices,
			}
		)
		return context

	def _get_csv_fields(self, pair_prominence: str) -> list[str]:
		"""Determine CSV field order based on PAIR_PROMINENCE setting."""
		base_fields = ["sport", "under", "over", "commence_time", "api_id"]
		if pair_prominence == "unfavored":
			return ["sport", "unfavored", "spread", "favored"] + base_fields[1:]
		elif pair_prominence == "favored":
			return ["sport", "favored", "spread", "unfavored"] + base_fields[1:]
		return ["sport", "home_team", "spread", "away_team"] + base_fields[1:]

	def _extract_markets(
		self, game_data: dict
	) -> tuple[Optional[float], Optional[float]]:
		"""Extract spread and totals from the first successful bookmaker."""
		spread = totals = None
		for bookmaker in game_data.get("bookmakers", []):
			for market in bookmaker.get("markets", []):
				if spread and totals:
					break
				if market.get("key") == "spreads":
					for outcome in market.get("outcomes", []):
						if outcome.get("point") is not None:
							spread = (
								round(outcome["point"])
								if settings.SPORTS.get("ROUND_SPREADS")
								else float(outcome["point"])
							)
							break
				elif market.get("key") == "totals":
					for outcome in market.get("outcomes", []):
						if outcome.get("point") is not None:
							totals = (
								round(outcome["point"])
								if settings.SPORTS.get("ROUND_TOTALS")
								else float(outcome["point"])
							)
							break
		return spread, totals

	def _get_or_create_team(self, sport: Sport, name: str) -> Team:
		"""Get or create a Team (team) with ASCII-safe name."""
		clean_name = name.encode("ascii", "ignore").decode()
		return Team.objects.get_or_create(type="TM", sport=sport, name=clean_name)[0]

	def _parse_commence_time(self, commence_time: str) -> str:
		"""Parse commence time based on UNIX_TIME setting."""
		if settings.SPORTS.get("UNIX_TIME"):
			return datetime.datetime.fromtimestamp(int(commence_time)).isoformat()
		return commence_time.rstrip("Z")  # Remove trailing 'Z' from ISO format

	def _populate_team_fields(
		self,
		row: dict,
		pair_prominence: str,
		spread: float,
		home_team: Team,
		away_team: Team,
	) -> None:
		"""Populate team-related fields based on PAIR_PROMINENCE."""
		home_name = home_team.short or home_team.name
		away_name = away_team.short or away_team.name

		if pair_prominence == "unfavored":
			if spread < 0:
				row["unfavored"] = home_name
				row["spread"] = spread
				row["favored"] = away_name
			else:
				row["unfavored"] = away_name
				row["spread"] = -spread
				row["favored"] = home_name
		elif pair_prominence == "favored":
			if spread < 0:
				row["favored"] = home_name
				row["spread"] = spread
				row["unfavored"] = away_name
			else:
				row["favored"] = away_name
				row["spread"] = -spread
				row["unfavored"] = home_name
		else:  # home_team
			row["home_team"] = home_name
			row["away_team"] = away_name
			row["spread"] = spread if spread > 0 else -spread
