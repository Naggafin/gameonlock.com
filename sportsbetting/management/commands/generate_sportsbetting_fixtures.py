import json
import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from slugify import slugify

from sportsbetting.models import GoverningBody, League, PlayPick

User = get_user_model()

fake = Faker()

# Constants
SPORTS = [
	{"name": "Football", "description": "American football"},
	{"name": "Basketball", "description": "Basketball"},
	{"name": "Baseball", "description": "Baseball"},
	{"name": "Soccer", "description": "Association football"},
]
GOVERNING_BODIES = ["NFL", "NBA", "MLB", "MLS", "NCAA"]
LEAGUE_NAMES = [
	"Pro League",
	"Eastern Conference",
	"Western Conference",
	"Premier Division",
]
DIVISION_NAMES = ["Division 1", "Division 2", "North", "South", "East", "West"]
TEAM_LOCATIONS = ["New York", "Los Angeles", "Chicago", "Houston", "Miami"]
POSITIONS = {
	"Football": ["QB", "RB", "WR", "DE"],
	"Basketball": ["PG", "SG", "SF", "PF", "C"],
	"Baseball": ["P", "C", "1B", "2B", "SS"],
	"Soccer": ["GK", "DF", "MF", "FW"],
}


class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		fixtures = self.generate_fixtures()
		self.save_fixtures(fixtures)
		self.stdout.write(
			self.style.SUCCESS("Successfully generated %d fixtures" % len(fixtures))
		)

	def generate_fixtures(self):
		fixtures = []
		used_combinations = set()  # To track unique constraints

		# Sport fixtures
		for i, sport in enumerate(SPORTS, 1):
			fixtures.append(
				{
					"model": "sportsbetting.Sport",
					"pk": i,
					"fields": {
						"name": sport["name"],
						"description": sport["description"],
						"slug_name": slugify(sport["name"]),
					},
				}
			)

		# GoverningBody fixtures
		for i, gb_name in enumerate(GOVERNING_BODIES, 1):
			sport_id = random.randint(1, len(SPORTS))
			fixtures.append(
				{
					"model": "sportsbetting.GoverningBody",
					"pk": i,
					"fields": {
						"sport": sport_id,
						"name": gb_name,
						"type": random.choice([t[0] for t in GoverningBody.TYPES]),
					},
				}
			)

		# League fixtures
		league_count = 0
		for gb_id in range(1, len(GOVERNING_BODIES) + 1):
			for _ in range(2):  # 2 leagues per governing body
				league_count += 1
				name = f"{LEAGUE_NAMES[league_count % len(LEAGUE_NAMES)]} {gb_id}"
				fixtures.append(
					{
						"model": "sportsbetting.League",
						"pk": league_count,
						"fields": {
							"governing_body": gb_id,
							"name": name,
							"region": random.choice([r[0] for r in League.REGIONS]),
						},
					}
				)

		# Division fixtures
		division_count = 0
		for league_id in range(1, league_count + 1):
			for _ in range(2):  # 2 divisions per league
				division_count += 1
				fixtures.append(
					{
						"model": "sportsbetting.Division",
						"pk": division_count,
						"fields": {
							"league": league_id,
							"name": f"{DIVISION_NAMES[division_count % len(DIVISION_NAMES)]} {league_id}",
							"hierarchy_level": random.randint(1, 3),
						},
					}
				)

		# Team fixtures
		team_count = 0
		for league_id in range(1, league_count + 1):
			for _ in range(4):  # 4 teams per league
				team_count += 1
				division_id = (
					random.randint(1, division_count)
					if random.random() > 0.51
					else None
				)
				name = f"{TEAM_LOCATIONS[team_count % len(TEAM_LOCATIONS)]} {fake.word().capitalize()}"
				if ((name, league_id) in used_combinations) or (
					(name, division_id) in used_combinations
				):
					continue
				used_combinations.add((name, ("league", league_id)))
				used_combinations.add((name, ("division", division_id)))
				fixtures.append(
					{
						"model": "sportsbetting.Team",
						"pk": team_count,
						"fields": {
							"league": league_id,
							"division": division_id,
							"name": name,
							"location": TEAM_LOCATIONS[
								team_count % len(TEAM_LOCATIONS)
							],
							"founding_year": random.randint(1900, 2023),
						},
					}
				)

		# Player fixtures
		player_count = 0
		for team_id in range(1, team_count + 1):
			for _ in range(5):  # 5 players per team
				player_count += 1
				teams = {
					i["pk"]: i for i in fixtures if i["model"] == "sportsbetting.Team"
				}
				leagues = {
					i["pk"]: i for i in fixtures if i["model"] == "sportsbetting.League"
				}
				governing_bodies = {
					i["pk"]: i
					for i in fixtures
					if i["model"] == "sportsbetting.GoverningBody"
				}
				sports = {
					i["pk"]: i for i in fixtures if i["model"] == "sportsbetting.Sport"
				}
				league_id = teams[team_id]["fields"]["league"]
				governing_body_id = leagues[league_id]["fields"]["governing_body"]
				sport_id = governing_bodies[governing_body_id]["fields"]["sport"]
				sport_name = sports[sport_id]["fields"]["name"]
				fixtures.append(
					{
						"model": "sportsbetting.Player",
						"pk": player_count,
						"fields": {
							"team": team_id,
							"name": fake.name(),
							"position": random.choice(POSITIONS[sport_name]),
							"jersey_number": random.randint(1, 99),
						},
					}
				)

		# ScheduledGame fixtures
		game_count = 0
		base_date = timezone.now()
		for _ in range(50):  # 50 games
			game_count += 1
			home_team = random.randint(1, team_count)
			away_team = random.randint(1, team_count)
			while home_team == away_team:  # Ensure different teams
				away_team = random.randint(1, team_count)

			teams = {i["pk"]: i for i in fixtures if i["model"] == "sportsbetting.Team"}
			leagues = {
				i["pk"]: i for i in fixtures if i["model"] == "sportsbetting.League"
			}
			governing_bodies = {
				i["pk"]: i
				for i in fixtures
				if i["model"] == "sportsbetting.GoverningBody"
			}
			league_id = teams[home_team]["fields"]["league"]
			governing_body_id = leagues[league_id]["fields"]["governing_body"]
			sport_id = governing_body_id = governing_bodies[governing_body_id][
				"fields"
			]["sport"]

			game_key = (home_team, away_team, str(base_date))
			if game_key in used_combinations:
				continue
			used_combinations.add(game_key)

			fixtures.append(
				{
					"model": "sportsbetting.ScheduledGame",
					"pk": game_count,
					"fields": {
						"sport": sport_id,
						"league": league_id,
						"home_team": home_team,
						"away_team": away_team,
						"location": fake.city(),
						"start_datetime": base_date.isoformat(),
					},
				}
			)
			base_date += timedelta(days=1)

		# BettingLine fixtures
		betting_count = 0
		for game_id in range(1, game_count + 1):
			betting_count += 1
			over_under = True if random.random() > 0.50 else False
			if over_under:
				under = 101
				over = random.randint(31, 100)
				while under > over:
					under = random.randint(30, 100)

			fixtures.append(
				{
					"model": "sportsbetting.BettingLine",
					"pk": betting_count,
					"fields": {
						"game": game_id,
						"spread": round(random.uniform(-10, 10), 1),
						"is_pick": random.choice([True, False]),
						"over": over if over_under else None,
						"under": under if over_under else None,
						"start_datetime": (
							base_date - timedelta(days=game_count - game_id)
						).isoformat(),
					},
				}
			)

		# Play and PlayPick fixtures (assuming 2 users exist)
		play_count = 0
		user_ids = User.objects.filter(is_active=True).values_list("id", flat=True)
		num_users = len(user_ids)
		now = timezone.now().isoformat()
		for _ in range(5 * num_users):  # 5 plays per user
			play_count += 1
			user_id = random.choice(user_ids)
			fixtures.append(
				{
					"model": "sportsbetting.Play",
					"pk": play_count,
					"fields": {
						"user": user_id,
						"amount": f"{random.uniform(10, 1000):.2f}",
						"placed_datetime": now,
					},
				}
			)

		pick_count = 0
		for play_id in range(1, play_count + 1):
			unique_pick = set()
			for _ in range(4):
				pick_count += 1

				betting_lines = {
					i["pk"]: i for i in fixtures if i["model"] == "sportsbetting.Play"
				}
				betting_lines = {
					i["pk"]: i
					for i in fixtures
					if i["model"] == "sportsbetting.BettingLine"
				}
				games = {
					i["pk"]: i
					for i in fixtures
					if i["model"] == "sportsbetting.ScheduledGame"
				}

				while True:
					betting_line_id = random.randint(1, betting_count)
					game_id = betting_lines[betting_line_id]["fields"]["game"]
					game = games[game_id]
					type = random.choice([t[0] for t in PlayPick.TYPES])
					if (play_id, betting_line_id, type) not in unique_pick:
						break
				unique_pick.add((play_id, betting_line_id, type))

				fixtures.append(
					{
						"model": "sportsbetting.PlayPick",
						"pk": pick_count,
						"fields": {
							"play": play_id,
							"betting_line": betting_line_id,
							"type": type,
							"team": random.choice(
								[
									game["fields"]["home_team"],
									game["fields"]["away_team"],
								]
							)
							if type == PlayPick.TYPES.spread
							else None,
							"is_over": random.choice([True, False])
							if type == PlayPick.TYPES.under_over
							else None,
						},
					}
				)

		return fixtures

	def save_fixtures(self, fixtures, filename="fixtures.json"):
		path = settings.BASE_DIR / "fixtures" / filename
		with open(path, "w") as f:
			json.dump(fixtures, f, indent=2)
