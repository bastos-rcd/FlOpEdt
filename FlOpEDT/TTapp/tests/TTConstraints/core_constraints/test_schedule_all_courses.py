import datetime as dt

import factory
import pytest

from base.models import Course, ScheduledCourse
from TTapp.models import ScheduleAllCourses


def test_test(create_typical_situation):
    courses = Course.objects.all()
    period = courses[0].period
    time1 = dt.datetime(2024,1,1, 8, 0, 0)
    time2 = dt.datetime(2024,1,1, 10, 0, 0)
    ScheduledCourse.objects.create(course=courses[0], start_time=time1, version__major=0)
    ScheduledCourse.objects.create(course=courses[1], start_time=time2,  version__major=0)
    with pytest.raises(AssertionError):
        ScheduleAllCourses().is_satisfied_for(period, 0)
