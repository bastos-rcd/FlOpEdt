import datetime as dt
import copy

import pytest

from rest_framework.test import APIClient, APITestCase
from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_403_FORBIDDEN,
    is_success,
)
from api.v1.tests.utils import retrieve_elements, add_user_permission

from django.utils.duration import duration_string
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from base.models.rooms import Room
from base.models.groups import Department
from base.models.availability import UserAvailability
from people.models import Tutor, User


from .factories.availability import UserIUTEveningFactory, UserIUTMorningFactory


@pytest.fixture
def client():
    return APIClient()


class TestListUserAvailability:
    endpoint = f"/fr/api/v1/availability/user/"

    def test_user_or_dept_required(self, client: APIClient):
        with pytest.raises(AssertionError) as e_info:
            retrieve_elements(
                client.get(
                    self.endpoint, {"from_date": "2030-01-22", "to_date": "2030-01-24"}
                )
            )

    def test_list_date(self, client: APIClient, make_default_week_user: None):
        user = User.objects.first()
        response = retrieve_elements(
            client.get(
                self.endpoint,
                {
                    "from_date": "0001-01-02",
                    "to_date": "0001-01-04",
                    "user_id": user.id,
                },
            ),
            2,
        )
        response = sorted(response, key=lambda ua: ua["start_time"])
        assert len(response) == 2
        response = [
            {k: v for k, v in r.items() if k in ["start_time", "duration"]}
            for r in response
        ]
        assert response == [
            {
                "start_time": dt.datetime(1, 1, 2, 0).isoformat(),
                "duration": duration_string(dt.timedelta(hours=24)),
            },
            {
                "start_time": dt.datetime(1, 1, 3, 0).isoformat(),
                "duration": duration_string(dt.timedelta(hours=24)),
            },
        ], response.content


class TestUpdateUserAvailability:
    endpoint = f"/fr/api/v1/availability/update_user/"
    from_date = "1871-03-20"
    to_date = "1871-03-20"
    wanted = {
        "from_date": from_date,
        "to_date": to_date,
        "intervals": [
            {
                "start_time": f"{from_date}T00:00:00",
                "duration": "12:00:00",
                "value": 3,
            },
            {
                "start_time": f"{to_date}T12:00:00",
                "duration": "12:00:00",
                "value": 2,
            },
        ],
    }

    def test_update_single_day(self, client, make_user_hourly_commune):
        user = User.objects.first()
        user.is_superuser = True
        user.save()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        response = retrieve_elements(client.post(self.endpoint, push), 4)
        assert response == push

    def test_update_two_days(self, client, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = copy.deepcopy(self.wanted) | {"subject_id": user.id}
        push["to_date"] = "1871-03-21"
        push["intervals"] += [
            {
                "start_time": f"{push['to_date']}T00:00:00",
                "duration": "10:00:00",
                "value": 4,
            },
            {
                "start_time": f"{push['to_date']}T10:00:00",
                "duration": "14:00:00",
                "value": 5,
            },
        ]
        response = retrieve_elements(client.post(self.endpoint, push), 4)
        assert response == push

    def test_update_cut_day_end(self, client: APIClient, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = copy.deepcopy(self.wanted) | {"subject_id": user.id}
        push["to_date"] = "1871-03-21"
        push["intervals"] += [
            {
                "start_time": f"{push['to_date']}T00:00:00",
                "duration": "10:00:00",
                "value": 4,
            },
        ]
        response = client.post(self.endpoint, push)
        assert not is_success(response.status_code), response

    def test_update_cut_day_middle(self, client: APIClient, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = copy.deepcopy(self.wanted) | {"subject_id": user.id}
        push["to_date"] = "1871-03-21"
        push["intervals"] += [
            {
                "start_time": f"{push['to_date']}T00:00:00",
                "duration": "10:00:00",
                "value": 4,
            },
            {
                "start_time": f"{push['to_date']}T12:00:00",
                "duration": "12:00:00",
                "value": 4,
            },
        ]
        response = client.post(self.endpoint, push)
        assert not is_success(response.status_code), response

    def test_perm_push_mine_denied(self, client, make_users):
        user = User.objects.first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        response = client.post(self.endpoint, push)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_mine_allowed(self, client, make_user_perm_push_my_user_av):
        user = make_user_perm_push_my_user_av
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": user.id}
        assert user.id == push["subject_id"]
        response = client.post(self.endpoint, push)
        assert is_success(response.status_code), response.content

    def test_perm_push_other_denied(
        self, client, make_user_perm_push_my_user_av, make_users
    ):
        user = make_user_perm_push_my_user_av
        other = User.objects.all().exclude(id=user.id).first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": other.id}
        response = client.post(self.endpoint, push)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_other_allowed(
        self, client, make_user_perm_push_any_user_av, make_users
    ):
        user = make_user_perm_push_any_user_av
        other = User.objects.all().exclude(id=user.id).first()
        client.force_authenticate(user=user)
        push = self.wanted | {"subject_id": other.id}
        response = client.post(self.endpoint, push)
        assert is_success(response.status_code), response.content


class TestUpdateRoomAvailability:
    endpoint = f"/fr/api/v1/availability/update_room/"
    from_date = "1848-04-27"
    to_date = "1848-04-27"
    wanted = {
        "from_date": from_date,
        "to_date": to_date,
        "intervals": [
            {
                "start_time": f"{from_date}T00:00:00",
                "duration": "12:00:00",
                "value": 3,
            },
            {
                "start_time": f"{to_date}T12:00:00",
                "duration": "12:00:00",
                "value": 2,
            },
        ],
    }

    def test_perm_push_denied(
        self, client: APIClient, db, make_users, make_perm_push_room_av
    ):
        r = Room.objects.create(name="r")
        u = User.objects.first()
        data = self.wanted | {"subject_id": r.id}

        client.force_authenticate(u)
        response = client.post(self.endpoint, data=data)
        assert response.status_code == HTTP_403_FORBIDDEN, response.content

    def test_perm_push_allowed(self, client, make_user_perm_push_room_av):
        r = Room.objects.create(name="r")
        u = make_user_perm_push_room_av
        data = self.wanted | {"subject_id": r.id}

        client.force_authenticate(u)
        response = client.post(self.endpoint, data=data)
        assert is_success(response.status_code), response.content


class TestUserAvailabilityDefault:
    endpoint = f"/fr/api/v1/availability/user-default-week/"

    def test_tutor_creation(self):
        pass

    def test_update(self):
        pass


class TestRoomAvailabilityActual:
    endpoint = f"/fr/api/v1/availability/room/"
