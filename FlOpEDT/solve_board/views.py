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

from TTapp.TTConstraints.slots_constraints import ConsiderDependencies
from TTapp.TTConstraints.core_constraints import ConsiderTutorsUnavailability, NoSimultaneousGroupCourses
import json
import pulp

from django.http import JsonResponse, HttpResponse
from django.conf import settings
# from channels import Group
from django.template.response import TemplateResponse

from core.decorators import dept_admin_required

from base.models import TrainingProgramme, ScheduledCourse, Week
from base.core.period_weeks import PeriodWeeks
from TTapp.TTModel import get_ttconstraints

# from solve_board.consumers import ws_add

# String used to specify all filter
text_all='All'


def get_work_copies(department, week):
    """
    Get the list of working copies for a target week
    """
    period_filter = PeriodWeeks().get_filter(week=week)
    work_copies = ScheduledCourse.objects \
                    .filter(
                        period_filter,
                        course__module__train_prog__department=department) \
                    .values_list('work_copy', flat=True) \
                    .distinct()     
    
    return list(work_copies)

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

    # Get available solvers only on production environment
    solvers = get_pulp_solvers(not settings.DEBUG)
    
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
    constraints = get_ttconstraints(department, **kwargs)
    return [c.get_viewmodel() for c in constraints]


def get_context(department, year, week, train_prog=None):
    #
    #   Get contextual datas
    #
    week_object = Week.objects.get(nb=week, year=year)
    params = {'week': week_object}

    # Get constraints
    if train_prog and not train_prog == text_all:
        params.update({'train_prog':train_prog})

    constraints = get_constraints_viewmodel(department, **params)

    # Get working copy list
    work_copies = get_work_copies(department, week_object)

    context = { 
        'constraints': constraints,
        'work_copies': work_copies,
    }

    return context


@dept_admin_required
def fetch_context(req, train_prog, year, week, **kwargs):

    context = get_context(req.department, year, week, train_prog)
    return HttpResponse(json.dumps(context), content_type='text/json')

@dept_admin_required
def launch_pre_analyse(req, train_prog, year, week, type, **kwargs):
    resultat = { type: [] }
    result= dict()
    if type == "ConsiderTutorsUnavailability":
        if train_prog == "All" or not ConsiderTutorsUnavailability.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department):
            constraints = ConsiderTutorsUnavailability.objects.filter(department = req.department)
        else:
            constraints = ConsiderTutorsUnavailability.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department)
        for constraint in constraints:
            result = constraint.pre_analyse(week=Week.objects.get(nb= week, year =year))
            resultat[type].append(result)

    elif type == "NoSimultaneousGroupCourses":
        if train_prog == "All" or not NoSimultaneousGroupCourses.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department):
            constraints = NoSimultaneousGroupCourses.objects.filter(department = req.department)
        else:
            constraints = NoSimultaneousGroupCourses.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department)
        for constraint in constraints:
            result = constraint.pre_analyse(week=Week.objects.get(nb= week, year =year))
            resultat[type].append(result)

    elif type == "ConsiderDependencies":
        if train_prog == "All" or not ConsiderDependencies.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department):
            constraints = ConsiderDependencies.objects.filter(department = req.department)
        else:
            constraints = ConsiderDependencies.objects.filter(train_progs__in = TrainingProgramme.objects.filter(abbrev=train_prog).all(), department = req.department)
        for constraint in constraints:
            result = constraint.pre_analyse(week=Week.objects.get(nb= week, year =year))
            resultat[type].append(result)
            
    return JsonResponse(resultat)


@dept_admin_required
def main_board(req, **kwargs):

    department = req.department

    # Get week list
    period = PeriodWeeks(department, exclude_empty_weeks=True)
    week_list = period.get_weeks(format=True)

    # Get solver list
    solvers_viewmodel = get_pulp_solvers_viewmodel()

    # Get all TrainingProgramme
    all_tps = list(TrainingProgramme.objects \
                    .filter(department=department) \
                    .values_list('abbrev', flat=True)) 

    view_context = {
                   'department': department,
                   'text_all': text_all,
                   'weeks': json.dumps(week_list),
                   'train_progs': json.dumps(all_tps),
                   'solvers': solvers_viewmodel,
                   }
    
    # Get contextual datas (constraints, work_copies)
    if len(week_list) > 0:
        data_context = get_context(department, year=week_list[0][0], week=week_list[0][1])
        view_context.update({ k:json.dumps(v) for k, v in data_context.items()})
    
    return TemplateResponse(req, 'solve_board/main-board.html', view_context)

