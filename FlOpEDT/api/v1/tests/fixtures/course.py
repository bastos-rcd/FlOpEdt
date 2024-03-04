import factory
import pytest

from api.v1.tests.factories.course import *
from api.v1.tests.factories.people import *
from base.models import Course

@pytest.fixture
def create_courses(db):
    return lambda n: CourseFactory.create_batch(n)

@pytest.fixture
def create_typical_situation(db):
    train_prog = TrainingProgramFactory.create()
    modules = ModuleFactory.create_batch(5, train_prog=train_prog)
    course_types = CourseTypeFactory.create_batch(2)
    tutors = TutorFactory.create_batch(3)
    groups = GroupFactory.create_batch(3, train_prog=train_prog)
    courses = [Course.objects.create(module=module, course_type=course_type, tutor=tutor) 
               for module in modules 
               for course_type in course_types
               for tutor in tutors]
