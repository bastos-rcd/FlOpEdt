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
from api.TTapp import views
# from api.TTapp import views

routerTTapp = routers.SimpleRouter()

# routerTTapp.register(r'customconstrains', views.TTCustomConstraintsViewSet)
# routerTTapp.register(r'limitcoursetypetimeperperiods', views.TTLimitCourseTypeTimePerPeriodsViewSet)
# routerTTapp.register(r'reasonabledays', views.TTReasonableDaysViewSet)
# routerTTapp.register(r'stabilize', views.TTStabilizeViewSet)
# routerTTapp.register(r'minhalfdays', views.TTMinHalfDaysViewSet)
# routerTTapp.register(r'minnonpreferedslots', views.TTMinNonPreferedSlotsViewSet)
# routerTTapp.register(r'avoidbothtimes', views.TTAvoidBothTimesViewSet)
# routerTTapp.register(r'simultaneouscourses', views.TTSimultaneousCoursesViewSet)
# routerTTapp.register(r'limitedstarttimechoices', views.TTLimitedStartTimeChoicesViewSet) # TODO: Fix
routerTTapp.register(r'constraint', views.FlopConstraintListViewSet, basename ="constraint")
routerTTapp.register('constraint/(?P<name>\w+)', views.FlopConstraintViewSet, basename ="constraint")
routerTTapp.register(r'constraint_types', views.FlopConstraintTypeViewSet, basename ="constraint_types")
routerTTapp.register(r'novisio', views.NoVisioViewSet, basename ="novisio")
routerTTapp.register(r'constraints_fields', views.FlopConstraintFieldViewSet, basename ="constraints_fields")
