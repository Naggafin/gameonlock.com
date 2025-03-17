from django.db import migrations


def create_sports_fixtures(apps, schema_editor):
	Sport = apps.get_model("sportsbetting", "Sport")
	GoverningBody = apps.get_model("sportsbetting", "GoverningBody")
	League = apps.get_model("sportsbetting", "League")

	# Data structure representing the hierarchy
	sports_data = {
		"Football": {
			"governing_bodies": [
				{"name": "NFL", "type": "pro", "leagues": ["AFC", "NFC"]},
				{
					"name": "NCAA Football",
					"type": "col",
					"leagues": ["SEC", "Big Ten", "Pac-12"],
				},
			]
		},
		"Basketball": {
			"governing_bodies": [
				{
					"name": "NBA",
					"type": "pro",
					"leagues": ["Eastern Conference", "Western Conference"],
				},
				{
					"name": "NCAA Basketball",
					"type": "col",
					"leagues": ["ACC", "Big East", "Big 12"],
				},
			]
		},
		"Baseball": {
			"governing_bodies": [
				{
					"name": "MLB",
					"type": "pro",
					"leagues": ["American League", "National League"],
				},
			]
		},
		"Hockey": {
			"governing_bodies": [
				{
					"name": "NHL",
					"type": "pro",
					"leagues": ["Eastern Conference", "Western Conference"],
				}
			]
		},
	}

	# Iterate over sports and their governing bodies
	for sport_name, data in sports_data.items():
		sport, _ = Sport.objects.get_or_create(name=sport_name)

		for body_data in data["governing_bodies"]:
			governing_body, _ = GoverningBody.objects.get_or_create(
				sport=sport, name=body_data["name"], type=body_data["type"]
			)

			# Create associated leagues
			for league_name in body_data["leagues"]:
				League.objects.get_or_create(
					governing_body=governing_body, name=league_name, region="na"
				)


class Migration(migrations.Migration):
	dependencies = [("sportsbetting", "0001_initial")]

	operations = [migrations.RunPython(create_sports_fixtures)]
