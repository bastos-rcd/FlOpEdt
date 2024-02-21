import datetime as dt

import pytest

from rest_framework.test import APIClient, APITestCase
from rest_framework.status import (
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_403_FORBIDDEN,
    is_success,
)
from api.v1.tests.utils import retrieve_elements

from django.utils.duration import duration_string

from base.models.groups import Department
from base.models.availability import UserAvailability
from base.models.timing import Week
from people.models import Tutor, User


from .factories.availability import UserIUTEveningFactory, UserIUTMorningFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def make_availabilities_IUT(db: None):
    TutorFactory.create_batch(size=2)
    tutor = Tutor.objects.first()
    week = Week.objects.get(nb=4, year=2030)
    UserIUTEveningFactory.create_batch(
        size=UserIUTEveningFactory.cycle, user=tutor, week=week
    )
    week = Week.objects.get(nb=5, year=2030)
    UserIUTMorningFactory.create_batch(
        size=UserIUTMorningFactory.cycle, user=tutor, week=week
    )
    tutor = Tutor.objects.all()[1]
    UserIUTEveningFactory.create_batch(
        size=UserIUTEveningFactory.cycle, user=tutor, week=week
    )


class TestUserAvailabilityActual:
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
        ]


class TestUserAvailabilityActual:
    endpoint = f"/fr/api/v1/availability/update_user/"

    def test_update(self, client, make_user_hourly_commune):
        user = User.objects.first()
        client.force_authenticate(user=user)
        date = "1871-03-20"
        wanted = {
            "date": date,
            "subject_id": user.id,
            "intervals": [
                {
                    "start_time": f"{date}T00:00:00",
                    "duration": "12:00:00",
                    "value": 3,
                },
                {
                    "start_time": f"{date}T12:00:00",
                    "duration": "12:00:00",
                    "value": 2,
                },
            ],
        }
        response = retrieve_elements(client.post(self.endpoint, wanted), 3)
        assert response == wanted

    @pytest.mark.skip(reason="rights have to be implemented")
    def test_update_rights(self, client, make_users, make_default_week_user):
        user = User.objects.first()
        client.force_authenticate(user=user)
        date = "1871-03-20"
        wanted = {
            "date": date,
            "subject_id": user.id,
            "intervals": [
                {
                    "start_time": f"{date}T00:00:00",
                    "duration": "12:00:00",
                    "value": 3,
                },
                {
                    "start_time": f"{date}T12:00:00",
                    "duration": "12:00:00",
                    "value": 2,
                },
            ],
        }
        response = client.post(self.endpoint, wanted)
        assert is_success(response.status_code), response.content
        wanted["subject_id"] = User.objects.all()[1].id
        assert user.id != wanted["subject_id"]
        response = client.post(self.endpoint, wanted)
        print(dir(response))
        print(response.content)
        print(response.data)
        assert response.status_code == HTTP_403_FORBIDDEN, (response.content, user.id)

    def test_rights(self):
        pass


class TestUserAvailabilityDefault:
    endpoint = f"/fr/api/v1/availability/user-default-week/"

    def test_tutor_creation(self):
        pass

    def test_update(self):
        pass


class TestRoomAvailabilityActual:
    endpoint = f"/fr/api/v1/availability/room/"
