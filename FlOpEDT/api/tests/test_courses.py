import pytest
from base.models import Department, Course, ScheduledCourse, Week, Module, \
    StructuralGroup, TrainingProgramme, Period, CourseType
from rest_framework.test import APIClient
from api.tests.fixtures import department_a, week_2021_11, period_a, module_a, train_prog_a, basic_group_a, parent_group_a, course_type_a


@pytest.fixture
def Course1(db, week_2021_11: Week,
            module_a: Module, basic_group_a: StructuralGroup,
            course_type_a: CourseType
            ) -> Course:
    return Course.objects.create(type=course_type_a,
                                 week=week_2021_11,
                                 module=module_a)


@pytest.fixture
def client():
    return APIClient()

# Query
def test_courses(client,
                 Course1: Course):
    endpoint = "/fr/api/courses/courses/"

    response= client.get(endpoint)
    assert response.status_code == 200
    assert len(response.data) == 1
    result = dict(response.data[0])
    assert result["week"] == 11
    assert result["year"] == 2021
    