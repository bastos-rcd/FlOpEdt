import pytest
from rest_framework.test import APIClient, APITestCase
from api.v1.tests.utils import retrieve_elements


@pytest.fixture
def client():
    return APIClient()


class TestUserAvailabilityActual:
    endpoint = f"/fr/api/v1/"

    def test_default_week_creation(self, client, make_default_week_user):
        pass
