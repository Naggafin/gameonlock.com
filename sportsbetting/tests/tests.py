from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock, patch
from sportsbetting.models import Sport, GoverningBody, Team  # Import necessary models

import requests
from django.conf import settings
from django.core import mail
from django.test import TestCase

from sportsbetting.models import BettingLine, Game, Pick, Play, Team
from sportsbetting.tasks import (
    fetch_and_store_team_data,
    notify_admin_of_issues,
    resolve_play_outcomes,
    sync_game_scores,
)


class SportsBettingTasksTests(TestCase):
    def setUp(self):
        # Setup test data for games and plays
        # First, create necessary related objects
        sport = Sport.objects.create(name="Test Sport")
        governing_body = GoverningBody.objects.create(sport=sport, name="Test GB", type="pro")
        self.team1 = Team.objects.create(name="Team 1", governing_body=governing_body)
        self.team2 = Team.objects.create(name="Team 2", governing_body=governing_body)
        self.game = Game.objects.create(
            sport=sport,
            governing_body=governing_body,
            home_team=self.team1,
            away_team=self.team2,
            start_datetime=datetime.now(),
        )
        self.betting_line = BettingLine.objects.create(
            game=self.game, spread=-3.5, over=45.5, under=45.5  # Added under to satisfy constraint
        )
        self.play = Play.objects.create(user_id=1, amount=10.00, status="pending")
        self.pick1 = Pick.objects.create(
            play=self.play,
            betting_line=self.betting_line,
            type="sp",
            team=self.team1,
        )
        self.pick2 = Pick.objects.create(
            play=self.play,
            betting_line=self.betting_line,
            type="uo",
            is_over=True,
        )

    @patch("requests.get")
    def test_sync_game_scores_success(self, mock_get):
        # Mock API response for successful score sync
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "games": [
                {"id": "G1", "status": "completed", "home_score": 24, "away_score": 21}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Run the task
        result = sync_game_scores()

        # Check if game was updated
        self.game.refresh_from_db()
        self.assertEqual(self.game.status, "completed")
        self.assertEqual(self.game.home_score, 24)
        self.assertEqual(self.game.away_score, 21)
        self.assertIn("Updated scores for 1 games", result)

    @patch("requests.get")
    def test_sync_game_scores_api_failure(self, mock_get):
        # Mock API failure
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = (
            requests.exceptions.RequestException("API Error")
        )
        mock_get.return_value = mock_response

        # Run the task
        result = sync_game_scores()

        # Check if error was handled and admin notified
        self.assertIn("Failed to sync game scores", result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Score Sync Failure")

    def test_resolve_play_outcomes_won(self):
        # Update game to completed with scores that make picks correct
        self.game.status = "completed"
        self.game.home_score = 24
        self.game.away_score = 20  # Home wins by 4, covers spread of -3.5
        self.game.save()

        # Run the task
        result = resolve_play_outcomes()

        # Check if play was resolved as won
        self.play.refresh_from_db()
        self.assertEqual(self.play.status, "won")
        self.assertGreater(self.play.payout, 0)
        self.assertIn("Resolved 1 plays", result)
        self.assertEqual(len(mail.outbox), 2)  # User and admin notifications
        self.assertEqual(mail.outbox[0].subject, "Play Outcome: Won")
        self.assertEqual(mail.outbox[1].subject, "Play Outcomes Resolved")

    def test_resolve_play_outcomes_lost(self):
        # Update game to completed with scores that make picks incorrect
        self.game.status = "completed"
        self.game.home_score = 20
        self.game.away_score = 24  # Home loses, does not cover spread of -3.5
        self.game.save()

        # Run the task
        result = resolve_play_outcomes()

        # Check if play was resolved as lost
        self.play.refresh_from_db()
        self.assertEqual(self.play.status, "lost")
        self.assertEqual(self.play.payout, 0)
        self.assertIn("Resolved 1 plays", result)
        self.assertEqual(len(mail.outbox), 2)  # User and admin notifications
        self.assertEqual(mail.outbox[0].subject, "Play Outcome: Lost")

    def test_notify_admin_of_issues(self):
        # Run the task
        issue_type = "Test Issue"
        details = "This is a test issue detail."
        result = notify_admin_of_issues(issue_type, details)

        # Check if email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"System Issue: {issue_type}")
        self.assertIn(details, mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertIn(settings.ADMIN_EMAIL, mail.outbox[0].to)
        self.assertIn(f"Admin notified of {issue_type}", result)

    @patch("requests.get")
    def test_fetch_and_store_team_data_success(self, mock_get):
        # Mock API response for team data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "teams": [
                {
                    "strLogo": "http://example.com/logo.jpg",
                    "strBadge": "http://example.com/badge.jpg",
                    "strWebsite": "http://teamwebsite.com",
                    "strLocation": "Test City",
                    "intFormedYear": "2000",
                }
            ]
        }
        mock_response.status_code = HTTPStatus.OK
        mock_response.content = b"image data"
        mock_get.return_value = mock_response

        # Create a team that needs data
        team = Team.objects.create(name="Test Team", downloaded=False)

        # Run the task
        result = fetch_and_store_team_data()

        # Check if team was updated
        team.refresh_from_db()
        self.assertTrue(team.downloaded)
        self.assertEqual(team.website, "http://teamwebsite.com")
        self.assertEqual(team.location, "Test City")
        self.assertEqual(team.founding_year, "2000")
        self.assertIn("Updated 1 teams", result)
