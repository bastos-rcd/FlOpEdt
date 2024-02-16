import pytest

from api.v1.tests.factories.people import UserFactory


@pytest.fixture
def make_users(db):
    UserFactory.create_batch(size=10)
