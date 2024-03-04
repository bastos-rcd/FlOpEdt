import factory

class TrainingPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.TrainingPeriod"


class SchedulingPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.SchedulingPeriod"
