import factory

from .availability import RoomDailyAvailabilityFactory


class RoomTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.RoomType"
    name = factory.Sequence(lambda n: f"room_type{n}")


class RoomAndAvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Room"

    name = factory.Sequence(lambda n: f"room{n}")
    av = factory.RelatedFactoryList(
        RoomDailyAvailabilityFactory, factory_related_name="room", size=7
    )
