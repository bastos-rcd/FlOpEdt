import factory


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Module"
    abbrev = factory.Sequence(lambda n: f"Mod_{n}")
    train_prog = factory.SubFactory("api.v1.tests.factories.group.TrainingProgrammeFactory")
    training_period = factory.SubFactory("api.v1.tests.factories.timing.TrainingPeriodFactory")


class CourseTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.CourseType"
    name = factory.Sequence(lambda n: f"CourseType_{n}")
    

class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Course"
    type = factory.SubFactory(CourseTypeFactory)
    duration = factory.Faker("time_delta")
    module = factory.SubFactory(ModuleFactory)
    room_type = factory.SubFactory("api.v1.tests.factories.room.RoomTypeFactory")
    tutor = factory.SubFactory("api.v1.tests.factories.people.TutorFactory")
    groups = factory.SubFactory("api.v1.tests.factories.group.StructuralGroupFactory")
    period = factory.SubFactory("api.v1.tests.factories.timing.SchedulingPeriodFactory")



class ModuleAndCoursesFactory(ModuleFactory):
    class Meta:
        model = "base.Module"
    courses = factory.RelatedFactoryList(CourseFactory, factory_related_name="module", size=10)



class ScheduledCourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.ScheduledCourse"
    course = factory.SubFactory(CourseFactory)
    start_time = factory.Faker("time_object")
    room = factory.SubFactory("api.v1.tests.factories.room.RoomAndAvFactory")
    work_copy = factory.Faker("random_int", min=0, max=10)
    tutor = factory.SubFactory("api.v1.tests.factories.people.TutorFactory")
