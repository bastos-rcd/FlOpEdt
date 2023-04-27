import pytest
from base.models import Department
from displayweb.models import BreakingNews
from rest_framework.test import APIClient

@pytest.fixture
def department_cs(db) -> Department:
    return Department.objects.create(abbrev="CS", name="Computer Science")

@pytest.fixture
def department_networks(db) -> Department:
    return Department.objects.create(abbrev="NT",
                                     name="Networks & Telecommunication")

@pytest.fixture
def y1(db, department_cs:Department) -> BreakingNews:
    return BreakingNews.objects.create(department= department_cs,
                                       week = 11, year = 2021,
                                       y=5, txt = "Lorem ipsum dolor sit amet.")


@pytest.fixture
def client():
    return APIClient()

# Query
def test_bknews(client,
                y1 : BreakingNews):
    endpoint = "/fr/api/display/breakingnews/"
    response = client.get(endpoint, format="json")
    print(response)
    print(response.data)
    assert len(response.data) == 1
    result = dict(response.data[0])
    print(result)
    assert result["week"] == 11
