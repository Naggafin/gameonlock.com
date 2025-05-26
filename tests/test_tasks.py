import pytest
from unittest.mock import patch, MagicMock
from django.core.files.base import ContentFile
from sportsbetting.tasks import fetch_and_store_team_data
from sportsbetting.models import Team, GoverningBody, Sport

@pytest.mark.django_db
def test_fetch_and_store_team_data_no_teams(caplog):
    caplog.set_level("INFO")
    Team.objects.all().delete()
    result = fetch_and_store_team_data()
    assert result == "No teams to update."
    assert "No teams require data fetching." in caplog.text

@pytest.mark.django_db
def test_fetch_and_store_team_data_success(monkeypatch):
    sport = Sport.objects.create(name="Test Sport")
    gb = GoverningBody.objects.create(name="Test GB", sport=sport, type="pro")
    team = Team.objects.create(name="Test Team", downloaded=False, governing_body=gb)
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "teams": [{
            "strLogo": "http://example.com/logo.jpg",
            "strBadge": "http://example.com/brand.jpg",
            "strWebsite": "http://example.com",
            "strLocation": "Test City",
            "intFormedYear": 2020,
        }]
    }
    monkeypatch.setattr("sportsbetting.tasks.requests.get", lambda *a, **kw: mock_response)
    monkeypatch.setattr("sportsbetting.tasks.download_image", lambda url: ContentFile(b"fakeimg"))
    result = fetch_and_store_team_data()
    team.refresh_from_db()
    assert team.downloaded is True
    assert team.website == "http://example.com"
    assert team.location == "Test City"
    assert team.founding_year == 2020
    assert result.startswith("Updated ")

@pytest.mark.django_db
def test_fetch_and_store_team_data_api_failure(monkeypatch, caplog):
    sport = Sport.objects.create(name="Fail Sport")
    gb = GoverningBody.objects.create(name="Fail GB", sport=sport, type="pro")
    team = Team.objects.create(name="Fail Team", downloaded=False, governing_body=gb)
    mock_response = MagicMock()
    mock_response.status_code = 500
    monkeypatch.setattr("sportsbetting.tasks.requests.get", lambda *a, **kw: mock_response)
    result = fetch_and_store_team_data()
    assert "API request failed for Fail Team" in caplog.text
    assert result.startswith("Updated ")

@pytest.mark.django_db
def test_fetch_and_store_team_data_request_exception(monkeypatch, caplog):
    sport = Sport.objects.create(name="Except Sport")
    gb = GoverningBody.objects.create(name="Except GB", sport=sport, type="pro")
    team = Team.objects.create(name="Except Team", downloaded=False, governing_body=gb)
    import requests
    def raise_exc(*a, **kw):
        raise requests.RequestException("Network error")
    monkeypatch.setattr("sportsbetting.tasks.requests.get", raise_exc)
    with patch.object(fetch_and_store_team_data, 'retry', side_effect=Exception("retry called")) as mock_retry:
        try:
            fetch_and_store_team_data.run()
        except Exception as e:
            assert "retry called" in str(e)
    assert "Request failed for team Except Team" in caplog.text
