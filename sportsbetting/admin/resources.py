import logging

import dateutil
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import translation_text as _
from import_export import fields, resources
from import_export.widgets import (
    DateTimeWidget,
    ForeignKeyWidget,
    IntegerWidget,
    Widget,
)

from .models import BettingLine, GoverningBody, ScheduledGame, Sport, Team

logger = logging.getLogger(__name__)


class SpreadValueWidget(Widget):
    """Widget to parse spread value (integer or None) from spread column."""

    def clean(self, value, row=None, **kwargs):
        if not value:
            return None
        try:
            if value.lower().startswith("p"):
                return int(value[1:])
            return int(value)
        except ValueError:
            raise ValidationError(
                _("Invalid spread '%s', expected integer or 'P' followed by integer.")
                % value
            )


class SpreadIsPickWidget(Widget):
    """Widget to parse is_pick boolean from spread column."""

    def clean(self, value, row=None, **kwargs):
        if not value:
            return False
        return value.lower().startswith("p")


class ScheduledGameResource(resources.ModelResource):
    """Resource for ScheduledGame model, used by BettingLineResource."""

    sport = fields.Field(
        column_name="sport",
        attribute="sport",
        widget=ForeignKeyWidget(Sport, field="name", use_natural_keys=True),
    )
    governing_body = fields.Field(
        column_name="governing_body",
        attribute="governing_body",
        widget=ForeignKeyWidget(GoverningBody, field="name", use_natural_keys=True),
        default=None,
    )
    home_team = fields.Field(
        column_name="home_team",
        attribute="home_team",
        widget=ForeignKeyWidget(Team, field="name", use_natural_keys=True),
    )
    away_team = fields.Field(
        column_name="away_team",
        attribute="away_team",
        widget=ForeignKeyWidget(Team, field="name", use_natural_keys=True),
    )
    start_datetime = fields.Field(
        column_name="commence_time",
        attribute="start_datetime",
        widget=DateTimeWidget(),
    )

    class Meta:
        model = ScheduledGame
        fields = (
            "id",
            "sport",
            "governing_body",
            "home_team",
            "away_team",
            "start_datetime",
        )
        import_id_fields = [
            "sport",
            "governing_body",
            "home_team",
            "away_team",
            "start_datetime",
        ]
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Validate and prepare row data before import."""
        required_fields = ["sport", "home_team", "away_team", "commence_time"]
        for field in required_fields:
            if not row.get(field):
                raise ValidationError(_("Missing required field '%s'.") % field)

        commence_time_str = row.get("commence_time", "").strip()
        try:
            commence_time = dateutil.parser.parse(commence_time_str)
            row["commence_time"] = timezone.make_aware(commence_time)
        except Exception as e:
            raise ValidationError(
                _("Invalid commence_time format '%s'.") % commence_time_str
            ) from e

    def after_import_row(self, row, row_result, **kwargs):
        """Create or fetch Team instances and resolve governing_body."""
        sport_name = row.get("sport", "").strip()
        governing_body_name = row.get("governing_body", "").strip()
        home_team_name = row.get("home_team", "").strip().title()
        away_team_name = row.get("away_team", "").strip().title()

        try:
            sport = Sport.objects.filter(Q(name__iexact=sport_name)).get()
        except Sport.DoesNotExist:
            raise ValidationError(_("Sport '%s' not found.") % sport_name)

        if not governing_body_name:
            try:
                home_team_obj = Team.objects.filter(name__iexact=home_team_name).first()
                if home_team_obj:
                    governing_body = home_team_obj.governing_body
                else:
                    governing_bodies = GoverningBody.objects.filter(sport=sport)
                    if governing_bodies.count() == 1:
                        governing_body = governing_bodies.first()
                    else:
                        # Future enhancement: Consider API call to fetch governing body data
                        raise ValidationError(
                            _("Could not resolve governing body. Please specify.")
                        )
            except Exception as e:
                raise ValidationError(_("Could not resolve governing body.")) from e
        else:
            try:
                governing_body = GoverningBody.objects.filter(
                    Q(name__iexact=governing_body_name)
                ).get()
            except GoverningBody.DoesNotExist:
                raise ValidationError(
                    _("Governing body '%s' not found.") % governing_body_name
                )

        home_team_obj, _ = Team.objects.get_or_create(
            name=home_team_name, governing_body=governing_body
        )
        away_team_obj, _ = Team.objects.get_or_create(
            name=away_team_name, governing_body=governing_body
        )

        row["home_team"] = home_team_obj.name
        row["away_team"] = away_team_obj.name
        row["governing_body"] = governing_body.name if governing_body else None


class BettingLineResource(resources.ModelResource):
    """Resource for importing/exporting BettingLine data, including ScheduledGame dependencies."""

    game = fields.Field(
        column_name="game",
        attribute="game",
        widget=ForeignKeyWidget(ScheduledGame, use_natural_keys=True),
    )
    sport = fields.Field(
        column_name="sport",
        attribute="game__sport",
        widget=ForeignKeyWidget(Sport, field="name", use_natural_keys=True),
    )
    governing_body = fields.Field(
        column_name="governing_body",
        attribute="game__governing_body",
        widget=ForeignKeyWidget(GoverningBody, field="name", use_natural_keys=True),
        default=None,
    )
    home_team = fields.Field(
        column_name="home_team",
        attribute="game__home_team",
        widget=ForeignKeyWidget(Team, field="name", use_natural_keys=True),
    )
    away_team = fields.Field(
        column_name="away_team",
        attribute="game__away_team",
        widget=ForeignKeyWidget(Team, field="name", use_natural_keys=True),
    )
    commence_time = fields.Field(
        column_name="commence_time",
        attribute="game__start_datetime",
        widget=DateTimeWidget(),
    )
    spread = fields.Field(
        attribute="spread",
        column_name="spread",
        widget=SpreadValueWidget(),
    )
    is_pick = fields.Field(
        attribute="is_pick",
        column_name="spread",
        widget=SpreadIsPickWidget(),
    )
    over = fields.Field(
        attribute="over",
        column_name="over",
        widget=IntegerWidget(),
    )
    under = fields.Field(
        attribute="under",
        column_name="under",
        widget=IntegerWidget(),
    )

    class Meta:
        model = BettingLine
        fields = (
            "id",
            "sport",
            "governing_body",
            "home_team",
            "away_team",
            "commence_time",
            "spread",
            "over",
            "under",
        )
        export_order = fields
        import_id_fields = [
            "sport",
            "governing_body",
            "home_team",
            "away_team",
            "commence_time",
        ]
        skip_unchanged = True
        report_skipped = True
        use_transactions = True

    def before_import_row(self, row, **kwargs):
        """Validate row data before import."""
        required_fields = ["sport", "home_team", "away_team", "commence_time"]
        for field in required_fields:
            if not row.get(field):
                raise ValidationError(_("Missing required field '%s'.") % field)

        if not (row.get("spread") or (row.get("over") and row.get("under"))):
            raise ValidationError(_("Spread or over/under must be provided."))

        over = row.get("over")
        under = row.get("under")
        if bool(over) != bool(under):
            raise ValidationError(_("Both over and under must be provided or neither."))
        if over and under and int(under) > int(over):
            raise ValidationError(_("Over value is less than the under value."))

    def after_import_row(self, row, row_result, **kwargs):
        """Create or update ScheduledGame and Team before saving BettingLine."""
        request = kwargs.get("request")
        sport_name = row.get("sport", "").strip()
        governing_body_name = row.get("governing_body", "").strip()
        home_team_name = row.get("home_team", "").strip().title()
        away_team_name = row.get("away_team", "").strip().title()
        commence_time = row.get("commence_time")

        scheduled_game_data = {
            "sport": sport_name,
            "governing_body": governing_body_name,
            "home_team": home_team_name,
            "away_team": away_team_name,
            "commence_time": commence_time,
        }
        scheduled_game_resource = ScheduledGameResource()
        dataset = scheduled_game_resource.export(data=[scheduled_game_data])
        result = scheduled_game_resource.import_data(
            dataset,
            dry_run=False,
            raise_errors=True,
            use_transactions=True,
            request=request,
        )

        if result.has_errors():
            for error in result.row_errors():
                raise ValidationError(
                    _("Failed to create ScheduledGame: %s") % error[1][0].error
                )

        scheduled_game = ScheduledGame.objects.get(
            sport__name__iexact=sport_name,
            governing_body__name__iexact=governing_body_name
            if governing_body_name
            else None,
            home_team__name=home_team_name,
            away_team__name=away_team_name,
            start_datetime__date=commence_time.date(),
        )

        row["game"] = scheduled_game

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        """Log import completion and errors."""
        request = kwargs.get("request")
        if result.has_errors():
            for error in result.row_errors():
                logger.error("Import error on row %d: %s", error[0], error[1][0].error)
        else:
            messages.success(request, _("Successfully imported betting lines."))
            logger.info("Successfully imported %d betting lines", len(dataset))
