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

import json
import logging

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext as _

from core.decorators import tutor_or_superuser_required

import base.queries as queries

from people.models import Tutor, GroupPreferences, StudentPreferences, Student, \
    UserPreferredLinks, PhysicalPresence, User
from people.admin import TutorResource, GroupPreferencesResource, \
    StudentPreferencesResource, UserPreferredLinksResource, PhysicalPresenceResource
from base.models import Department, Week, Theme

logger = logging.getLogger(__name__)


@login_required
def redirect_change_people_kind(req):
    if req.user.is_student:
        return redirect('people:change_student')
    if req.user.is_tutor:
        if req.user.tutor.status == Tutor.FULL_STAFF:
            return redirect('people:change_fullstaff')
        if req.user.tutor.status == Tutor.SUPP_STAFF:
            return redirect('people:change_supplystaff')
        if req.user.tutor.status == Tutor.BIATOS:
            return redirect('people:change_BIATOS')
    else:
        raise Http404("Who are you?")


def fetch_tutors(req):
    dataset = TutorResource().export(Tutor.objects.all())
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response


def fetch_preferences_group(req):
    dataset = GroupPreferencesResource().export(GroupPreferences.objects.all())
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response


def fetch_preferences_students(req):
    dataset = StudentPreferencesResource().export(StudentPreferences.objects.all())
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response


@login_required
def student_preferences(req):
    if req.method == 'POST':
        logger.info(f'REQ: student preferences {req}')
        if req.user.is_authenticated and req.user.is_student:
            user = req.user
            morning_weight = req.POST['morning_evening']
            free_half_day_weight = req.POST['light_free']
            hole_weight = req.POST['hole_nothole']
            eat_weight = req.POST['eat']

            student = Student.objects.get(username=user.username)
            student_pref, created = StudentPreferences.objects.get_or_create(student=student)
            if created:
                student_pref.save()
            student_pref.morning_weight = morning_weight
            student_pref.free_half_day_weight = free_half_day_weight
            student_pref.hole_weight = hole_weight
            student_pref.eat_weight = eat_weight

            student_pref.save()
            group_pref = None
            for group in student.generic_groups.all():
                group_pref, created = GroupPreferences.objects.get_or_create(group=group)
                if created:
                    group_pref.save()
            if group_pref is not None:
                group_pref.calculate_fields()
                group_pref.save()
            return redirect("people:student_preferences")
        else:
            raise Http404("Who are you?")
    else:
        if req.user.is_authenticated and req.user.is_student:
            student = Student.objects.get(username=req.user.username)
            try:
                student_pref = StudentPreferences.objects.get(student=student)
            except ObjectDoesNotExist:
                student_pref = StudentPreferences(student=student)
                student_pref.save()

            # To display the correct text once we validate the form without move the input
            morning = student_pref.morning_weight
            morning_txt = ""
            if morning == 0:
                morning_txt = 'Commencer le plus tôt possible mais finir tôt'
            if morning == 0.25:
                morning_txt = 'Ne pas commencer trop tard et ne pas finir trop tard'
            if morning == 0.5:
                morning_txt = 'Ni trop tôt ni trop tard'
            if morning == 0.75:
                morning_txt = 'Ne pas commencer trop tôt et finir plus tard'
            if morning == 1:
                morning_txt = 'Commencer le plus tard possible mais finir tard'

            free_half_day = student_pref.free_half_day_weight
            free_half_day_txt = ""
            if free_half_day == 0:
                free_half_day_txt = 'Avoir toute la semaine des journées allégées'
            if free_half_day == 0.25:
                free_half_day_txt = 'Avoir plus de journées allégées que de demi-journées libérées'
            if free_half_day == 0.5:
                free_half_day_txt = 'Avoir des semaines équilibrées'
            if free_half_day == 0.75:
                free_half_day_txt = 'Avoir plus de demi-journées libérées que de journées allégées'
            if free_half_day == 1:
                free_half_day_txt = 'Avoir des journées chargées mais aussi des demi-journées libérées'

            hole = student_pref.hole_weight
            hole_txt = ""
            if hole == 0:
                hole_txt = 'Ne pas avoir de trous entre deux cours'
            if hole == 0.5:
                hole_txt = 'Indifférent'
            if hole == 1:
                hole_txt = 'Avoir des trous entre deux cours'

            eat = student_pref.eat_weight
            eat_txt = ""
            if eat == 0:
                eat_txt = 'Manger plus tôt'
            if eat == 0.5:
                eat_txt = 'Indifférent'
            if eat == 1:
                eat_txt = 'Manger plus tard'

            day = Department.objects.get(abbrev='INFO')

            themes = []
            for a in Theme:
                themes.append(a.value)

            return TemplateResponse(
                req,
                'people/studentPreferencesSelection.html',
                {'morning': morning,
                 'morning_txt': morning_txt,
                 'free_half_day': free_half_day,
                 'free_half_day_txt': free_half_day_txt,
                 'hole': hole,
                 'hole_txt': hole_txt,
                 'selfeat': eat,
                 'eat_txt': eat_txt,
                 'user_notifications_pref':
                     queries.get_notification_preference(req.user),
                 'themes': themes,
                 'theme': queries.get_theme_preference(req.user),
                 })
        else:
            # Make a decorator instead
            raise Http404("Who are you?")


def fetch_user_preferred_links(req, **kwargs):
    pref = UserPreferredLinks.objects \
        .prefetch_related('user__departments') \
        .filter(user__departments=req.department)
    dataset = UserPreferredLinksResource().export(pref)
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response


def fetch_physical_presence(req, year, week, **kwargs):
    presence = PhysicalPresence.objects.filter(user__departments=req.department,
                                               week__year=year,
                                               week__nb=week)
    dataset = PhysicalPresenceResource().export(presence)
    response = HttpResponse(dataset.csv,
                            content_type='text/csv')
    return response


@tutor_or_superuser_required
def change_physical_presence(req, year, week_nb, user):
    bad_response = {'status': 'KO'}

    if not req.is_department_admin and req.user.username != user:
        bad_response['more'] = _(f'Not allowed')
        return JsonResponse(bad_response)

    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        bad_response['more'] = _(f'No such user as {user}')
        return JsonResponse(bad_response)

    good_response = {'status': 'OK', 'more': ''}

    changes = json.loads(req.POST.get('changes', '{}'))
    logger.info("List of changes")
    for change in changes:
        logger.info(change)
    print(week_nb, year)
    # Default week at None
    if week_nb == 0 or year == 0:
        week = None
    else:
        try:
            week = Week.objects.get(nb=week_nb, year=year)
        except Week.DoesNotExist:
            bad_response['more'] = 'Wrong week'
            return JsonResponse(bad_response)

    for change in changes:
        logger.info(f"Change {change}")
        if not change['force_here']:
            PhysicalPresence.objects.filter(week=week,
                                            day=change['day'],
                                            user=user).delete()
        else:
            PhysicalPresence.objects.create(week=week,
                                            day=change['day'],
                                            user=user)

    return JsonResponse(good_response)
