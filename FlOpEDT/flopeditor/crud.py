# -*- coding: utf-8 -*-
"""
Python versions: Python 3.6

This file is part of the FlOpEDT/FlOpScheduler project.
Copyright (c) 2017
Authors: Iulian Ober, Paul Renaud-Goud, Pablo Seban, et al.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program. If not, see
<http://www.gnu.org/licenses/>.

You can be released from the requirements of the license by purchasing
a commercial license. Buying such a license is mandatory as soon as
you develop activities involving the FlOpEDT/FlOpScheduler software
without disclosing the source code of your own applications.


This module is used to establish the crud back-end interface.
"""

import json
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from base.models import Department
from flopeditor.cruds import training_programmes, student_group_type,\
    rooms, room_types, student_structural_group, course_type, period, module, tutors, student_transversal_group, \
    students


def good_request(request, department):
    """ Request rights verification
    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department: Department.
    :type department:  base.models.Department
    :return: true if the user has the right access to do the request
    :rtype:  boolean
    """
    if request.method == 'GET':
        return not request.user.is_anonymous and request.user.is_tutor
    return not request.user.is_anonymous and \
        request.user.has_department_perm(department, admin=True)


def crud_model(request, department_abbrev, crud):
    """Crud model for edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department_abbrev: Department abbreviation.
    :type department_abbrev:  String
    :param crud: Module associated to the crud.
    :type crud:  Module
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    if not good_request(request, department):
        return HttpResponseForbidden()

    if request.method == "GET":
        return crud.read(department)
    elif request.method == "POST":
        actions = json.loads(request.body.decode('utf-8'))['actions']
        result = []
        for action in actions:
            if action['request'] == 'NEW':
                result.append(crud.create(action, department))
            elif action['request'] == 'MODIFIED':
                result.append(crud.update(action, department))
            elif action['request'] == 'DELETED':
                result.append(crud.delete(action, department))
        return JsonResponse({
            'actions': result
        })
    return HttpResponseForbidden()


def crud_tutors(request, department_abbrev):
    """Crud url for rooms edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department_abbrev: Department abbreviation.
    :type department_abbrev:  String
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    if not good_request(request, department):
        pass
    elif request.method == "GET":
        return tutors.read()
    elif request.method == "POST":
        actions = json.loads(request.body.decode('utf-8'))['actions']
        result = []
        for action in actions:
            if action['request'] == 'NEW':
                result.append(tutors.create(request, action))
            elif action['request'] == 'MODIFIED':
                result.append(tutors.update(request, action))
            elif action['request'] == 'DELETED':
                result.append(tutors.delete(request, action))
        return JsonResponse({
            'actions': result
        })
    return HttpResponseForbidden()


def crud_rooms(request, department_abbrev):
    """Crud url for rooms edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department_abbrev: Department abbreviation.
    :type department_abbrev:  String
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    department = get_object_or_404(Department, abbrev=department_abbrev)
    if not good_request(request, department):
        pass
    elif request.method == "GET":
        return rooms.read()
    elif request.method == "POST":
        actions = json.loads(request.body.decode('utf-8'))['actions']
        result = []
        for action in actions:
            if action['request'] == 'NEW':
                result.append(rooms.create(request, action))
            elif action['request'] == 'MODIFIED':
                result.append(rooms.update(request, action))
            elif action['request'] == 'DELETED':
                result.append(rooms.delete(request, action))
        return JsonResponse({
            'actions': result
        })
    return HttpResponseForbidden()


def crud_room_types(request, department_abbrev):
    """Crud url for room types edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department_abbrev: Department abbreviation.
    :type department_abbrev:  String
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, room_types)


def crud_student_group_type(request, department_abbrev):
    """Crud url for student group type (TP, TD...) edition

    :param request: Client request.
    :param department_abbrev: Department abbreviation.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, student_group_type)


def crud_module(request, department_abbrev):
    """Crud url for module edition

    :param request: Client request.
    :param department_abbrev: Department abbreviation.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, module)


def crud_student_structural_group(request, department_abbrev):
    """Crud url for student group edition

    :param request: Client request.
    :param department_abbrev: Department abbreviation.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, student_structural_group)


def crud_student_transversal_group(request, department_abbrev):
    """Crud url for student group edition

    :param request: Client request.
    :param department_abbrev: Department abbreviation.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, student_transversal_group)

def crud_students(request, department_abbrev):
    """Crud url for student group edition

    :param request: Client request.
    :param department_abbrev: Department abbreviation.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, students)


def crud_training_programmes(request, department_abbrev):
    """Crud url for groups edition
    :param request: Client request.
    :param department_abbrev: Department abbreviation.
    :type request:  django.http.HttpRequest
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, training_programmes)


def crud_course(request, department_abbrev):
    """Crud url for course edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department_abbrev: Department abbreviation.
    :type department_abbrev:  String
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, course_type)


def crud_periods(request, department_abbrev):
    """Crud url for period edition

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param department_abbrev: Department abbreviation.
    :type department_abbrev:  String
    :return: Server response for the request.
    :rtype:  django.http.JsonResponse

    """
    return crud_model(request, department_abbrev, period)
