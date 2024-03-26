from django.urls import include, path
from rest_framework import routers

from . import views

routerConstraintBase = routers.SimpleRouter()

routerConstraintBase.register(
    "course_start_time",
    views.CourseStartTimeConstraintsViewSet,
    basename="course-start-time",
)
