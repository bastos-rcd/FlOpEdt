import pytest


from people.models import Tutor
from base.models import Week
from base.preferences import UserPreference
from base.timing import Day

# from api.v1.tests.base.conftest import tutor_fs_a, tutor_fs_b, week_2024_01


@pytest.fixture(autouse=True)
def availability_a_fs_a_2024_01(db, tutor_fs_a: Tutor, week_2024_01: Week):
    return UserPreference.objects.create(
        user=tutor_fs_a,
        start_time=480,
        duration=60,
        week=week_2024_01,
        day=Day.MONDAY,
        value=8,
    )


@pytest.fixture(scope="module")
def availability_b_fs_a_2024_01(db, tutor_fs_a: Tutor, week_2024_01: Week):
    return UserPreference.objects.create(
        user=tutor_fs_a,
        start_time=540,
        duration=60,
        week=week_2024_01,
        day=Day.MONDAY,
        value=7,
    )


@pytest.fixture(scope="module")
def availability_c_fs_a_2024_01(db, tutor_fs_a: Tutor, week_2024_01: Week):
    return UserPreference.objects.create(
        user=tutor_fs_a,
        start_time=600,
        duration=60,
        week=week_2024_01,
        day=Day.MONDAY,
        value=6,
    )


@pytest.fixture(scope="module")
def availability_d_fs_a_2024_01(db, tutor_fs_a: Tutor, week_2024_01: Week):
    return UserPreference.objects.create(
        user=tutor_fs_a,
        start_time=480,
        duration=60,
        week=week_2024_01,
        day=Day.TUESDAY,
        value=5,
    )


@pytest.fixture(scope="module")
def availability_a_fs_b_2024_01(db, tutor_fs_b: Tutor, week_2024_01: Week):
    return UserPreference.objects.create(
        user=tutor_fs_b,
        start_time=480,
        duration=60,
        week=week_2024_01,
        day=Day.MONDAY,
        value=5,
    )
