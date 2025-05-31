from unittest.mock import MagicMock, patch

from django.test import TestCase

from sportsbetting.models import Team
from sportsbetting.tasks import fetch_and_store_team_data


class CeleryTaskTests(TestCase):
    def setUp(self):
        from sportsbetting.tests.helpers import create_common_test_data

        common_data = create_common_test_data()
        self.sport = common_data['sport']
        self.gov_body = common_data['gov_body']
        self.team = common_data['team1']  # Using team1 from helpers as it's similar

    @patch("sportsbetting.tasks.requests.get")
    def test_fetch_and_store_team_data_no_teams(self, mock_get):
        Team.objects.all().delete()
        fetch_and_store_team_data()
        mock_get.assert_not_called()
