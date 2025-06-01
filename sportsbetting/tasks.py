from datetime import datetime, timedelta
from http import HTTPStatus

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from slugify import slugify
from sportsipy.mlb.schedule import Schedule as MLBSchedule
from sportsipy.nba.schedule import Schedule as NBASchedule
from sportsipy.ncaab.schedule import Schedule as NCAABSchedule
from sportsipy.ncaaf.schedule import Schedule as NCAAFSchedule
from sportsipy.nfl.schedule import Schedule as NFLSchedule

from .models import Game, GoverningBody, Pick, Play, Team

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3)
def fetch_and_store_team_data(self):
    """Celery task to fetch and store data for all teams that have not been downloaded yet."""
    teams = Team.objects.filter(downloaded=False)  # Get all teams needing data

    if not teams.exists():
        logger.info("No teams require data fetching.")
        return "No teams to update."

    for team in teams:
        try:
            api_url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team.name}"
            response = requests.get(api_url, timeout=10)

            if response.status_code == HTTPStatus.OK:
                data = response.json()
                team_data = None
                if isinstance(data, dict) and "teams" in data and data["teams"]:
                    team_data = data["teams"][0]
                elif isinstance(data, dict):
                    team_data = data
                else:
                    team_data = {}

                logo_url = team_data.get("strLogo")
                brand_url = team_data.get("strBadge")
                website = team_data.get("strWebsite")
                location = team_data.get("strLocation")
                founding_year = team_data.get("intFormedYear")

                team.website = website
                team.location = location
                team.founding_year = founding_year
                team.downloaded = True

                if logo_url and not team.logo:
                    filename = f"{slugify(team.name)}_logo.jpg"
                    image = download_image(logo_url)
                    team.logo.save(filename, image, save=False)

                if brand_url and not team.brand:
                    filename = f"{slugify(team.name)}_brand.jpg"
                    image = download_image(brand_url)
                    team.brand.save(filename, image, save=False)

                team.save(
                    update_fields=[
                        "logo",
                        "brand",
                        "website",
                        "location",
                        "founding_year",
                        "downloaded",
                    ]
                )
                logger.info(f"Successfully updated team: {team.name}")

            else:
                logger.warning(
                    f"API request failed for {team.name}. Status code: {response.status_code}"
                )

        except requests.RequestException as exc:
            logger.error(f"Request failed for team {team.name}: {exc}")
            self.retry(exc=exc, countdown=60)  # Retry after 60 seconds

    return f"Updated {teams.count()} teams."


