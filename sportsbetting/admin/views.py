import logging
from datetime import datetime

import dateutil
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.translation import translation_text as _
from django.views.generic import FormView

from ..forms import GenerateTicketForm
from ..models import GoverningBody, ScheduledGame, Sport, Team
from ..resources import BettingLineResource

logger = logging.getLogger(__name__)


class GenerateTicketView(LoginRequiredMixin, FormView):
    """Admin view to generate a ticket spreadsheet from API data."""

    template_name = "admin/sportsbetting/generate_ticket.html"
    form_class = GenerateTicketForm

    def form_valid(self, form):
        selected_keys = form.get_selected_keys()
        if not selected_keys:
            messages.warning(
                self.request,
                _("No sports selected. Please choose at least one option."),
            )
            return self.form_invalid(form)

        # Initialize resource for export
        resource = BettingLineResource()
        dataset = []

        # Fetch and process API data
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
                response.raise_for_status()
                remaining = response.headers.get("X-Requests-Remaining")
                data = response.json()
            except requests.RequestException as e:
                messages.error(
                    self.request, _("Error fetching sports data: %s") % str(e)
                )
                logger.error("API request failed: %s", str(e))
                return self.form_invalid(form)

            for game_data in data:
                try:
                    spread, totals = self._extract_markets(game_data)
                    if spread is None or totals is None:
                        messages.warning(
                            self.request,
                            _(
                                "Skipping game (api_id: %s) due to missing spread or totals."
                            )
                            % game_data.get("id"),
                        )
                        continue

                    # Resolve Sport and Teams
                    sport, _ = Sport.objects.get_or_create(
                        name=game_data.get("sport_title")
                    )
                    home_team = self._get_or_create_team(
                        sport, game_data.get("home_team")
                    )
                    away_team = self._get_or_create_team(
                        sport, game_data.get("away_team")
                    )

                    # Resolve GoverningBody
                    governing_body = self._resolve_governing_body(sport, home_team)
                    if not governing_body:
                        messages.warning(
                            self.request,
                            _("No governing body for game (api_id: %s).")
                            % game_data.get("id"),
                        )
                        continue

                    # Parse commence time
                    commence_time = self._parse_commence_time(
                        game_data.get("commence_time")
                    )
                    if not commence_time:
                        messages.warning(
                            self.request,
                            _("Invalid commence time for game (api_id: %s).")
                            % game_data.get("id"),
                        )
                        continue

                    # Create temporary ScheduledGame
                    scheduled_game, _ = ScheduledGame.objects.get_or_create(
                        sport=sport,
                        governing_body=governing_body,
                        home_team=home_team,
                        away_team=away_team,
                        start_datetime__date=commence_time.date(),
                        defaults={"start_datetime": commence_time},
                    )

                    # Prepare BettingLine data
                    spread_value = f"P{abs(int(spread))}" if spread < 0 else int(spread)
                    row = {
                        "sport": sport.name,
                        "governing_body": governing_body.name,
                        "home_team": home_team.name,
                        "away_team": away_team.name,
                        "commence_time": commence_time.isoformat(),
                        "spread": spread_value,
                        "over": int(totals + settings.SPORTS.get("TOTALS_SPREAD", 0)),
                        "under": int(totals - settings.SPORTS.get("TOTALS_SPREAD", 0)),
                    }
                    dataset.append(row)

                except Exception as e:
                    messages.warning(
                        self.request,
                        _("Error processing game (api_id: %s): %s")
                        % (game_data.get("id"), str(e)),
                    )
                    logger.error(
                        "Error processing game %s: %s", game_data.get("id"), str(e)
                    )
                    continue

        # Export dataset using BettingLineResource
        export_dataset = resource.export(data=dataset)
        csv_content = export_dataset.csv

        # Prepare response
        response = HttpResponse(
            csv_content,
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="ticket.csv"'},
        )

        if remaining:
            messages.info(
                self.request, _("You have %s sports data pulls left.") % remaining
            )
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
                "title": _("Generate Ticket"),
                "opts": ScheduledGame._meta,
                "sports": choices,
            }
        )
        return context

    def _extract_markets(self, game_data: dict) -> tuple[float, float]:
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
        """Get or create a Team with ASCII-safe name."""
        clean_name = name.encode("ascii", "ignore").decode()
        return Team.objects.get_or_create(sport=sport, name=clean_name)[0]

    def _resolve_governing_body(self, sport: Sport, home_team: Team) -> GoverningBody:
        """Resolve governing body from home team or sport."""
        governing_body = getattr(home_team, "governing_body", None)
        if not governing_body:
            governing_bodies = GoverningBody.objects.filter(sport=sport)
            if governing_bodies.count() == 1:
                governing_body = governing_bodies.first()
        return governing_body

    def _parse_commence_time(self, commence_time: str) -> datetime:
        """Parse commence time based on UNIX_TIME setting."""
        try:
            if settings.SPORTS.get("UNIX_TIME"):
                return timezone.make_aware(datetime.fromtimestamp(int(commence_time)))
            return timezone.make_aware(dateutil.parser.parse(commence_time))
        except (ValueError, TypeError):
            return None
