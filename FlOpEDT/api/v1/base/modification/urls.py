from rest_framework import routers

from api.v1.base.modification import views

routerModification = routers.SimpleRouter()

routerModification.register(
    "version", views.TimetableVersionViewSet, basename="timetable-version"
)
