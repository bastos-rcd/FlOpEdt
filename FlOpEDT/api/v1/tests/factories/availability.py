import datetime as dt

import factory
from base.timing import Day


class UserAvailabilityIUT(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.UserAvailability"
        exclude = ("cycle",)

    cycle = 30
    duration = 90
    day = factory.Sequence(
        lambda n: Day.CHOICES[min((n % 30) // 6, len(Day.CHOICES))][0]
    )
    start_time = factory.Iterator([480, 570, 665, 855, 945, 1035] * 5)


class UserIUTEveningFactory(UserAvailabilityIUT):
    value = factory.Iterator([3, 2, 1, 0, 0, 0] * 5)


class UserIUTMorningFactory(UserAvailabilityIUT):
    value = factory.Iterator([0, 0, 0, 1, 2, 3] * 5)


class UserAvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.UserAvailability"


class UserHourlyAvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.UserAvailability"
        exclude = ("cycle",)

    cycle = 24 * 7
    start_time = factory.Sequence(
        lambda n: dt.datetime(1871, 3, 18) + dt.timedelta(hours=n)
    )
    duration = dt.timedelta(hours=1)
    value = factory.Iterator(list(range(8)) * 3 * 7)


class UserDailyAvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.UserAvailability"

    start_time = factory.Sequence(lambda n: dt.datetime(1871, 3, 18 + (n % 7)))
    duration = dt.timedelta(days=1)
    value = factory.Iterator(range(9))


class RoomDailyAvailabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.RoomAvailability"

    start_time = factory.Sequence(lambda n: dt.datetime(1871, 3, 18 + (n % 7)))
    duration = dt.timedelta(days=1)
    value = factory.Iterator(range(9))
