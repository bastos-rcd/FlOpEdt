import pytest

from rest_framework.test import APIClient
from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_403_FORBIDDEN,
    is_success,
)

from api.v1.tests.factories.people import UserFactory

from people.models import ThemesPreferences, User

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


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

    def test_theme_retrieve_any_allowed(self, make_themes, client):
        u = User.objects.first()
        print(ContentType.objects.filter(app_label="people"))
        p, _ = Permission.objects.get_or_create(
            name="pouet",
            content_type=ContentType.objects.get(
                app_label="people", model="themespreferences"
            ),
            codename="view_any_themespreferences",
        )
        u.user_permissions.add(p)
        assert (
            "people.view_any_themespreferences" in u.get_all_permissions()
        ), u.user_permissions.all()
        th_id = ThemesPreferences.objects.all().exclude(user=u)[0].id
        client.force_authenticate(user=u)
        response = client.get(f"{self.root_endpoint}{th_id}/")
        assert is_success(response.status_code), response.content

    def test_theme_retrieve_other_forbidden_on_other(self, make_themes, client):
        u = User.objects.first()
        print(ContentType.objects.filter(app_label="people"))
        p, _ = Permission.objects.get_or_create(
            name="pouet",
            content_type=ContentType.objects.get(
                app_label="people", model="themespreferences"
            ),
            codename="view_my_themespreferences",
        )
        u.user_permissions.add(p)
        assert (
            "people.view_my_themespreferences" in u.get_all_permissions()
        ), u.user_permissions.all()
        th_id = ThemesPreferences.objects.all().exclude(user=u)[0].id
        client.force_authenticate(user=u)
        response = client.get(f"{self.root_endpoint}{th_id}/")
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_theme_retrieve_other_forbidden_on_mine(self, make_themes, client):
        u = User.objects.first()
        print(ContentType.objects.filter(app_label="people"))
        p, _ = Permission.objects.get_or_create(
            name="pouet",
            content_type=ContentType.objects.get(
                app_label="people", model="themespreferences"
            ),
            codename="view_my_themespreferences",
        )
        u.user_permissions.add(p)
        assert (
            "people.view_my_themespreferences" in u.get_all_permissions()
        ), u.user_permissions.all()
        th_id = ThemesPreferences.objects.filter(user=u)[0].id
        client.force_authenticate(user=u)
        response = client.get(f"{self.root_endpoint}{th_id}/")
        assert is_success(response.status_code), response.content

    def test_theme_retrieve_all_forbidden_on_mine(self, make_themes, client):
        u = User.objects.first()
        assert (
            "people.view_my_themespreferences" not in u.get_all_permissions()
        ), u.user_permissions.all()
        th_id = ThemesPreferences.objects.filter(user=u)[0].id
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
