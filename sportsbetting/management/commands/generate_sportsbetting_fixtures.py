import json
import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from sportsbetting.models import GoverningBody, League, Pick, Sport

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
TEAM_LOCATIONS = [
	"New York",
	"Los Angeles",
	"Chicago",
	"Houston",
	"Miami",
	"Boston",
	"Seattle",
	"Dallas",
	"Atlanta",
	"Phoenix",
	"Denver",
	"Philadelphia",
	"San Francisco",
	"Austin",
	"Portland",
]
TEAM_MASCOTS = [
	"Eagles",
	"Tigers",
	"Bears",
	"Lions",
	"Panthers",
	"Wolves",
	"Hawks",
	"Falcons",
	"Sharks",
	"Vipers",
]
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
		sports = list(Sport.objects.all())
		governing_bodies = list(GoverningBody.objects.select_related("sport"))

		if not sports or not governing_bodies:
			raise RuntimeError(
				"Sports and GoverningBodies must exist. "
				"Run migrations before generating fixtures."
			)

		# League fixtures
		leagues = {}

		for gb in governing_bodies:
			for i in range(2):  # 2 leagues per governing body
				league_id = len(leagues) + 1
				league = {
					"model": "sportsbetting.League",
					"pk": league_id,
					"fields": {
						"governing_body": gb.pk,
						"name": f"{gb.name} League {i + 1}",
						"region": random.choice([r[0] for r in League.REGIONS]),
					},
				}
				leagues[league_id] = league
				fixtures.append(league)

		# Team fixtures
		teams = {}
		used_team_names = set()

		for league in leagues.values():
			for _ in range(4):
				while True:
					location = random.choice(TEAM_LOCATIONS)
					mascot = random.choice(TEAM_MASCOTS)
					name = f"{location} {mascot}"
					key = (name.lower(), league["pk"])
					if key not in used_team_names:
						used_team_names.add(key)
						break

				team_id = len(teams) + 1
				team = {
					"model": "sportsbetting.Team",
					"pk": team_id,
					"fields": {
						"governing_body": league["fields"]["governing_body"],
						"league": league["pk"],
						"name": name,
						"location": location,
						"founding_year": random.randint(1950, 2020),
					},
				}
				teams[team_id] = team
				fixtures.append(team)

		# Game fixtures
		games = {}
		used_games = set()

		for league in leagues.values():
			league_teams = [
				t for t in teams.values() if t["fields"]["league"] == league["pk"]
			]

			for _ in range(random.randint(3, 5)):
				home, away = random.sample(league_teams, 2)
				start = timezone.now() + timedelta(days=random.randint(-3, 10))

				key = (home["pk"], away["pk"], start.date())
				if key in used_games:
					continue
				used_games.add(key)

				game_id = len(games) + 1
				is_finished = start < timezone.now() and random.choice([True, False])

				game = {
					"model": "sportsbetting.Game",
					"pk": game_id,
					"fields": {
						"governing_body": league["fields"]["governing_body"],
						"league": league["pk"],
						"home_team": home["pk"],
						"away_team": away["pk"],
						"location": fake.city(),
						"start_datetime": start.isoformat(),
						"is_finished": is_finished,
						"home_team_score": random.randint(0, 50)
						if is_finished
						else None,
						"away_team_score": random.randint(0, 50)
						if is_finished
						else None,
						"winner": random.choice([home["pk"], away["pk"]])
						if is_finished
						else None,
					},
				}
				games[game_id] = game
				fixtures.append(game)

		# BettingLine fixtures
		betting_lines = {}

		for game in games.values():
			bl_id = len(betting_lines) + 1
			betting_line = {
				"model": "sportsbetting.BettingLine",
				"pk": bl_id,
				"fields": {
					"game": game["pk"],
					"spread": round(random.uniform(-7, 7), 1),
					"is_pick": True,
					"over": random.randint(40, 100),
					"under": random.randint(30, 90),
				},
			}
			betting_lines[bl_id] = betting_line
			fixtures.append(betting_line)

		# Play and Pick fixtures (assuming 2 users exist)
		users = list(User.objects.filter(is_active=True)[:2])
		plays = {}
		picks = {}

		for user in users:
			for _ in range(2):  # 2 plays per user
				play_id = len(plays) + 1
				play = {
					"model": "sportsbetting.Play",
					"pk": play_id,
					"fields": {
						"user": user.pk,
						"amount": "50.00",
						"placed_datetime": timezone.now().isoformat(),
					},
				}
				plays[play_id] = play
				fixtures.append(play)

				for bl in random.sample(list(betting_lines.values()), 2):
					pick_id = len(picks) + 1
					pick = {
						"model": "sportsbetting.Pick",
						"pk": pick_id,
						"fields": {
							"play": play_id,
							"betting_line": bl["pk"],
							"type": Pick.TYPES.under_over,
							"is_over": random.choice([True, False]),
						},
					}
					picks[pick_id] = pick
					fixtures.append(pick)

		return fixtures

	def save_fixtures(self, fixtures, filename="data.json"):
		path = settings.BASE_DIR / "sportsbetting" / "fixtures"
		path.mkdir(parents=True, exist_ok=True)
		with open(path / filename, "w") as f:
			json.dump(fixtures, f, indent=2)
