import pytest

from ..factories.group import DepartmentFactory, TrainingProgrammeFactory
from ..factories.course import (
    ModuleFactory,
    CourseTypeFactory,
    CourseRRGroup,
    TrainingPeriodDummyFactory,
)


@pytest.fixture
def make_courses(db, make_classical_structural_groups):
    TrainingPeriodDummyFactory.create()
    d = DepartmentFactory.create()
    tp = TrainingProgrammeFactory.create()
    groups = make_classical_structural_groups(tp)
    mod = ModuleFactory.create(train_prog=tp)
    course_type = CourseTypeFactory.create()
    courses = CourseRRGroup.create_batch((2**3 - 1) * 2)
