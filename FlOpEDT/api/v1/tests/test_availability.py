import pytest
from rest_framework.test import APIClient, APITestCase
from api.v1.tests.utils import retrieve_elements

from base.models.groups import Department
from base.models.availability import UserAvailability
from base.models.timing import Week
from people.models import Tutor

from .factories.base import TutorFactory
from .factories.availability import UserIUTEveningFactory, UserIUTMorningFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def make_availabilities_IUT(db):
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

    def test_user(self, client):
        with pytest.raises(Exception) as e_info:
            client.get(
                self.endpoint, {"from_date": "2030-01-22", "to_date": "2030-01-24"}
            )

    def test_date(self, client, make_availabilities_IUT):
        tutor = Tutor.objects.first()
        response = retrieve_elements(
            client.get(
                self.endpoint,
                {
                    "from_date": "2030-01-22",
                    "to_date": "2030-01-24",
                    "user_id": tutor.id,
                },
            ),
            6 * 3,
        )
        response = retrieve_elements(
            client.get(
                self.endpoint,
                {
                    "from_date": "2030-01-29",
                    "to_date": "2030-01-30",
                    "user_id": tutor.id,
                },
            ),
            6 * 2,
        )
