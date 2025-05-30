import json
import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from slugify import slugify

from sportsbetting.models import GoverningBody, League, Pick, Sport, Team

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
        queryset = Sport.objects.all()
        if queryset.exists():
            data = serializers.serialize("json", queryset)
            objs = json.loads(data)
            sports = {i["pk"]: i for i in objs}
        else:
            sports = {}
            for i, sport in enumerate(SPORTS, 1):
                sport = {
                    "model": "sportsbetting.Sport",
                    "pk": i,
                    "fields": {
                        "name": sport["name"],
                        "description": sport["description"],
                        "slug_name": slugify(sport["name"]),
                    },
                }
                sports[i] = sport
                fixtures.append(sport)

        # GoverningBody fixtures
        queryset = GoverningBody.objects.all()
        if queryset.exists():
            data = serializers.serialize("json", queryset)
            objs = json.loads(data)
            governing_bodies = {i["pk"]: i for i in objs}
        else:
            governing_bodies = {}
            for i, gb_name in enumerate(GOVERNING_BODIES, 1):
                sport = random.choice(list(sports.values()))
                gb = {
                    "model": "sportsbetting.GoverningBody",
                    "pk": i,
                    "fields": {
                        "sport": sport["pk"],
                        "name": gb_name,
                        "type": random.choice([t[0] for t in GoverningBody.TYPES]),
                    },
                }
                governing_bodies[i] = gb
                fixtures.append(gb)

        # League fixtures
        queryset = League.objects.all()
        if queryset.exists():
            data = serializers.serialize("json", queryset)
            objs = json.loads(data)
            league_names = {i["pk"]: i for i in objs}
        else:
            leagues = {}
            for gb in governing_bodies.values():
                league_names = LEAGUE_NAMES.copy()
                for _ in range(2):
                    id = len(leagues) + 1
                    name = f"{league_names.pop(random.randint(0, len(league_names) - 1))} {gb['pk']}"
                    league = {
                        "model": "sportsbetting.League",
                        "pk": id,
                        "fields": {
                            "governing_body": gb["pk"],
                            "name": name,
                            "region": random.choice([r[0] for r in League.REGIONS]),
                        },
                    }
                    leagues[id] = league
                    fixtures.append(league)

        # Division fixtures
        """
		division_count = 0
		for league['pk'] in range(1, league_count + 1):
			for _ in range(2):  # 2 divisions per league
				division_count += 1
				fixtures.append(
					{
						"model": "sportsbetting.Division",
						"pk": division_count,
						"fields": {
							"league": league['pk'],
							"name": f"{DIVISION_NAMES[division_count % len(DIVISION_NAMES)]} {league['pk']}",
							"hierarchy_level": random.randint(1, 3),
						},
					}
				)
		"""

        # Team fixtures
        queryset = Team.objects.all()
        if queryset.exists():
            data = serializers.serialize("json", queryset)
            objs = json.loads(data)
            teams = {i["pk"]: i for i in objs}
        else:
            teams = {}
            for league in leagues.values():
                for _ in range(4):
                    # division_id = random.randint(1, division_count) if random.random() > 0.51 else None
                    id = len(teams) + 1
                    location = random.choice(TEAM_LOCATIONS)
                    name = f"{location} {fake.word().capitalize()}"
                    if (
                        (name, league["pk"]) in used_combinations
                    ):  # or ((name, division_id) in used_combinations):
                        continue
                    used_combinations.add((name, ("league", league["pk"])))
                    # used_combinations.add((name, ("division", division_id)))
                    team = {
                        "model": "sportsbetting.Team",
                        "pk": id,
                        "fields": {
                            "governing_body": league["fields"]["governing_body"],
                            "league": league["pk"],
                            # "division": division_id,
                            "name": name,
                            "location": location,
                            "founding_year": random.randint(1900, 2023),
                        },
                    }
                    teams[id] = team
                    fixtures.append(team)

        # Player fixtures
        """
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
				league['pk'] = teams[team_id]["fields"]["league"]
				governing_body_id = leagues[league['pk']]["fields"]["governing_body"]
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
		"""

        # Game fixtures
        games = {}
        for league in leagues.values():
            gb = governing_bodies[league["fields"]["governing_body"]]
            for _ in range(10):
                base_datetime = timezone.now()

                while True:
                    filtered_teams = [
                        team
                        for team in teams.values()
                        if team["fields"]["governing_body"] == gb["pk"]
                        and team["fields"]["league"] == league["pk"]
                    ]
                    home_team = filtered_teams.pop(
                        random.randint(0, len(filtered_teams) - 1)
                    )
                    away_team = filtered_teams.pop(
                        random.randint(0, len(filtered_teams) - 1)
                    )
                    game_key = (
                        home_team["pk"],
                        away_team["pk"],
                        str(base_datetime.date()),
                    )
                    if game_key in used_combinations:
                        continue
                    break
                used_combinations.add(game_key)

                id = len(games) + 1
                game = {
                    "model": "sportsbetting.Game",
                    "pk": id,
                    "fields": {
                        "sport": gb["fields"]["sport"],
                        "governing_body": gb["pk"],
                        "league": league["pk"],
                        "home_team": home_team["pk"],
                        "away_team": away_team["pk"],
                        "location": fake.city(),
                        "start_datetime": (
                            base_datetime + timedelta(days=random.randint(0, 30))
                        ).isoformat(),
                    },
                }
                games[id] = game
                fixtures.append(game)

        # BettingLine fixtures
        betting_lines = {}
        for game in games.values():
            over_under = True if random.random() > 0.50 else False
            if over_under:
                under = 101
                over = random.randint(31, 100)
                while under > over:
                    under = random.randint(30, 100)
            id = len(betting_lines) + 1
            betting_line = {
                "model": "sportsbetting.BettingLine",
                "pk": id,
                "fields": {
                    "game": game["pk"],
                    "spread": round(random.uniform(-10, 10), 1),
                    "is_pick": random.choice([True, False]),
                    "over": over if over_under else None,
                    "under": under if over_under else None,
                },
            }
            betting_lines[id] = betting_line
            fixtures.append(betting_line)

        # Play and Pick fixtures (assuming 2 users exist)
        plays = {}
        users = User.objects.filter(is_active=True)
        for _ in range(5 * len(users)):
            id = len(plays) + 1
            user = random.choice(users)
            play = {
                "model": "sportsbetting.Play",
                "pk": id,
                "fields": {
                    "user": user.pk,
                    "amount": f"{random.uniform(10, 1000):.2f}",
                    "placed_datetime": timezone.now().isoformat(),
                },
            }
            plays[id] = play
            fixtures.append(play)

        picks = {}
        for play in plays.values():
            unique_pick = set()
            for _ in range(4):
                while True:
                    betting_line = random.choice(list(betting_lines.values()))
                    game = games[betting_line["fields"]["game"]]
                    type = random.choice([t[0] for t in Pick.TYPES])
                    pick_key = (play["pk"], betting_line["pk"], type)
                    if pick_key not in unique_pick:
                        break
                unique_pick.add(pick_key)

                id = len(picks) + 1
                pick = {
                    "model": "sportsbetting.Pick",
                    "pk": id,
                    "fields": {
                        "play": play["pk"],
                        "betting_line": betting_line["pk"],
                        "type": type,
                        "team": random.choice(
                            [
                                game["fields"]["home_team"],
                                game["fields"]["away_team"],
                            ]
                        )
                        if type == Pick.TYPES.spread
                        else None,
                        "is_over": random.choice([True, False])
                        if type == Pick.TYPES.under_over
                        else None,
                    },
                }
                picks[id] = pick
                fixtures.append(pick)

        return fixtures

    def save_fixtures(self, fixtures, filename="data.json"):
        path = settings.BASE_DIR / "sportsbetting" / "fixtures"
        path.mkdir(parents=True, exist_ok=True)
        with open(path / filename, "w") as f:
            json.dump(fixtures, f, indent=2)
