import datetime as dt

import factory

from base.models import CourseType, GenericGroup, Module, TrainingPeriod

from .shared import PostGenerationWithCounter


class TrainingPeriodDummyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.TrainingPeriod"

    # not associated with any SchedulingPeriod
    name = factory.Sequence(lambda n: f"(Training)Period #{n}")


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Module"

    # missing train_prog
    abbrev = factory.Sequence(lambda n: f"mod{n:02d}")
    name = factory.Sequence(lambda n: f"Module #{n:02d}")
    training_period = factory.LazyFunction(TrainingPeriod.objects.first)


class CourseTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.CourseType"

    name = "Lab"


def go_groups(self, step, create, extracted, **kwargs):
    if not create:
        return
    self.groups.add(step.attributes.get("group_helper"))


class CourseRRGroup(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Course"
        exclude = ("group_helper",)

    duration = dt.timedelta(minutes=90)
    group_helper = factory.Iterator(GenericGroup.objects.all())
    module = factory.LazyFunction(Module.objects.first)
    type = factory.LazyFunction(CourseType.objects.first)
    groups = PostGenerationWithCounter(go_groups)
