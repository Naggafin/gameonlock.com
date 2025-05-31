import pytest
from django.test import Client
from django.urls import reverse

from sportsbetting.models import GoverningBody, Sport, Team


@pytest.mark.django_db
def test_betting_view_requires_login():
    client = Client()
    url = reverse("sportsbetting:bet")
    response = client.get(url)
    assert response.status_code in (302, 401)
    assert "/login" in response.url or response.status_code == 401


@pytest.mark.django_db
def test_admin_upload_ticket_requires_login():
    client = Client()
    url = reverse("admin:upload_ticket")
    response = client.get(url)
    assert response.status_code in (302, 401)
    assert "/login" in response.url or response.status_code == 401


@pytest.mark.django_db
def test_admin_generate_ticket_requires_login():
    client = Client()
    url = reverse("admin:sportsbetting_generate_ticket")
    response = client.get(url)
    assert response.status_code in (302, 401)
    assert "/login" in response.url or response.status_code == 401


@pytest.mark.django_db
def test_admin_upload_ticket_invalid_file(client, django_user_model):
    # Log in as admin
    user = django_user_model.objects.create_superuser(
        "admin", "admin@example.com", "password"
    )
    client.force_login(user)
    url = reverse("admin:upload_ticket")
    # No file uploaded
    response = client.post(url, {})
    assert response.status_code == 200
    assert b"No file uploaded" in response.content

    # Create required Sport and Team objects
    sport = Sport.objects.create(name="Football")
    governing_body = GoverningBody.objects.create(sport=sport, name="NFL", type="pro")
    Team.objects.create(name="TeamA", governing_body=governing_body)  # noqa: F841
    Team.objects.create(name="TeamB", governing_body=governing_body)  # noqa: F841


@pytest.mark.django_db
def test_admin_upload_ticket_valid_file(client, django_user_model, tmp_path):
    user = django_user_model.objects.create_superuser(
        "admin", "admin@example.com", "password"
    )
    client.force_login(user)
    # Create required Sport and Team objects
    sport = Sport.objects.create(name="Football")
    governing_body = GoverningBody.objects.create(sport=sport, name="NFL", type="pro")
    Team.objects.create(name="TeamA", governing_body=governing_body)  # noqa: F841
    Team.objects.create(name="TeamB", governing_body=governing_body)  # noqa: F841

    url = reverse("admin:upload_ticket")
    # Debug: print all Sport objects
    print("DEBUG: Sports in DB:", list(Sport.objects.all().values()))

    # Minimal valid CSV
    csv_content = "sport,home_team,away_team,spread,commence_time\nFootball,TeamA,TeamB,3,2025-06-01T12:00:00\n"
    file_path = tmp_path / "ticket.csv"
    file_path.write_text(csv_content)
    with open(file_path, "rb") as f:
        response = client.post(url, {"file": f})
    # Should redirect to admin:index on success
    assert response.status_code == 302
    assert reverse("admin:index") in response.url
