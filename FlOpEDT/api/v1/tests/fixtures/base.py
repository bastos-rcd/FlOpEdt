# Fixtures use to unuse and redefine arguments...
# pylint: disable=unused-argument,redefined-outer-name

import pytest

from base.models import (
    CourseType,
    Department,
    Module,
    StructuralGroup,
    TrainingPeriod,
    TrainingProgramme,
)
from people.models import SupplyStaff, Tutor, UserDepartmentSettings

from ..factories.group import DepartmentFactory


@pytest.fixture
def make_department(db):
    DepartmentFactory.create(name="dept info", abbrev="INF")


@pytest.fixture
def department_a(db) -> Department:
    return Department.objects.create(abbrev="test", name="Department test")


@pytest.fixture
def period_a(db, department_a: Department) -> TrainingPeriod:
    return TrainingPeriod.objects.create(
        name="Period test", starting_week=1, ending_week=20, department=department_a
    )


@pytest.fixture
def train_prog_a(db, department_a: Department) -> TrainingProgramme:
    return TrainingProgramme.objects.create(
        name="TP test", abbrev="TP test", department=department_a
    )


@pytest.fixture
def module_a(db, train_prog_a: TrainingProgramme, period_a: TrainingPeriod) -> Module:
    return Module.objects.create(
        abbrev="Module test",
        name="Module test",
        train_prog=train_prog_a,
        period=period_a,
    )


@pytest.fixture
def parent_group_a(db, train_prog_a: TrainingProgramme) -> StructuralGroup:
    return StructuralGroup.objects.create(
        name="Parent group test", train_prog=train_prog_a, size=0, basic=False
    )


@pytest.fixture
def basic_group_a(
    db, train_prog_a: TrainingProgramme, parent_group_a: StructuralGroup
) -> StructuralGroup:
    basic_group = StructuralGroup.objects.create(
        name="Group test", train_prog=train_prog_a, size=0, basic=True
    )
    basic_group.parent_groups.add(parent_group_a)
    return basic_group


@pytest.fixture
def tutor_fs_a(db, department_a: Department) -> SupplyStaff:
    t = Tutor.objects.create(
        username="fs_a_tut",
        first_name="fs_a",
        last_name="fs_a",
        is_tutor=True,
        email="fs_a@flop.org",
        is_staff=True,
    )
    UserDepartmentSettings.objects.create(user=t, department=department_a, is_main=True)
    return t


@pytest.fixture
def tutor_fs_b(db, department_a: Department) -> SupplyStaff:
    t = Tutor.objects.create(
        username="fs_b",
        first_name="fs_b",
        last_name="fs_b",
        is_tutor=True,
        email="fs_b@flop.org",
        is_staff=True,
    )
    UserDepartmentSettings.objects.create(user=t, department=department_a, is_main=True)
    return t


@pytest.fixture
def tutor_admin_a(db, department_a: Department) -> SupplyStaff:
    t = Tutor.objects.create(
        username="fs_a_tutadmin",
        first_name="fs_a",
        last_name="fs_a",
        is_tutor=True,
        email="fs_a@flop.org",
        is_staff=True,
        is_superuser=True,
    )
    UserDepartmentSettings.objects.create(
        user=t, department=department_a, is_main=True, is_admin=True
    )
    return t


@pytest.fixture
def course_type_a(db, department_a: Department) -> CourseType:
    return CourseType.objects.create(department=department_a, name="Course Type test")