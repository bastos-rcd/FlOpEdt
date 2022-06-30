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

# Week numbers issues helper
# ---------------------------

from django.utils.translation import gettext_lazy as _

import datetime

import base.models

days_infos = {
    'm': {'shift': 0, 'slug': _('Mon.')},
    'tu': {'shift': 1, 'slug': _('Tue.')},
    'w': {'shift': 2, 'slug': _('Wed.')},
    'th': {'shift': 3, 'slug': _('Thu.')},
    'f': {'shift': 4, 'slug': _('Fri.')},
    'sa': {'shift': 5, 'slug': _('Sat.')},
    'su': {'shift': 6, 'slug': _('Sun.')}
}


def get_current_school_year():
    now = datetime.datetime.now()
    # TODO find a alternative way to test the swap month
    if now.month <= 6:
        school_year = now.year - 1
    else:
        school_year = now.year
    return school_year


current_year = actual_year = get_current_school_year()


# monday of Week #2
def monday_w2(y):
    eve = datetime.date(y, 1, 1)
    eve_w = eve.weekday()
    if eve_w < 4:
        m = eve + datetime.timedelta(7 - eve_w)
    else:
        m = eve + datetime.timedelta(14 - eve_w)
    return m


# week comprising the next working day
def current_week():
    now = datetime.date.today()
    mond = monday_w2(now.year)
    if now.weekday() > 4:
        now = now + datetime.timedelta(2)
    delta = now - mond
    return {'week': 2 + (delta.days // 7), 'year': now.year}


# list of days
def num_all_days(y, w, dept):
    if w == 0:
        return []
    monday = monday_w2(y) + datetime.timedelta(7 * (w - 2))
    day_list = []
    dept_day_list = base.models.TimeGeneralSettings.objects.get(
        department=dept).days
    iday = 0
    for d_ref in dept_day_list:
        cur_day = monday + datetime.timedelta(days_infos[d_ref]['shift'])
        day_list.append({'num': iday,
                         'date': f"{cur_day.day:02d}/{cur_day.month:02d}",
                         'ref': d_ref,
                         'name': days_infos[d_ref]['slug']})
        iday += 1
    return day_list

# More or less working weeks


def week_list():
    li = []
    for i in list(range(35, 53)):
        li.append({'week': i, 'year': actual_year})
    for i in list(range(1, 53)):
        li.append({'week': i, 'year': actual_year+1})
    return li


def year_by_week(week):
    if week > 36:
        return current_year
    else:
        return current_year + 1
