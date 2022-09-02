# coding: utf-8
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

import os
import json
import logging

from django.http import HttpResponse
from django.shortcuts import render
from django.db import transaction
from django.conf import settings

from core.decorators import dept_admin_required

from base.models import Department, Period, Week

from configuration.make_planif_file import make_planif_file
from configuration.make_filled_database_file import make_filled_database_file
from configuration.extract_planif_file import extract_planif
from configuration.deploy_database import extract_database_file
from configuration.file_manipulation import upload_file, check_ext_file
from configuration.forms import ImportPlanif, ImportConfig
from base.weeks import current_year

logger = logging.getLogger(__name__)

@dept_admin_required
def configuration(req, **kwargs):
    """
    Main view of Configuration
    :param req:
    :return:
    """
    arg_req = {}

    arg_req['form_config'] = ImportConfig()
    arg_req['form_planif'] = ImportPlanif()

    arg_req['departements'] = [{'name': depart.name, 'abbrev': depart.abbrev}
                               for depart in Department.objects.all() if not depart.abbrev == 'default']
    arg_req['periods'] = [{'name': period.name, 'department': period.department.abbrev}
                          for period in Period.objects.all()]
    arg_req['current_year'] = current_year
    return render(req, 'configuration/configuration.html', arg_req)


@dept_admin_required
def import_config_file(req, **kwargs):
    """
    View for the first step of the configuration. It imports the file
    to build the database, clear the database, extract the file to
    build the database and make the planif file for the second step
    of the configuration.
    Ajax request.

    :param req:
    :return:
    """
    if req.method == 'POST':
        form = ImportConfig(req.POST, req.FILES)
        logger.debug(req)
        logger.debug(req.FILES)
        if form.is_valid():
            logger.debug(req.FILES['fichier'])
            logger.debug(req.FILES['fichier'].name)
            if check_ext_file(req.FILES['fichier'], ['.xlsx', '.xls']):
                path = upload_file(req.FILES['fichier'], "uploaded_database_file.xlsx")
                # If one of method fail the transaction will be not commit.
                try:
                    with transaction.atomic():
                        dept_abbrev = req.POST['abbrev']
                        try:
                            dept_name = req.POST['name']
                        except:
                            dept_name = None
                        logger.debug(dept_name)
                        try:
                            dept = Department.objects.get(abbrev=dept_abbrev)
                            if not dept_name == dept.name and dept_name is not None:
                                response = {'status': 'error',
                                            'data': "Il existe déjà un département utilisant cette abbréviation."}
                                return HttpResponse(json.dumps(response), content_type='application/json')
                            dept_name = dept.name
                            dept.delete()
                            logger.debug("flush OK")
                        except Exception as e:
                            logger.warning(f'Exception with dept')
                            logger.warning(e)

                        extract_database_file(department_name=dept_name,
                                              department_abbrev=dept_abbrev, bookname=path)
                        logger.debug("extract OK")

                        os.rename(path, os.path.join(settings.MEDIA_ROOT,
                                                     'configuration',
                                                     f'database_file_{dept_abbrev}.xlsx'))
                        logger.warning("rename OK")
                        response = {'status': 'ok',
                                    'data': 'OK',
                                    'dept_abbrev': dept_abbrev,
                                    'dept_fullname': dept_name
                        }
                except Exception as e:
                    os.remove(path)
                    logger.debug(e)
                    response = {'status': 'error', 'data': str(e)}
                    return HttpResponse(json.dumps(response), content_type='application/json')
                dept = Department.objects.get(abbrev=dept_abbrev)
                source = os.path.join(settings.MEDIA_ROOT,
                                      'configuration',
                                      'empty_planif_file.xlsx')
                target_repo = os.path.join(settings.MEDIA_ROOT,
                                           'configuration')
                logger.info("start planif")
                make_planif_file(dept, empty_bookname=source, target_repo=target_repo)
                logger.info("make planif OK")
            else:
                response = {'status': 'error', 'data': 'Invalid format'}
        else:
            response = {'status': 'error', 'data': 'Form not valid'}
    return HttpResponse(json.dumps(response), content_type='application/json')


