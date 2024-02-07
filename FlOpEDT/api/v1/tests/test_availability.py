import pytest
from rest_framework.test import APIClient, APITestCase
import json


@pytest.fixture
def client():
    return APIClient()


class TestAvailability:
    endpoint = f"/fr/api/v1/availability/user-actual/"

    def test_test(self, client, availability_a_fs_a_2024_01, tutor_fs_a):

        user_id = tutor_fs_a.id

        param_dict = {
            "from_date": "2024-01-01",
            "to_date": "2024-01-07",
            "user_id": user_id,
        }

        response = client.get(self.endpoint, param_dict)

        assert response.status_code == 200
        print(response)
        print(response.content)
        print(json.loads(response.content))
        assert False
