from rest_framework import routers

from django.urls import path, include

from . import views

routerConstraintBase = routers.SimpleRouter()

routerConstraintBase.register(
    "course_start_time",
    views.CourseStartTimeConstraintsViewSet,
    basename="course-start-time",
)
