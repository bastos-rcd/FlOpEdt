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

import pulp
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, JsonResponse
# from channels import Group
from django.template.response import TemplateResponse
from django.utils.encoding import force_str
from django.utils.functional import Promise

from base.models import ScheduledCourse, SchedulingPeriod, TrainingProgramme
from core.decorators import dept_admin_required
from TTapp.FlopModel import get_flop_constraints
from TTapp.TimetableConstraints.core_constraints import (
    ConsiderTutorsUnavailability, NoSimultaneousGroupCourses)
from TTapp.TimetableConstraints.slots_constraints import ConsiderDependencies

# from solve_board.consumers import ws_add

# String used to specify all filter
text_all='All'


def get_version_majors(department, period):
    """
    Get the list of working copies for a target period
    """
    version_majors = ScheduledCourse.objects \
                    .filter(course__period=period,
                            course__module__train_prog__department=department) \
                    .values_list('version__major', flat=True) \
                    .distinct()     
    
    return list(version_majors)

def get_pulp_solvers(available=True):
    def recurse_solver_hierachy(solvers):
        for s in solvers:
            if available:
                try:
                    if s().available():
                        yield s
                except pulp.PulpSolverError:
                    # cf in pulp: pulp/apis/choco_api.py l38
                    # CHOCO solver poorly handled
                    pass
            else:
                yield s

            yield from recurse_solver_hierachy(s.__subclasses__())
    
    solvers = pulp.LpSolver_CMD.__subclasses__()
    return tuple(recurse_solver_hierachy(solvers))


def get_pulp_solvers_viewmodel():   

    # Build a dictionnary of supported solver 
    # classnames and readable names

    # Get available solvers only on production environment TODO : WHY???
    solvers = get_pulp_solvers() #if so : get_pulp_solvers(not settings.DEBUG)
    
    # Get readable solver name from solver class name
    viewmodel = []
    for s in solvers:
        key = s.__name__
        name = key.replace('PULP_', '').replace('_CMD', '')
        viewmodel.append((key, name))

    return viewmodel

def get_constraints_viewmodel(department, **kwargs):
    #
    # Extract simplified datas from constraints instances
    #
    constraints = get_flop_constraints(department, **kwargs)
    return [c.get_viewmodel() for c in constraints]


def get_context(department, period):
    #
    #   Get contextual datas
    #
    params = {'period': period}

    constraints = get_constraints_viewmodel(department, **params)

    # Get working copy list
    version_majors = get_version_majors(department, period)

    context = { 
        'constraints': constraints,
        'version_majors': version_majors,
    }

    return context


@dept_admin_required
def fetch_context(req, train_prog, period, **kwargs):

    context = get_context(req.department, period)
    return HttpResponse(json.dumps(context, cls=LazyEncoder), content_type='text/json')

@dept_admin_required
def launch_pre_analyse(req, train_prog, period, type, **kwargs):
    period = SchedulingPeriod.objects.get(id=period)
    resultat = { type: [] }
    result= dict()
    if type == "ConsiderTutorsUnavailability":
        constraints = ConsiderTutorsUnavailability.objects.filter(department = req.department)
        for constraint in constraints:
            result = constraint.pre_analyse(period=period)
            resultat[type].append(result)

    elif type == "NoSimultaneousGroupCourses":
        if train_prog == "All" or not NoSimultaneousGroupCourses.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department):
            constraints = NoSimultaneousGroupCourses.objects.filter(department = req.department)
        else:
            constraints = NoSimultaneousGroupCourses.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department)
        for constraint in constraints:
            result = constraint.pre_analyse(period=period)
            resultat[type].append(result)

    elif type == "ConsiderDependencies":
        if train_prog == "All" or not ConsiderDependencies.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department):
            constraints = ConsiderDependencies.objects.filter(department = req.department)
        else:
            constraints = ConsiderDependencies.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department)
        for constraint in constraints:
            result = constraint.pre_analyse(period=period)
            resultat[type].append(result)
    return JsonResponse(resultat)


@dept_admin_required
def main_board(req, **kwargs):

    department = req.department

    # Get periods names list
    periods = [{'id':sp.id, 'name':sp.name} for sp in department.scheduling_periods(exclude_empty=True)]

    # Get solver list
    solvers_viewmodel = get_pulp_solvers_viewmodel()

    # Get all TrainingProgramme
    all_tps = list(TrainingProgramme.objects \
                    .filter(department=department) \
                    .values_list('abbrev', flat=True)) 

    view_context = {
                   'department': department,
                   'text_all': text_all,
                   'periods': json.dumps(periods),
                   'train_progs': json.dumps(all_tps),
                   'solvers': solvers_viewmodel,
                   'email': req.user.email,
                   }
    
    # Get contextual datas (constraints, work_copies)
    if len(periods) > 0:
        data_context = get_context(department, period=periods[0]['id'])
        view_context.update({k:json.dumps(v, cls=LazyEncoder) for k, v in data_context.items()})
    
    return TemplateResponse(req, 'solve_board/main-board.html', view_context)


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_str(obj)
        return super(LazyEncoder, self).default(obj)
