import factory

from datetime import datetime, timedelta


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
