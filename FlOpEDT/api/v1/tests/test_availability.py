import pytest
from rest_framework.test import APIClient
from urllib.parse import urlencode


@pytest.fixture
def client():
    return APIClient()


def test_bknews(client, availability_a_fs_a_2024_01, tutor_fs_a):
    endpoint = f"/fr/api/v1/availability/user-actual"

    user_id = tutor_fs_a.id

    params = urlencode(
        {"from_date": "2024-01-01", "to_date": "2024-01-07", "user_id": user_id}
    )

    response = client.get(f"{endpoint}/?{params}")
    print(response.data)
    assert False
    # assert response.status_code == 200
    # print(response.data)
    # assert len(response.data) == 1
    # result = dict(response.data[0])
    # print(result)
    # assert result["week"] == 11
