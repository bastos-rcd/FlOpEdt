import factory

from datetime import datetime, timedelta


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


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Department"


# Useless, see base/migrations/00074
# class WeekFactory(factory.django.DjangoModelFactory):
#     class Meta:
#         model = "base.Week"
#         exclude = ("current_time",)

#     current_time = factory.Sequence(lambda n: datetime.now() + timedelta(0, 0, 7 * n))
#     nb = factory.LazyAttribute(lambda o: o.current_time.isocalendar().week)
#     year = factory.LazyAttribute(lambda o: o.current_time.isocalendar().year)
