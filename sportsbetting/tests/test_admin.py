import csv
import io

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from import_export import resources

from sportsbetting.admin.resources import (
	BettingLineResource,
	GameResource,
	TeamResource,
)
from sportsbetting.models import BettingLine, Game, Team


class AdminImportExportTests(TestCase):
	def setUp(self):
		# Create a superuser for admin access
		self.client = Client()
		self.superuser = User.objects.create_superuser(
			username="admin", email="admin@example.com", password="adminpass123"
		)
		self.client.login(username="admin", password="adminpass123")

		# Create test data
		common_data = create_common_test_data()
		self.team1 = common_data["team1"]
		self.team2 = common_data["team2"]
		self.game = common_data["game"]
		self.betting_line = common_data["betting_line"]

	def test_team_export(self):
		# Test exporting team data
		resource = TeamResource()
		dataset = resource.export()

		self.assertEqual(
			dataset.headers,
			[
				"id",
				"name",
				"external_id",
				"website",
				"location",
				"founding_year",
				"downloaded",
			],
		)
		self.assertEqual(len(dataset), Team.objects.count())
		self.assertEqual(dataset[0][1], "Team 1")  # Check name of first team

	def test_game_export(self):
		# Test exporting game data
		resource = GameResource()
		dataset = resource.export()

		self.assertEqual(
			dataset.headers,
			[
				"id",
				"external_id",
				"home_team",
				"away_team",
				"start_time",
				"status",
				"home_score",
				"away_score",
				"updated_at",
			],
		)
		self.assertEqual(len(dataset), Game.objects.count())
		self.assertEqual(dataset[0][1], "G1")  # Check external_id of first game

	def test_betting_line_export(self):
		# Test exporting betting line data
		resource = BettingLineResource()
		dataset = resource.export()

		self.assertEqual(
			dataset.headers, ["id", "game", "home_spread", "over_under", "updated_at"]
		)
		self.assertEqual(len(dataset), BettingLine.objects.count())
		self.assertEqual(dataset[0][2], -3.5)  # Check home_spread of first betting line

	def test_team_import_valid_data(self):
		# Test importing valid team data
		resource = TeamResource()
		csv_data = io.StringIO()
		writer = csv.writer(csv_data)
		writer.writerow(
			[
				"id",
				"name",
				"external_id",
				"website",
				"location",
				"founding_year",
				"downloaded",
			]
		)
		writer.writerow(
			["", "Team 3", "T3", "http://team3.com", "City 3", "1990", "False"]
		)

		dataset = resources.tablib.Dataset().load(csv_data.getvalue())
		result = resource.import_data(dataset, dry_run=False)

		self.assertFalse(result.has_errors())
		self.assertEqual(Team.objects.count(), 3)
		team3 = Team.objects.get(external_id="T3")
		self.assertEqual(team3.name, "Team 3")
		self.assertEqual(team3.website, "http://team3.com")

	def test_betting_line_import_invalid_data(self):
		# Test importing invalid betting line data (missing game reference)
		resource = BettingLineResource()
		csv_data = io.StringIO()
		writer = csv.writer(csv_data)
		writer.writerow(["id", "game", "home_spread", "over_under", "updated_at"])
		writer.writerow(["", "9999", "-5.5", "48.5", ""])

		dataset = resources.tablib.Dataset().load(csv_data.getvalue())
		result = resource.import_data(dataset, dry_run=False)

		self.assertTrue(result.has_errors())
		self.assertEqual(
			BettingLine.objects.count(), 1
		)  # No new betting line should be added

	def test_admin_access_team_import_export_page(self):
		# Test accessing the admin import/export page for teams
		response = self.client.get(reverse("admin:sportsbetting_team_changelist"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Import")
		self.assertContains(response, "Export")

	def test_admin_access_betting_line_import_export_page(self):
		# Test accessing the admin import/export page for betting lines
		response = self.client.get(
			reverse("admin:sportsbetting_bettingline_changelist")
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Import")
		self.assertContains(response, "Export")
