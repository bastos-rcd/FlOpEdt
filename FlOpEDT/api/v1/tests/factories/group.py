import factory

class TrainingProgrammeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.TrainingProgramme"
    name = factory.Sequence(lambda n: f"TrainingProgramme_{n}")
    abbrev = factory.Sequence(lambda n: f"Train_prog_{n}")


class StructuralGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.StructuralGroup"
    name = factory.Sequence(lambda n: f"StructuralGroup_{n}")
    train_prog = factory.SubFactory(TrainingProgrammeFactory)
    size = 10

