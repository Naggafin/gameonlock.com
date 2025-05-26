from http import HTTPStatus

import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.files.base import ContentFile
from slugify import slugify

from .models import Team

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

                team.save(update_fields=["logo", "brand", "website", "location", "founding_year", "downloaded"])
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
