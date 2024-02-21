import pytest

from rest_framework.test import APIClient
from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_403_FORBIDDEN,
    is_success,
)

from api.v1.tests.factories.people import UserFactory

from people.models import ThemesPreferences, User


@pytest.fixture
def make_themes(db):
    u = UserFactory.create(username="pouet")
    ThemesPreferences.objects.create(user=u, theme="pouet_th")
    u = UserFactory.create(username="patate")
    ThemesPreferences.objects.create(user=u, theme="patate_th")


@pytest.fixture
def client():
    return APIClient()


class TestDjangoRules:
    root_endpoint = "/fr/api/v1/people/themes/"

    def test_theme_list(self, make_themes, client):
        user = User.objects.first()
        client.force_authenticate(user=user)
        response = client.get(self.root_endpoint)
        assert is_success(response.status_code), response.content

    def test_theme_retrieve_allowed(self, make_themes, client):
        u = User.objects.first()
        th_id = ThemesPreferences.objects.filter(user=u)[0].id
        client.force_authenticate(user=u)
        response = client.get(f"{self.root_endpoint}{th_id}/")
        assert is_success(response.status_code), response.content

    def test_theme_retrieve_forbidden(self, make_themes, client):
        u = User.objects.first()
        th_id = ThemesPreferences.objects.all().exclude(user=u)[0].id
        client.force_authenticate(user=u)
        response = client.get(f"{self.root_endpoint}{th_id}/")
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_theme_create(self, make_themes, client):
        user = User.objects.create(username="new")
        client.force_authenticate(user=user)
        response = client.post(
            f"/fr/api/v1/people/themes/", data={"user": user.id, "theme": "azeaze"}
        )
        assert is_success(response.status_code), response.content
