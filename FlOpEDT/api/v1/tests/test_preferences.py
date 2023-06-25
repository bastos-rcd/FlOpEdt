import pytest
from base.models.groups import Department
from base.models.preferences import UserPreference
from people.models import Tutor
from rest_framework.test import APIClient
from api.v1.tests.fixtures import department_a, tutor_fs_a
from base.timing import datetime_to_floptime, date_to_flopday, time_to_floptime
import datetime

first_may_2023_8AM = datetime.datetime(year=2023, month=5, day=1, hour=8)
first_may_2023_9AM = datetime.datetime(year=2023, month=5, day=1, hour=9)
first_may_2023_10AM = datetime.datetime(year=2023, month=5, day=1, hour=10)
first_may_2023_11AM = datetime.datetime(year=2023, month=5, day=1, hour=11)

# To be removed when floptime is abandonned
flop_first_may_2023 = datetime_to_floptime(first_may_2023_8AM)[0]

time_8AM = datetime.time(hour=8)
time_9AM = datetime.time(hour=9)
time_10AM = datetime.time(hour=10)
time_11AM = datetime.time(hour=11)
time_1PM = datetime.time(hour=13)

# To be removed when floptime is abandonned
flop_time_8AM = time_to_floptime(time_8AM)
flop_time_9AM = time_to_floptime(time_9AM)
flop_time_10AM = time_to_floptime(time_10AM)
flop_time_11AM = time_to_floptime(time_11AM)
flop_time_1PM = time_to_floptime(time_1PM)


@pytest.fixture
def user_preference1(db, tutor_fs_a: Tutor) -> UserPreference:
    return UserPreference.objects.create(user=tutor_fs_a,
                                         value=4,
                                         start_time=flop_time_8AM,
                                         duration=60,
                                         week=flop_first_may_2023.week,
                                         day=flop_first_may_2023.day,
                                         # To be changed when floptime is abandonned
                                         # start_time=first_may_2023_8AM,
                                         # end_time=first_may_2023_9AM
                                         )


@pytest.fixture
def user_preference2(db, tutor_fs_a: Tutor) -> UserPreference:
    return UserPreference.objects.create(user=tutor_fs_a,
                                         value=0,
                                         start_time=flop_time_9AM,
                                         duration=60,
                                         week=flop_first_may_2023.week,
                                         day=flop_first_may_2023.day,
                                        #  start_time=first_may_2023_9AM,
                                        #  end_time=first_may_2023_10AM
                                        )


@pytest.fixture
def user_preference3(db, tutor_fs_a: Tutor) -> UserPreference:
    return UserPreference.objects.create(user=tutor_fs_a,
                                         value=8,
                                         start_time=flop_time_10AM,
                                         duration=60,
                                         week=flop_first_may_2023.week,
                                         day=flop_first_may_2023.day,
                                        #  start_time=first_may_2023_10AM,
                                        #  end_time=first_may_2023_11AM
                                        )


@pytest.fixture
def default_user_preference1(db, tutor_fs_a: Tutor) -> UserPreference:
    return UserPreference.objects.create(user=tutor_fs_a,
                                         value=8,
                                         week=None,
                                         week_day='m',
                                         start_time=flop_time_8AM,
                                         end_time=flop_time_10AM)


@pytest.fixture
def default_user_preference2(db, tutor_fs_a: Tutor) -> UserPreference:
    return UserPreference.objects.create(user=tutor_fs_a,
                                         value=8,
                                         week=None,
                                         week_day='m',
                                         start_time=flop_time_10AM,
                                         end_time=flop_time_1PM)


@pytest.fixture
def default_user_preference3(db, tutor_fs_a: Tutor) -> UserPreference:
    return DefaultWeekUserPreference.objects.create(user=tutor_fs_a,
                                                    value=8,
                                                    week=None,
                                                    week_day='m',
                                                    start_time=flop_time_10AM,
                                                    end_time=flop_time_11AM)


@pytest.fixture
def client():
    return APIClient()


# Query
def test_preferences(client,
                     user_preference1: UserPreference,
                     default_user_preference2,
                     default_user_preference3):
    endpoint_default = "/fr/api/preferences/user-default"
    endpoint_actual = "fr/api/preferences/user-actual/?week=18&year=2023"

    response_default = client.get(endpoint_default)
    assert response_default.status_code == 200
    assert len(response_default.data) == 2
    result = dict(response_default.data[0])
    assert result["value"] == 8

    response_actual = client.get(endpoint_actual)
    assert response_actual.status_code == 200
    assert len(response_actual.data) == 1
    result = dict(response_actual.data[0])
    assert result["value"] == 4
