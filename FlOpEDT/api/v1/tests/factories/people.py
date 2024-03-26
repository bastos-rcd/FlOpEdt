import factory

from .availability import UserDailyAvailabilityFactory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "people.User"

    first_name = factory.Sequence(lambda n: f"Louise{n}")
    last_name = "Doe"
    username = factory.Sequence(lambda n: f"User #{n}")
    is_tutor = False


class UserAndAvFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "people.User"

    username = factory.Sequence(lambda n: f"user_{n}")
    av = factory.RelatedFactoryList(
        UserDailyAvailabilityFactory, factory_related_name="user", size=7
    )


class TutorFactory(UserFactory):
    class Meta:
        model = "people.Tutor"

    is_tutor = True
