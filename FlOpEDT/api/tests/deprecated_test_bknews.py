import pytest
from rest_framework.test import APIClient

from api.tests.fixtures import department_a
from base.models import Department
from displayweb.models import BreakingNews


@pytest.fixture
def bknews(db, department_a: Department) -> BreakingNews:
    return BreakingNews.objects.create(
        department=department_a,
        week=11,
        year=2021,
        y=5,
        txt="Lorem ipsum dolor sit amet.",
    )


@pytest.fixture
def client():
    return APIClient()


# Query
def test_bknews(client, bknews: BreakingNews):
    endpoint = "/fr/api/display/breakingnews/"
    response = client.get(endpoint)
    print(response)
    assert response.status_code == 200
    print(response.data)
    assert len(response.data) == 1
    result = dict(response.data[0])
    print(result)
    assert result["week"] == 11
