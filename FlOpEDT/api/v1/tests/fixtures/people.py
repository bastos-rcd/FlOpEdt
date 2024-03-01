import pytest

from api.v1.tests.factories.people import UserFactory, UserAndAvFactory


@pytest.fixture
def make_users(db):
    return lambda n: UserFactory.create_batch(size=n)


@pytest.fixture
def make_users_and_av(db):
    return lambda n: UserAndAvFactory.create_batch(size=n)
