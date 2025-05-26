from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from sportsbetting.models import Team
from sportsbetting.tasks import fetch_and_store_team_data

class CeleryTaskTests(TestCase):
    def setUp(self):
        from sportsbetting.models import Sport, GoverningBody
        self.sport = Sport.objects.create(name="Soccer")
        self.gov_body = GoverningBody.objects.create(sport=self.sport, name="FIFA", type="pro")
        self.team = Team.objects.create(name="Test Team", downloaded=False, governing_body=self.gov_body)

    @patch("sportsbetting.tasks.requests.get")
    def test_fetch_and_store_team_data_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake image data"
        mock_get.return_value = mock_response

        fetch_and_store_team_data()
        self.team.refresh_from_db()
        self.assertTrue(self.team.downloaded)

    @patch("sportsbetting.tasks.requests.get")
    def test_fetch_and_store_team_data_no_teams(self, mock_get):
        Team.objects.all().delete()
        fetch_and_store_team_data()
        mock_get.assert_not_called()
