import factory

from .availability import RoomDailyAvailabilityFactory


class RoomAndAvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Room"

    name = factory.Sequence(lambda n: f"room{n}")
    av = factory.RelatedFactoryList(
        RoomDailyAvailabilityFactory, factory_related_name="room", size=7
    )