def download_image(url):
    """Downloads an image."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == HTTPStatus.OK:
            return ContentFile(response.content)
    except requests.RequestException as exc:
        logger.error(f"Failed to download image from {url}: {exc}")
    return None


@shared_task(max_retries=3, rate_limit="1/m")
def fetch_and_sync_games():
    """Fetch and update/create Game data."""
    gbs = GoverningBody.objects.all()
    gb_keys = set(gbs.values_list("key", flat=True))
    gb_map = {
        "nfl": NFLSchedule,
        "nba": NBASchedule,
        "mlb": MLBSchedule,
        "ncaab": NCAABSchedule,
        "ncaaf": NCAAFSchedule,
    }

    for key, schedule in gb_map.items():
        if key not in gb_keys:
            continue
        try:
            gb = gbs.get(key=key)
            for game in schedule:
                if game.result is None:
                    continue
                try:
                    home_team = Team.objects.get_or_create(
                        name=game.home_name, governing_body=gb
                    )[0]
                    away_team = Team.objects.get_or_create(
                        name=game.away_name, governing_body=gb
                    )[0]

                    game = Game.objects.get(
                        governing_body=gb,
                        home_team=home_team,
                        away_team=away_team,
                        start_datetime__date=game.datetime.date(),
                    )
                    game.home_team_score = game.home_points
                    game.away_team_score = game.away_points
                    game.is_finished = True
                    game.save()
                    logger.info(f"Updated scores for {sport} game {game.id}")
                except Game.DoesNotExist:
                    logger.warning(f"Game not found: {game.boxscore_index}")
                except Exception as e:
                    logger.error(
                        f"Error updating {league} game {game.boxscore_index}: {str(e)}"
                    )
        except Exception as e:
            logger.error(f"Failed to sync {league} scores: {str(e)}")


@shared_task(bind=True, max_retries=3, rate_limit="1/s")
def sync_game_scores(self):
    """
    Task to sync game scores from an external API and update the database.
    """
    api_key = settings.SPORTS["SPORTS_API_KEY"]
    url = f"{settings.SPORTS['SPORTS_API_PROVIDER_URL']}/games"
    headers = {"Authorization": f"Bearer {api_key}"}
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        response = requests.get(
            url, headers=headers, params={"date_from": yesterday, "date_to": today}
        )
        response.raise_for_status()
        games_data = response.json()

        updated_games = 0
        for game_data in games_data.get("games", []):
            game_id = game_data.get("id")
            if not game_id:
                continue

            try:
                game = Game.objects.get(external_id=game_id)
                game.status = game_data.get("status", game.status)
                game.home_score = game_data.get("home_score", game.home_score)
                game.away_score = game_data.get("away_score", game.away_score)
                game.updated_at = datetime.now()
                game.save()
                updated_games += 1
            except Game.DoesNotExist:
                continue

        logger.info(f"Updated scores for {updated_games} games")
        return f"Updated scores for {updated_games} games"
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to sync game scores: {str(e)}"
        logger.error(error_msg)
        send_mail(
            subject="Score Sync Failure",
            message=error_msg,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )
        self.retry(exc=e, countdown=60)
        return error_msg


@shared_task
def resolve_play_outcomes():
    """
    Task to resolve outcomes of plays based on game results.
    """
    unresolved_plays = Play.objects.filter(
        status="pending", picks__betting_line__game__status="completed"
    ).distinct()
    resolved_count = 0

    for play in unresolved_plays:
        picks = Pick.objects.filter(play=play)
        if not picks:
            continue

        all_picks_correct = True
        for pick in picks:
            game = pick.game
            betting_line = pick.betting_line

            if pick.pick_type == "sp":  # Spread bet
                if pick.team == game.home_team:
                    score_diff = game.home_score - game.away_score
                    expected_diff = betting_line.home_spread
                else:
                    score_diff = game.away_score - game.home_score
                    expected_diff = -betting_line.home_spread

                if score_diff < expected_diff:
                    all_picks_correct = False
                    break

            elif pick.pick_type == "uo":  # Over/Under bet
                total_score = game.home_score + game.away_score
                if pick.is_over and total_score <= betting_line.over_under:
                    all_picks_correct = False
                    break
                elif not pick.is_over and total_score >= betting_line.over_under:
                    all_picks_correct = False
                    break

        if all_picks_correct:
            play.status = "won"
            play.payout = play.amount * settings.BET_MULTIPLIER
        else:
            play.status = "lost"
            play.payout = 0

        play.resolved_at = datetime.now()
        play.save()
        resolved_count += 1

        # Notify user of outcome
        send_mail(
            subject=f"Play Outcome: {play.status.capitalize()}",
            message=f"Your play with ID {play.id} has been resolved as {play.status}. Payout: {play.payout}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[play.user.email],
            fail_silently=True,
        )

    if resolved_count > 0:
        send_mail(
            subject="Play Outcomes Resolved",
            message=f"Resolved {resolved_count} plays. Check admin dashboard for details.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=True,
        )

    logger.info(f"Resolved {resolved_count} plays")
    return f"Resolved {resolved_count} plays"


@shared_task
def notify_admin_of_issues(issue_type, details):
    """
    Task to notify admin of system issues or anomalies.
    """
    subject = f"System Issue: {issue_type}"
    message = f"An issue of type {issue_type} has been detected. Details: {details}"
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.ADMIN_EMAIL]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    logger.info(f"Admin notified of {issue_type}")
    return f"Admin notified of {issue_type}"
