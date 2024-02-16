import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "people.User"

    first_name = factory.Sequence(lambda n: f"Aline{n}")
    last_name = "Doe"
    username = factory.Sequence(lambda n: f"User #{n}")
    is_tutor = False


class TutorFactory(UserFactory):
    class Meta:
        model = "people.Tutor"

    is_tutor = True
