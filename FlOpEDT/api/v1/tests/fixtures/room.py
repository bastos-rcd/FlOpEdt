import pytest
from ..factories.room import RoomAndAvFactory


@pytest.fixture
def make_rooms_and_av(db):
    return lambda n: RoomAndAvFactory.create_batch(size=n)