@dept_admin_required
def get_config_file(req, **kwargs):
    """
    Resend the empty configuration's file.

    :param req:
    :return:
    """
    f = open(f"{settings.MEDIA_ROOT}/configuration/empty_database_file.xlsx", "rb")
    response = HttpResponse(f, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="database_file.xls"'
    f.close()
    return response


@dept_admin_required
def get_planif_file(req, with_courses=False, **kwargs):
    """
    Send an empty planification's file.
    Rely on the configuration step if it was taken.
    :param req:
    :return:
    """
    logger.debug(req.GET['departement'])
    filename = os.path.join(settings.MEDIA_ROOT,
                             'configuration',
                             f"planif_file_{req.GET['departement']}")
    if with_courses:
        filename += '_with_courses'
    filename += ".xlsx"

    if not os.path.exists(filename):
        filename = os.path.join(settings.MEDIA_ROOT,
                                'configuration',
                                f"empty_planif_file.xlsx")
    f = open(filename, "rb")
    response = HttpResponse(f, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="planif_file.xlsx"'
    f.close()
    return response

@dept_admin_required
def get_filled_database_file(req, **kwargs):
    """
    Send an filled database file.
    Rely on the configuration step if it was taken.
    :param req:
    :return:
    """
    logger.debug(req.GET['departement'])
    basic_filename = f"database_file_{req.GET['departement']}"
    filename = os.path.join(settings.MEDIA_ROOT,
                             'configuration',
                             basic_filename)
    filename += ".xlsx"

    if not os.path.exists(filename):
        filename = os.path.join(settings.MEDIA_ROOT,
                                'configuration',
                                f"empty_database_file.xlsx")
    f = open(filename, "rb")
    response = HttpResponse(f, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="planif_file.xlsx"'
    f.close()
    return response


@dept_admin_required
def mk_and_dl_planif(req, with_courses, **kwargs):
    logger.debug(req.GET['departement'])
    dept_abbrev = req.GET['departement']
    dept = Department.objects.get(abbrev=dept_abbrev)
    source = os.path.join(settings.MEDIA_ROOT,
                          'configuration',
                          'empty_planif_file.xlsx')
    target_repo = os.path.join(settings.MEDIA_ROOT,
                               'configuration')
    logger.info("start planif")
    make_planif_file(dept, empty_bookname=source, target_repo=target_repo, with_courses=with_courses)
    return get_planif_file(req, with_courses, **kwargs)


@dept_admin_required
def mk_and_dl_database_file(req, **kwargs):
    logger.debug(req.GET['departement'])
    dept_abbrev = req.GET['departement']
    dept = Department.objects.get(abbrev=dept_abbrev)
    logger.info("start filled database file")
    make_filled_database_file(dept)
    return get_filled_database_file(req, **kwargs)


@dept_admin_required
def import_planif_file(req, **kwargs):
    """
    Import a planification's file filled. Before data processing, it must to
    check if the first step of te configuration is done. Extract the data of the xlsx file.

    :param req:
    :return:
    """
    form = ImportPlanif(req.POST, req.FILES)
    if form.is_valid():
        if check_ext_file(req.FILES['fichier'], ['.xlsx', '.xls']):
            logger.info(req.FILES['fichier'])
            path = upload_file(req.FILES['fichier'], "configuration/planif_file_.xlsx")
            # If one of methods fail, the transaction will be not commit.
            try:
                with transaction.atomic():
                    try:
                        dept = Department.objects.get(abbrev=req.POST['departement'])
                    except Exception as e:
                        response = {'status': 'error', 'data': str(e)}
                        return HttpResponse(json.dumps(response), content_type='application/json')
                    stabilize_courses = "stabilize" in req.POST
                    assign_colors = "assign_colors" in req.POST
                    print("AAAAA", assign_colors)
                    choose_weeks = "choose_weeks" in req.POST
                    choose_periods = "choose_periods" in req.POST
                    if choose_weeks:
                        week_nb = req.POST["week_nb"]
                        year = req.POST["year"]
                        if not week_nb and not year:
                            from_week = None
                        else:
                            week_nb = int(week_nb)
                            year = int(year)
                            from_week = Week.objects.get(nb=week_nb, year=year)
                        week_nb_end = req.POST["week_nb_end"]
                        year_end = req.POST["year_end"]
                        if not week_nb_end and not year_end:
                            until_week = None
                        else:
                            week_nb_end = int(week_nb_end)
                            year_end = int(year_end)
                            until_week = Week.objects.get(nb=week_nb_end, year=year_end)
                    else:
                        from_week = None
                        until_week = None

                    if choose_periods:
                        periods = Period.objects.filter(department=dept, name__in=req.POST.getlist('periods'))
                        print(periods)
                    else:
                        periods = None

                    extract_planif(dept, bookname=path, from_week=from_week, until_week=until_week, periods=periods,
                                   stabilize_courses=stabilize_courses, assign_colors=assign_colors)
                    logger.info("Extract file OK")
                    rep = "OK !"

                    os.rename(path, f"{settings.MEDIA_ROOT}/configuration/planif_file.xlsx")
                    logger.info("Rename OK")

                    response = {'status': 'ok', 'data': rep}
            except Exception as e:
                os.remove(path)
                logger.info(e)
                response = {'status': 'error', 'data': str(e)}
        else:
            response = {'status': 'error', 'data': 'Invalid format'}
    else:
        response = {'status': 'error', 'data': "Form can't be valid"}
    return HttpResponse(json.dumps(response), content_type='application/json')
