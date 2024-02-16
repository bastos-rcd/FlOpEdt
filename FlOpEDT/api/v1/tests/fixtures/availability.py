import pytest

from api.v1.tests.factories.people import UserFactory
from api.v1.tests.factories.availability import UserAvailabilityFactory

import datetime as dt


@pytest.fixture
def make_default_week_user(db):
    user = UserFactory.create(username="u_def_wk")
    for day in range(1, 8):
        UserAvailabilityFactory.create(
            user=user,
            start_time=dt.datetime(1, 1, day, 0),
            duration=dt.timedelta(hours=24),
            value=8,
        )
