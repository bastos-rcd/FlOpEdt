import factory



class CourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Course"
    
    module = factory.SubFactory("api.v1.tests.factories.course.ModuleFactory")


class CourseTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.CourseType"


class ModuleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.Module"
    abbrev = factory.Sequence(lambda n: f"Mod_{n}")
    name = factory.Sequence(lambda n: f"Module {n}")
    # TODO : Add mandatory fields using sequences


class ModuleAndCoursesFactory(ModuleFactory):
    class Meta:
        model = "base.Module"

    courses = factory.RelatedFactoryList(CourseFactory, factory_related_name="module", size=10)



class ScheduledCourseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.ScheduledCourse"
