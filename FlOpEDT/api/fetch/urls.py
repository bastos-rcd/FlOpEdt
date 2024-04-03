# This file is part of the FlOpEDT/FlOpScheduler project.
# Copyright (c) 2017
# Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with this program. If not, see
# <http://www.gnu.org/licenses/>.
#
# You can be released from the requirements of the license by purchasing
# a commercial license. Buying such a license is mandatory as soon as
# you develop activities involving the FlOpEDT/FlOpScheduler software
# without disclosing the source code of your own applications.

from rest_framework import routers

from api.fetch import views

routerFetch = routers.SimpleRouter()

routerFetch.register(
    r"scheduledcourses", views.ScheduledCoursesViewSet, basename="scheduledcourses"
)
routerFetch.register(
    r"new_api_scheduledcourses",  # entry of ScheduledCourses for new api with standard dates
    views.NewApiScheduledCoursesViewSet,
    basename="new_api_scheduledcourses",
)
routerFetch.register(
    r"unscheduledcourses",
    views.UnscheduledCoursesViewSet,
    basename="unscheduledcourses",
)
# routerFetch.register(
#     r"coursedefweek", views.CourseTypeDefaultWeekViewSet, basename="coursedefweek"
# )
# routerFetch.register(r'allversions', views.AllVersionsViewSet)
routerFetch.register(r"alldepts", views.DepartmentsViewSet, basename="dept")
# routerFetch.register(r'tutorcourses', views.TutorCoursesViewSet, basename='tutorcourses')
routerFetch.register(
    r"extrasched", views.ExtraSchedCoursesViewSet, basename="extrasched"
)
routerFetch.register(r"bknews", views.BKNewsViewSet, basename="BKNews")
routerFetch.register(
    r"constraints", views.ConstraintsQueriesViewSet, basename="constraints"
)
routerFetch.register(r"weekdays", views.WeekDaysViewSet, basename="weekdays")
routerFetch.register(r"idtutor", views.IDTutorViewSet, basename="idtutor")
routerFetch.register(r"idtrainprog", views.IDTrainProgViewSet, basename="idtrainprog")
routerFetch.register(r"idmodule", views.IDModuleViewSet, basename="idmodule")
routerFetch.register(
    r"idcoursetype", views.IDCourseTypeViewSet, basename="idcoursetype"
)
routerFetch.register(r"idgroup", views.IDGroupViewSet, basename="idgroup")
routerFetch.register(r"idgrouptype", views.IDGroupTypeViewSet, basename="idgrouptype")
routerFetch.register(r"idroom", views.IDRoomViewSet, basename="idroom")
routerFetch.register(r"idroomtype", views.IDRoomTypeViewSet, basename="idroomtype")
routerFetch.register(r"parameter", views.ParameterViewSet, basename="parameter")
