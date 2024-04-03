import factory

from base.models import Department


class DepartmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Department"

    abbrev = factory.Sequence(lambda n: f"dept{n:02d}")
    name = factory.Sequence(lambda n: f"Department #{n:02d}")


class TrainingProgrammeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.TrainingProgramme"

    abbrev = factory.Sequence(lambda n: f"tp {n:02d}")
    name = factory.Sequence(lambda n: f"Training Programme #{n:02d}")
    department = factory.LazyFunction(Department.objects.first)


class StructuralGroupDummyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.StructuralGroup"

    # missing: train_prog, name
    size = 314
