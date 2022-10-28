# -*- coding: utf-8 -*-

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

import logging

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import login
from django.shortcuts import redirect
from django.views.generic import CreateView, UpdateView

from base.models import TimeGeneralSettings, Department, UserPreference, Day

from .forms import AddFullStaffTutorForm, AddSupplyStaffTutorForm, AddBIATOSTutorForm
from .forms import ChangeFullStaffTutorForm, ChangeSupplyStaffTutorForm, ChangeBIATOSTutorForm
from .models import User, FullStaff, SupplyStaff, BIATOS, TutorPreference

logger = logging.getLogger(__name__)


class ChangeFullStaffTutor(UpdateView):
    model = FullStaff
    from_class = ChangeFullStaffTutorForm
    template_name = 'people/changeuser.html'
    fields = ('email', 'is_iut', )
    success_url = '/'
    
    def get_object(self, queryset=None):
        return self.request.user if self.request.user.is_authenticated else None
         

class ChangeSupplyStaffTutor(UpdateView):
    model = SupplyStaff
    from_class = ChangeSupplyStaffTutorForm
    template_name = 'people/changeuser.html'
    fields = ('email', 'employer', 'position', 'field', )
    success_url = '/'
    
    def get_object(self, queryset=None):
        return self.request.user if self.request.user.is_authenticated else None
         

class ChangeBIATOSTutor(UpdateView):
    model = BIATOS
    from_class = ChangeBIATOSTutorForm
    template_name = 'people/changeuser.html'
    fields = ('email', )
    success_url = '/'
    
    def get_object(self, queryset=None):
        return self.request.user if self.request.user.is_authenticated else None
         

def fill_default_user_preferences(user, dept=None):
    """
    Insert default preferences for the default week
    TO BE COMPLETED if several departments
    """
    dst = 8*60
    lst = 13*60
    lft = 13*60
    dft = 18*60
    default_duration = 60
    days = [d[0] for d in Day.CHOICES]
    if dept is None:
        dept = Department.objects.first()
    if dept is not None:
        try:
            settings = TimeGeneralSettings.objects.get(department=dept)
            dst = settings.day_start_time
            lst = settings.lunch_break_start_time
            lft = settings.lunch_break_finish_time
            dft = settings.day_finish_time
            days = settings.days
            default_duration = settings.default_preference_duration
        except ObjectDoesNotExist:
            logger.info(f'No TimeGeneralSettings for department {dept}')

    current_time = dst
    first_day = days.pop()
    duration = default_duration
    
    # fill the first day of the week
    for max_time in [lst, dft]:

        # use default duration if fits, otherwise cut
        while current_time < max_time:
            if current_time + duration > max_time:
                duration = max_time - current_time
            pref = UserPreference(user=user,
                                  week=None,
                                  day=first_day,
                                  start_time=current_time,
                                  duration=duration,
                                  # hardcoded
                                  value=8)
            pref.save()
            current_time += duration
        if max_time == lst:
            duration = default_duration
            current_time = lft
            
    # copy the pattern for the other days
    for day in days:
        for pref in UserPreference.objects.filter(user=user,
                                                  week=None,
                                                  day=first_day):
            new_pref = UserPreference(user=user,
                                      week=None,
                                      day=day,
                                      start_time=pref.start_time,
                                      duration=pref.duration,
                                      value=pref.value)
            new_pref.save()
