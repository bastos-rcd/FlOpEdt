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
from django.urls import path
from .base.courses import views as courses_views
from .people import views as people_views
from .base.groups import views as groups_views

routerV1 = routers.SimpleRouter()

routerV1.register(r'scheduled_courses', courses_views.ScheduledCoursesViewSet, basename="scheduled_courses")
routerV1.register(r'users', people_views.UsersViewSet, basename="users")
routerV1.register(r'getcurrentuser', people_views.getCurrentUserView.as_view(), basename='getcurrentuser'),
routerV1.register(r'structural_groups', groups_views.StructuralGroupViewSet, basename="structura_groups")
routerV1.register(r'transversal_groups', groups_views.TransversalGroupViewSet, basename="transversal_groups")
routerV1.register(r'training_programmes', groups_views.TrainingProgrammeViewset, basename="training_programmes")
