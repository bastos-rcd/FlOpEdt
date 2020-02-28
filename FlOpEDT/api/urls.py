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

from rest_framework import routers, permissions
from api import views
from django.urls import path
from django.conf.urls import include, url
from django.views.generic import RedirectView
from rest_framework.schemas import get_schema_view
from django.contrib.auth.decorators import login_required
from rest_framework.authtoken.views import obtain_auth_token 
# from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
from rest_framework_swagger.views import get_swagger_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

#####################################
# URLS based on django applications #
#####################################
app_name = "api"

routerBase = routers.SimpleRouter()
routerPeople = routers.SimpleRouter()
routerDisplayweb = routers.SimpleRouter()
routerTTapp = routers.SimpleRouter()
routerFetch = routers.SimpleRouter()


# routerBase.register(r'studentspreferences', views.StudentPreferencesViewSet, basename="students")
# routerBase.register(r'groupspreferences', views.GroupPreferencesViewSet)
routerBase.register(r'departments', views.DepartmentViewSet)
routerBase.register(r'trainingprograms', views.TrainingProgramsViewSet)
routerBase.register(r'grouptypes', views.GroupTypesViewSet)
routerBase.register(r'groups', views.GroupsViewSet, basename="groups")
routerBase.register(r'holidays', views.HolidaysViewSet)
routerBase.register(r'traininghalfdays', views.TrainingHalfDaysViewSet)
routerBase.register(r'periods', views.PeriodsViewSet)
routerBase.register(r'timesettings', views.TimeGeneralSettingsViewSet)
routerBase.register(r'roomtypes', views.RoomTypesViewSet)
routerBase.register(r'roomgroups', views.RoomGroupsViewSet)
routerBase.register(r'rooms', views.RoomsViewSet)
routerBase.register(r'roomsorts', views.RoomSortsViewSet)
routerBase.register(r'modules', views.ModulesViewSet)
routerBase.register(r'modules-course', views.Modules_Course_ViewSet)
routerBase.register(r'coursetypes', views.CourseTypesViewSet)
routerBase.register(r'courses', views.CoursesViewSet)
routerBase.register(r'edtversions', views.EdtVersionsViewSet)
routerBase.register(r'coursemodifications', views.CourseModificationsViewSet)
routerBase.register(r'planningmodifications', views.PlanningModificationsViewSet)
routerBase.register(r'tutorcosts', views.TutorCostsViewSet)
routerBase.register(r'groupcosts', views.GroupCostsViewSet)
routerBase.register(r'groupfreehalfdays', views.GroupFreeHalfDaysViewSet)
routerBase.register(r'dependencies', views.DependenciesViewSet)
routerBase.register(r'coursesstarttimeconstraints', views.CourseStartTimeConstraintsViewSet)
routerBase.register(r'regens', views.RegensViewSet)
routerBase.register(r'login', views.LoginView, basename="login")
routerBase.register(r'logout', views.LogoutView, basename="logout")

routerPeople.register(r'users', views.UsersViewSet)
routerPeople.register(r'userdepartmentsettings', views.UserDepartmentSettingsViewSet)
routerPeople.register(r'tutors', views.TutorsViewSet)
routerPeople.register(r'supplystaff', views.SupplyStaffsViewSet)
routerPeople.register(r'students', views.StudentsViewSet)
routerPeople.register(r'default', views.UsersPreferences_Default_ViewSet, basename="default")
routerPeople.register(r'single-week', views.UsersPreferences_Single_ViewSet, basename="single-week")
routerPeople.register(r'single-week-or-default', views.UsersPreferences_SingleODefault_ViewSet, basename="single-week-or-default")
routerPeople.register(r'coursepreferences', views.CoursePreferencesViewSet)
routerPeople.register(r'roompreferences', views.RoomPreferencesViewSet)


routerDisplayweb.register(r'breakingnews', views.BreakingNewsViewSet)
routerDisplayweb.register(r'moduledisplays', views.ModuleDisplaysViewSet)
routerDisplayweb.register(r'trainingprogrammedisplays', views.TrainingProgrammeDisplaysViewSet)
routerDisplayweb.register(r'groupdisplays', views.GroupDisplaysViewSet)


