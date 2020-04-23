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


This module is used to declare the database interactions related to FlopEditor, an app used
to manage a department statistics for FlOpEDT.
"""


from base.models import Department, TimeGeneralSettings, Day
from people.models import Tutor, UserDepartmentSettings, SupplyStaff, FullStaff, BIATOS





def create_departments_in_database(dept_name, dept_abbrev, tutors_id):
    """Create department with admin and default settings in database

    :param dept_name: Department name
    :type dept_name: String
    :param dept_abbrev: Department abbrev
    :type dept_abbrev: String
    :param tutor_id: Tutor id
    :type tutor_id: String
    """

    dept = Department(name=dept_name, abbrev=dept_abbrev)

    dept.save()
    for tutor_id in tutors_id:
        tutor = Tutor.objects.get(id=tutor_id)
        UserDepartmentSettings(user=tutor, department=dept,
                               is_main=False, is_admin=True).save()

    TimeGeneralSettings(
        department=dept,
        day_start_time=8*60,
        day_finish_time=18*60+45,
        lunch_break_start_time=12*60+30,
        lunch_break_finish_time=14*60,
        days=[
            Day.MONDAY,
            Day.TUESDAY,
            Day.WEDNESDAY,
            Day.THURSDAY,
            Day.FRIDAY,
        ]).save()

def update_departments_in_database(old_dept_name, new_dept_name,
                                   old_dept_abbrev, new_dept_abbrev, tutors_id):
    """Update department with admin and default settings in database

    :param dept_name: Department name
    :type dept_name: String
    :param old_dept_abbrev: Old department abbrev
    :type old_dept_abbrev: String
    :param new_dept_abbrev: New department abbrev
    :type new_dept_abbrev: String
    :param tutor_id: Tutor id
    :type tutor_id: String

    """
    dept = Department.objects.get(name=old_dept_name, abbrev=old_dept_abbrev)
    # On change les noms et abbreviations du departement
    dept.name = new_dept_name
    dept.abbrev = new_dept_abbrev
    # On retire les droits a tous les Tutor
    uds = UserDepartmentSettings.objects.filter(department=dept, is_admin=True)
    for u_d in uds:
        u_d.delete()
    # On ajoute chaque nouveau responsable
    for tutor_id in tutors_id:
        tutor = Tutor.objects.get(id=tutor_id)
        UserDepartmentSettings.objects.create(user=tutor, department=dept,
                                              is_main=False, is_admin=True)
    dept.save()



def get_status_of_user(request):
    """
    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: status of user with position and employer if he's a supply_staff
    :rtype:  string status
    :rtype:  string position if supply_staff else None
    :rtype:  string employer if supply_staff else None

    """
    tutor = Tutor.objects.get(username=request.user)
    if tutor.status == 'fs':
        status = 'Permanent'
    elif tutor.status == 'ss':
        status = 'Vacataire'
        supply_staff = SupplyStaff.objects.get(username=tutor.username)
        return status, supply_staff.position, supply_staff.employer
    else:
        status = 'Biatos'
    return status, None, None



def update_user_in_database(old_username, request):
    """
    update user in database

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :param old_username: username
    :type old_username: String

    """

    new_username = request.POST['newIdProfil']
    new_first_name = request.POST['newFirtNameProfil']
    new_last_name = request.POST['newLastNameProfil']
    new_email = request.POST['newEmailProfil']
    new_status = request.POST['newInputStatus']
    old_status = request.POST['oldStatus']
    new_status_vacataire = request.POST['newstatusVacataire']
    new_employer = request.POST['newEmployer']

    if old_status == 'Permanent':
        user = FullStaff.objects.get(username=old_username)
    elif old_status == 'Vacataire':
        user = SupplyStaff.objects.get(username=old_username)
    else:
        user = BIATOS.objects.get(username=old_username)

    user.username = new_username
    user.first_name = new_first_name
    user.last_name = new_last_name
    user.email = new_email
    if old_status != new_status and new_status == 'Permanent':
        user.__class__ = FullStaff
        user.status = 'fs'
    elif old_status != new_status and new_status == 'Vacataire':
        user.__class__ = SupplyStaff
        user.save()
        user.employer = new_employer
        user.position = new_status_vacataire
        user.status = 'ss'
    elif old_status != new_status:
        user.__class__ = BIATOS
        user.status = 'bi'
    user.save()
