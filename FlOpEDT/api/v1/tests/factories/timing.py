import factory


class SchedulingPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.SchedulingPeriod"

    name = factory.Sequence(lambda n: f"SchedulingPeriod_{n}")
    start_date = factory.Faker("date_this_year")
    end_date = factory.Faker("date_this_year")
    mode = factory.Faker("random_element", elements=["d", "w", "m", "y", "c"])


class TrainingPeriodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.TrainingPeriod"

    name = factory.Sequence(lambda n: f"TrainingPeriod_{n}")
    periods = factory.RelatedFactoryList(
        SchedulingPeriodFactory, factory_related_name="training_periods", size=10
    )
