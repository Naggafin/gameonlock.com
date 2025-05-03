import requests
from django.conf import settings
from django.db import migrations
from requests.exceptions import ConnectionError


def create_sports_fixtures(apps, schema_editor):
	Sport = apps.get_model("sportsbetting", "Sport")
	GoverningBody = apps.get_model("sportsbetting", "GoverningBody")

	try:
		sports_data = requests.get(
			url=settings.SPORTS["SPORTS_API_PROVIDER_URL"],
			params={"apiKey": settings.SPORTS["SPORTS_API_KEY"], "all": "true"},
		).json()
	except ConnectionError:
		return

	# Process JSON data to extract sports and governing bodies with keys
	sports = {}
	governing_bodies = {}

	for item in sports_data:
		# Split the key into sport_key and governing_body_key
		key_parts = item["key"].split("_", 1)  # Split on first underscore only
		sport_key = key_parts[0]
		governing_body_key = key_parts[1] if len(key_parts) > 1 else None

		# Map group to sport name
		sport_name = (
			item["group"] if item["group"] != "American Football" else "Football"
		)
		if sport_name not in sports:
			sports[sport_name] = {"key": sport_key}

		# Use title as governing body name
		governing_body_name = item["title"]
		if governing_body_name not in governing_bodies:
			governing_bodies[governing_body_name] = {
				"sport_name": sport_name,
				"key": governing_body_key,
				"description": item["description"],
				# Determine type based on naming conventions
				"type": (
					"col"
					if "ncaa" in governing_body_key.lower()
					or "college" in item["description"].lower()
					else "pro"
				),
			}

	# Create Sports
	for sport_name, sport_data in sports.items():
		Sport.objects.get_or_create(
			name=sport_name,
			defaults={"key": sport_data["key"]},
		)

	# Create Governing Bodies
	for governing_body_name, body_data in governing_bodies.items():
		sport = Sport.objects.get(name=body_data["sport_name"])
		if not GoverningBody.objects.filter(
			sport=sport, name=governing_body_name
		).exists():
			GoverningBody.objects.create(
				sport=sport,
				name=governing_body_name,
				key=body_data["key"],
				type=body_data["type"],
				description=body_data["description"],
			)


class Migration(migrations.Migration):
	dependencies = [("sportsbetting", "0001_initial")]

	operations = [migrations.RunPython(create_sports_fixtures)]
