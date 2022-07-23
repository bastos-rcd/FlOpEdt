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

from api.base import views

routerBase = routers.SimpleRouter()

# routerBase.register(r'studentspreferences', views.StudentPreferencesViewSet, basename="students")
# routerBase.register(r'groupspreferences', views.GroupPreferencesViewSet)

# routerBase.register(r'departments', views.DepartmentViewSet)
routerBase.register(r'trainingprogram/name', views.TrainingProgrammeNameViewSet, basename='trainingprogramme-name')
# routerBase.register(r'trainingprogram', views.TrainingProgrammeViewSet)
# routerBase.register(r'holidays', views.HolidaysViewSet)
# routerBase.register(r'traininghalfdays', views.TrainingHalfDaysViewSet)
# routerBase.register(r'periods', views.PeriodsViewSet)
# routerBase.register(r'timesettings', views.TimeGeneralSettingsViewSet)
routerBase.register(r'weeks', views.WeeksViewSet, basename='weeks')

# routerBase.register(r'edtversions', views.EdtVersionsViewSet)
# routerBase.register(r'coursemodifications', views.CourseModificationsViewSet)
# routerBase.register(r'tutorcosts', views.TutorCostsViewSet)
# routerBase.register(r'groupcosts', views.GroupCostsViewSet)
# routerBase.register(r'CourseStartTimeFilter', views.GroupFreeHalfDaysViewSet)
# routerBase.register(r'dependencies', views.DependenciesViewSet)
# routerBase.register(r'coursesstarttimeconstraints', views.CourseStartTimeConstraintsViewSet)
# routerBase.register(r'regens', views.RegensViewSet)
# routerBase.register(r'login', views.LoginView, basename="login")
# routerBase.register(r'logout', views.LogoutView, basename="logout")