routerTTapp.register(r'customconstrains', views.TTCustomConstraintsViewSet)
routerTTapp.register(r'limitcoursetypetimeperperiods', views.TTLimitCourseTypeTimePerPeriodsViewSet)
routerTTapp.register(r'reasonabledays', views.TTReasonableDaysViewSet)
routerTTapp.register(r'stabilize', views.TTStabilizeViewSet)
routerTTapp.register(r'minhalfdays', views.TTMinHalfDaysViewSet)
routerTTapp.register(r'minnonpreferedslots', views.TTMinNonPreferedSlotsViewSet)
routerTTapp.register(r'avoidbothtimes', views.TTAvoidBothTimesViewSet)
routerTTapp.register(r'simultaneouscourses', views.TTSimultaneousCoursesViewSet)
routerTTapp.register(r'limitedstarttimechoices', views.TTLimitedStartTimeChoicesViewSet) # TODO: Fix
routerTTapp.register(r'limitiedroomchoices', views.TTLimitedRoomChoicesViewSet)

routerFetch.register(r'scheduledcourses', views.ScheduledCoursesViewSet, basename='scheduledcourses')
routerFetch.register(r'unscheduledcourses', views.UnscheduledCoursesViewSet, basename='unscheduledcourses')
routerFetch.register(r'availabilities', views.AvailabilitiesViewSet, basename='availabilities')
routerFetch.register(r'dweek', views.DefaultWeekViewSet, basename='dweek')
routerFetch.register(r'coursedefweek', views.CourseDefaultWeekViewSet, basename='coursedefweek')
routerFetch.register(r'trainprogs', views.TrainingProgramsViewSet)
routerFetch.register(r'allversions', views.AllVersionsViewSet)
routerFetch.register(r'alltutors', views.AllTutorsViewSet)
routerFetch.register(r'alldepts', views.DepartmentsViewSet)
routerFetch.register(r'tutorcourses', views.TutorCoursesViewSet, basename='tutorcourses')
routerFetch.register(r'extrasched', views.ExtraSchedCoursesViewSet, basename='extrasched')
routerFetch.register(r'bknews', views.BKNewsViewSet, basename='BKNews')
routerFetch.register(r'coursetypes', views.AllCourseTypesViewSet)


######################
# User friendly URLS #
######################

routerPreferences= routers.SimpleRouter()

# routerPreferences.register(r'students', views.StudentPreferencesViewSet, basename="students")
# routerPreferences.register(r'groups', views.GroupPreferencesViewSet)
routerPreferences.register(r'default', views.UsersPreferences_Default_ViewSet, basename="default")
routerPreferences.register(r'single-week', views.UsersPreferences_Single_ViewSet, basename="single-week")
routerPreferences.register(r'single-week-or-default', views.UsersPreferences_SingleODefault_ViewSet, basename="single-week-or-default")
routerPreferences.register(r'course', views.CoursePreferencesViewSet)
routerPreferences.register(r'room', views.RoomPreferencesViewSet)
routerPreferences.register(r'test-user-def', views.UserPreferenceDefaultViewSet, basename="plop")
routerPreferences.register(r'test-user-single', views.UserPreferenceSingleViewSet, basename="plop")
routerPreferences.register(r'test-user-sowdef', views.UserPreferenceSingleOwDefaultViewSet, basename="plop")


routerRooms = routers.SimpleRouter()

routerRooms.register(r'types', views.RoomTypesViewSet)
routerRooms.register(r'groups', views.RoomGroupsViewSet)
routerRooms.register(r'rooms', views.RoomsViewSet)
routerRooms.register(r'sorts', views.RoomSortsViewSet)

routerCourses = routers.SimpleRouter()

routerCourses.register(r'modules', views.ModulesViewSet)
routerCourses.register(r'modules-course', views.Modules_Course_ViewSet)
routerCourses.register(r'types', views.CourseTypesViewSet)
routerCourses.register(r'courses', views.CoursesViewSet)

routerGroups = routers.SimpleRouter()

routerGroups.register(r'types', views.GroupTypesViewSet)
routerGroups.register(r'groups', views.GroupsViewSet, basename="groups")

################
# SWAGGER VIEW #
################
schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^$', views.LoginView.as_view()),
    url(r'^logout/$', views.LogoutView.as_view()),
    url(r'^backoffice/$', login_required(views.TemplateView.as_view(template_name='logout.html'))),
    path('base/', include(routerBase.urls)),
    path('user/', include(routerPeople.urls)),
    path('display/', include(routerDisplayweb.urls)),
    path('ttapp/', include(routerTTapp.urls)),
    path('fetch/', include(routerFetch.urls)),
    path('rest-auth/', include('rest_auth.urls')),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    url('doc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('preferences/', include(routerPreferences.urls)),
    path('rooms/', include(routerRooms.urls)),
    path('courses/', include(routerCourses.urls)),
    path('groups/', include(routerGroups.urls)),
]