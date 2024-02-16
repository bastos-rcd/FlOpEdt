import datetime as dt

import pytest

from rest_framework.test import APIClient, APITestCase
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE
from api.v1.tests.utils import retrieve_elements

from django.utils.duration import duration_string

from base.models.groups import Department
from base.models.availability import UserAvailability
from base.models.timing import Week
from people.models import Tutor, User


from .factories.base import TutorFactory
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
    endpoint = f"/fr/api/v1/availability/user-actual/"

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
