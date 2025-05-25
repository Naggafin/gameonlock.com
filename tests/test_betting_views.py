import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client

import sportsbetting.views

@pytest.mark.django_db
def test_betting_view_requires_login():
    client = Client()
    url = reverse('sportsbetting:bet')
    response = client.get(url)
    assert response.status_code in (302, 401)
    assert '/login' in response.url or response.status_code == 401
