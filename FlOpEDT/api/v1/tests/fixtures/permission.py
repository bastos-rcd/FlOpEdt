# Fixtures use to unuse and redefine arguments...
# pylint: disable=unused-argument,redefined-outer-name

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from api.v1.tests.utils import add_user_permission
from people.models import User


@pytest.fixture
def make_perm_push_room_av(db):
    p, _ = Permission.objects.get_or_create(
        name="push roomavailability",
        content_type=ContentType.objects.get(
            app_label="base", model="roomavailability"
        ),
        codename="push_roomavailability",
    )
    return p


@pytest.fixture
def make_user_perm_push_room_av(make_perm_push_room_av):
    p = make_perm_push_room_av
    user = User.objects.create(username="withperm")
    add_user_permission(user, p)
    return user


@pytest.fixture
def make_perm_push_any_user_av(db):
    p, _ = Permission.objects.get_or_create(
        name="push any useravailability",
        content_type=ContentType.objects.get(
            app_label="base", model="useravailability"
        ),
        codename="push_any_useravailability",
    )
    return p


@pytest.fixture
def make_user_perm_push_any_user_av(make_perm_push_any_user_av):
    p = make_perm_push_any_user_av
    user = User.objects.create(username="withperm")
    add_user_permission(user, p)
    return user


@pytest.fixture
def make_perm_push_my_user_av(db) -> Permission:
    p, _ = Permission.objects.get_or_create(
        name="push my useravailability",
        content_type=ContentType.objects.get(
            app_label="base", model="useravailability"
        ),
        codename="push_my_useravailability",
    )
    return p


@pytest.fixture
def make_user_perm_push_my_user_av(make_perm_push_my_user_av) -> User:
    p = make_perm_push_my_user_av
    user = User.objects.create(username="withperm")
    add_user_permission(user, p)
    return user


@pytest.fixture
def make_perm_view_my_user_av(db) -> Permission:
    p, _ = Permission.objects.get_or_create(
        name="view my useravailability",
        content_type=ContentType.objects.get(
            app_label="base", model="useravailability"
        ),
        codename="view_my_useravailability",
    )
    return p


@pytest.fixture
def make_perm_view_any_user_av(db) -> Permission:
    p, _ = Permission.objects.get_or_create(
        name="view any useravailability",
        content_type=ContentType.objects.get(
            app_label="base", model="useravailability"
        ),
        codename="view_any_useravailability",
    )
    return p


@pytest.fixture
def make_perm_add_department(db) -> Permission:
    p, _ = Permission.objects.get_or_create(
        content_type=ContentType.objects.get(app_label="base", model="department"),
        codename="add_department",
    )
    return p


@pytest.fixture
def make_perm_delete_department(db) -> Permission:
    p, _ = Permission.objects.get_or_create(
        content_type=ContentType.objects.get(app_label="base", model="department"),
        codename="delete_department",
    )
    return p


@pytest.fixture
def make_perm_change_department(db) -> Permission:
    p, _ = Permission.objects.get_or_create(
        content_type=ContentType.objects.get(app_label="base", model="department"),
        codename="change_department",
    )
    return p
