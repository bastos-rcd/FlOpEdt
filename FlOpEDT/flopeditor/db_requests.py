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


This module is used to declare the database interactions related to flop!EDITOR, an app used
to manage a department statistics for FlOpEDT.
"""


from base.models import Day, Department, TimeGeneralSettings
from people.models import (
    BIATOS,
    FullStaff,
    SupplyStaff,
    Tutor,
    User,
    UserDepartmentSettings,
)

TUTOR_CHOICES_LIST = ["Permanent", "Vacataire", "Biatos"]

TUTOR_CHOICES_DICT = {
    Tutor.FULL_STAFF: TUTOR_CHOICES_LIST[0],
    Tutor.SUPP_STAFF: TUTOR_CHOICES_LIST[1],
    Tutor.BIATOS: TUTOR_CHOICES_LIST[2],
}


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
        UserDepartmentSettings(
            user=tutor, department=dept, is_main=False, is_admin=True
        ).save()

    TimeGeneralSettings(
        department=dept,
        day_start_time=8 * 60,
        day_end_time=18 * 60 + 45,
        morning_end_time=12 * 60 + 30,
        afternoon_start_time=14 * 60,
        days=[
            Day.MONDAY,
            Day.TUESDAY,
            Day.WEDNESDAY,
            Day.THURSDAY,
            Day.FRIDAY,
        ],
    ).save()


def update_departments_in_database(
    old_dept_name, new_dept_name, old_dept_abbrev, new_dept_abbrev, admins_id
):
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
    # We change the name and department abbrevs
    dept.name = new_dept_name
    dept.abbrev = new_dept_abbrev
    # We delete the rights of all the department admins
    uds = UserDepartmentSettings.objects.filter(department=dept)
    for user_dept_settings in uds:
        user_dept_settings.is_admin = False
        user_dept_settings.save()
    # We add admins rights to each admin selected
    for admin_id in admins_id:
        admin = Tutor.objects.get(id=admin_id)
        admin_dept_settings = UserDepartmentSettings.objects.get(
            user=admin, department=dept
        )
        admin_dept_settings.is_admin = True
        admin_dept_settings.save()
    dept.save()


def get_status_of_user(request):
    """
    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: status of user with position and employer if it's a supply_staff
    :rtype:  string status
    :rtype:  string position if supply_staff else None
    :rtype:  string employer if supply_staff else None

    """
    user = User.objects.get(username=request.user)
    if user.is_tutor:
        tutor = Tutor.objects.get(username=request.user)
        return get_status_of_tutor(tutor)
    else:
        return None, None, None


def get_status_of_tutor(tutor):
    """
    :param tutor: tutor.
    :type tutor:  people.models.Tutor
    :return: status of user with position and employer if it's a supply_staff
    :rtype:  string status
    :rtype:  string position if supply_staff else None
    :rtype:  string employer if supply_staff else None

    """
    if tutor.status == Tutor.FULL_STAFF:
        status = TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]
    elif tutor.status == Tutor.SUPP_STAFF:
        status = TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]
        try:
            supply_staff = SupplyStaff.objects.get(username=tutor.username)
            return status, supply_staff.position, supply_staff.employer
        except SupplyStaff.DoesNotExist:
            pass
    else:
        status = TUTOR_CHOICES_DICT[Tutor.BIATOS]
    return status, None, None


def get_is_iut(request):
    """

    :param request: Client request.
    :type request:  django.http.HttpRequest
    :return: true if FullStaff and is_iut
    :rtype:  Boolean


    """
    user = User.objects.get(username=request.user)
    if user.is_tutor:
        tutor = Tutor.objects.get(username=request.user)
        if tutor.status == Tutor.FULL_STAFF:
            try:
                fullstaff = FullStaff.objects.get(username=request.user)
                return fullstaff.is_iut
            except FullStaff.DoesNotExist:
                pass

    return None


def update_user_in_database(request):
    """
    update user in database

    :param request: Client request.
    :type request:  django.http.HttpRequest

    """
    old_username = request.user.username
    new_username = request.POST["newIdProfil"]
    new_first_name = request.POST["newFirtNameProfil"]
    new_last_name = request.POST["newLastNameProfil"]
    new_email = request.POST["newEmailProfil"]
    new_status = request.POST["newInputStatus"]
    old_status = request.POST["oldStatus"]
    new_status_vacataire = request.POST["newstatusVacataire"]
    new_employer = request.POST["newEmployer"]
    new_is_iut = "iut" in request.POST
    tutor = Tutor.objects.get(username=old_username)

    if old_status == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
        user = FullStaff.objects.get(id=tutor.id)
    elif old_status == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]:
        user = SupplyStaff.objects.get(id=tutor.id)
    else:
        user = BIATOS.objects.get(id=tutor.id)

    if old_status != new_status and new_status == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
        user_update = FullStaff(tutor_ptr_id=tutor.id)
        user_update.__dict__.update(tutor.__dict__)
        user_update.username = new_username
        user_update.first_name = new_first_name
        user_update.last_name = new_last_name
        user_update.email = new_email
        user_update.status = Tutor.FULL_STAFF
        user_update.is_iut = new_is_iut
        user_update.save()
        user.delete(keep_parents=True)
    elif (
        old_status != new_status and new_status == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]
    ):
        user_update = SupplyStaff(tutor_ptr_id=tutor.id)
        user_update.__dict__.update(tutor.__dict__)
        user_update.username = new_username
        user_update.first_name = new_first_name
        user_update.last_name = new_last_name
        user_update.email = new_email
        user_update.status = Tutor.SUPP_STAFF
        user_update.employer = new_employer
        user_update.position = new_status_vacataire
        user_update.save()
        user.delete(keep_parents=True)
    elif old_status != new_status:
        user_update = BIATOS(tutor_ptr_id=tutor.id)
        user_update.__dict__.update(tutor.__dict__)
        user_update.username = new_username
        user_update.first_name = new_first_name
        user_update.last_name = new_last_name
        user_update.email = new_email
        user_update.status = Tutor.BIATOS
        user_update.save()
        user.delete(keep_parents=True)
    else:
        user.username = new_username
        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        if new_status == TUTOR_CHOICES_DICT[Tutor.SUPP_STAFF]:
            user.employer = new_employer
            user.position = new_status_vacataire
        elif new_status == TUTOR_CHOICES_DICT[Tutor.FULL_STAFF]:
            user.is_iut = new_is_iut
        user.save()
