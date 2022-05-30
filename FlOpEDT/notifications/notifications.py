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

from core.decorators import timer
from base.models import Course, ScheduledCourse, Week, GenericGroup
from notifications.models import BackUpModif
from base.timing import flopdate_to_datetime, Day, french_format
from people.models import Tutor, NotificationsPreferences
import django
import os
import json
from datetime import date, datetime
from django.utils.translation import gettext_lazy as _
from django.utils.translation import gettext

from django.core.mail import send_mail
from django.utils.html import strip_tags

def backup():
    print("Deleting old backup")
    BackUpModif.objects.filter(new=False).delete()
    print("Old backup deleted")
    print("Converting recent backup in old one")
    old_backup = BackUpModif.objects.filter(new=True)
    for b in old_backup:
        b.new = False
        b.save()
    print("Old backup conversion done")
    print("New backup started")
    #Get week number by using isocalendar
    today = date.today()
    week_number = date(today.year, today.month, today.day).isocalendar()[1]
    week = Week.objects.get(nb=week_number, year=today.year)

    courses = Course.objects.filter(week__gte=week)
    scheduled_courses = ScheduledCourse.objects.filter(work_copy=0,
                                                       course__in=courses)

    for course in courses:
        #Get all fields necessary for modification check
        #A course can not be in ScheduledCourse
        scheduled_course=scheduled_courses.filter(course=course)
        if scheduled_course.exists():
            scheduled_course = scheduled_course[0]
            week = course.week.nb
            year = course.week.year
            day = scheduled_course.day
            module = course.module.abbrev
            course_type = course.type
            #Can have no tutor
            tutor = scheduled_course.tutor.username if scheduled_course.tutor != None else None
            #Can have no supp_tutors
            supp_tutors = list(course.supp_tutor.all()) if course.supp_tutor != None else None
            start_time = scheduled_course.start_time
            #Can have no room
            room = scheduled_course.room.name if scheduled_course.room != None else None
            #Multiple groups are possible for a single course
            groups = list(course.groups.all())
            for group in groups:
                train_prog = group.train_prog.abbrev
                department = group.train_prog.department.abbrev
                #Create a new BackUpModif object which represent the table used for backup, fill it and then save it
                line = BackUpModif()
                line.new = True
                line.week = week
                line.year = year
                line.day = day
                line.module_abbrev = module
                line.tutor_username = tutor
                line.supp_tutor_usernames = supp_tutors
                line.start_time = start_time
                line.room_name = room
                line.group_name = group.name
                line.department_abbrev = department
                line.train_prog_name = train_prog
                line.course_type_name = course_type
                line.save()
    print("Backup done")
    print("Number of courses saved : " + str(BackUpModif.objects.filter(new=True).count()))


def check_changes(save_json_files=False):
    new_backup = set(BackUpModif.objects.filter(new=True))
    old_backup = set(BackUpModif.objects.filter(new=False))
    news = new_backup - old_backup
    olds = old_backup - new_backup
    changes = olds | news

    # Create two dict that will be save as JSON at the end
    student_changes_dict = {}
    tutor_changes_dict = {}

    departments = {change.department_abbrev for change in changes}

    # Initialise user dict with all departments
    for department in departments:
        student_changes_dict[department] = {}

    for change in changes:
        if change in olds:
            mode = "Deleted"
            #Useful for translation
            gettext("Deleted")
        else:
            mode = "Created"
            #Useful for translation
            gettext("Created")
        group = change.group_name
        department = change.department_abbrev
        train_prog = change.train_prog_name
        tutor_username = change.tutor_username
        module = change.module_abbrev
        course_type = change.course_type_name
        room = change.room_name
        start_time = change.start_time
        week = Week.objects.get(year=change.year, nb=change.week)
        day = Day(week=week, day=change.day)
        change_datetime = flopdate_to_datetime(day, change.start_time)

        # Store all changes for users
        if train_prog not in student_changes_dict[department]:
            student_changes_dict[department][train_prog] = {}
        if group not in student_changes_dict[department][train_prog]:
            student_changes_dict[department][train_prog][group] = []
        student_object = {gettext('Mode'): mode,
                          gettext('Date'): change_datetime.date().strftime('%d/%m/%Y'),
                          gettext('Start time'): french_format(start_time),
                          gettext('Course Type'): course_type,
                          gettext('Module'): module,
                          gettext('Tutor'): tutor_username,
                          gettext('Room'): room}
        student_changes_dict[department][train_prog][group].append(student_object)

        # Store all changes for tutors
        if tutor_username not in tutor_changes_dict:
            tutor_changes_dict[tutor_username] = {}
        if department not in tutor_changes_dict[tutor_username]:
            tutor_changes_dict[tutor_username][department] = []
        tutor_object = {gettext('Mode'): mode,
                        gettext('Date'): change_datetime.date().strftime('%d/%m/%Y'),
                        gettext('Start time'): french_format(start_time),
                        gettext('Course Type'): course_type,
                        gettext('Module'): module,
                        gettext('Train_prog'): train_prog,
                        gettext('Group'): group,
                        gettext('Room'): room}
        tutor_changes_dict[tutor_username][department].append(tutor_object)

        if save_json_files:
            # Save users changes as JSON
            with open("notifications/modifs_student.json", "w") as outfile:
                json.dump(student_changes_dict, outfile)

            # Save tutors changes as JSON
            with open("notifications/modifs_tutor.json", "w") as outfile:
                json.dump(tutor_changes_dict, outfile)

    return student_changes_dict, tutor_changes_dict


def days_nb_from_today(change):
    string_date = change[gettext('Date')]
    datetime_date = datetime.strptime(string_date, "%d/%m/%Y").date()
    return (datetime_date - date.today()).days


def send_notifications():
    student_changes_dict, tutor_changes_dict = check_changes()
    # Choose department
    if not student_changes_dict:
        if not tutor_changes_dict:
            return
        else:
            department = list(list(tutor_changes_dict.values())[0].keys())[0]
    else:
        department = list(student_changes_dict.keys())[0]

    subject = _("[flop!Scheduler] Changes on your planning")

    outro_text = _(
        "This email is automatically generated by flop!Scheduler. To manage your notifications settings, "
        "please <a href='%(url)s/edt/%(dept)s/semaine-type'> click here <a/>.") % {'url': 'url_of_your_website',
                                                                                   'dept': department}

    for tutor_username, tutor_dic in tutor_changes_dict.items():
        if tutor_username is None:
            continue
        tutor = Tutor.objects.get(username=tutor_username)
        notif, c = NotificationsPreferences.objects.get_or_create(user=tutor)
        nb_of_notified_weeks = notif.nb_of_notified_weeks
        if not nb_of_notified_weeks:
            continue
        nb_of_notified_days = 7 * nb_of_notified_weeks
        filtered_changes = {}
        total_filtered_changes = []
        for department, changes in tutor_dic.items():
            filtered_changes[department] = [change for change in changes
                                            if 0 <= days_nb_from_today(change) <= nb_of_notified_days]
            total_filtered_changes += filtered_changes[department]
        if not total_filtered_changes:
            continue
        intro_text = _("Hi ") + tutor.first_name + ",<br /> <br />"
        intro_text += _("Here are the changes of your planning for the %g following days :") % nb_of_notified_days
        intro_text += "<br /> <br />"
        html_msg = ""
        for department in tutor_dic:
            dept_changes = filtered_changes[department]
            if not dept_changes:
                continue
            dept_changes.sort(key=lambda x: (x[gettext('Date')], x[gettext('Start time')]))
            html_msg += _("For the department %s :") % department + "<br />"
            html_msg += html_table_with_changes(dept_changes)
        send_changes_email(subject, intro_text, html_msg, outro_text, to_email=tutor.email)

    students = set()

    for dept_abbrev in student_changes_dict:
        for train_prog in student_changes_dict[dept_abbrev]:
            for group_name in student_changes_dict[dept_abbrev][train_prog]:
                group = GenericGroup.objects.get(name=group_name, train_prog__abbrev=train_prog,
                                                 train_prog__department__abbrev=dept_abbrev)
                students |= set(group.student_set.all())

    for student in students:
        notif, created = NotificationsPreferences.objects.get_or_create(user=student)
        if created:
            continue
        nb_of_notified_weeks = notif.nb_of_notified_weeks
        if not nb_of_notified_weeks:
            continue
        nb_of_notified_days = 7 * nb_of_notified_weeks
        intro_text = _("Hi ") + student.first_name + ",<br /> <br />"
        intro_text += _("Here are the changes of your planning for the %g following days :") % nb_of_notified_days
        intro_text += "<br /> <br />"
        groups = student.belong_to.all()
        department = groups[0].train_prog.department.abbrev
        student_changes = []
        for group in groups:
            student_changes += student_changes_dict[group.train_prog.department.abbrev][group.train_prog.abbrev][group.name]

        filtered_changes = [change for change in student_changes
                            if 0 <= days_nb_from_today(change) <= nb_of_notified_days]
        if not filtered_changes:
            continue
        filtered_changes.sort(key=lambda x: (x[gettext('Date')], x[gettext('Start time')]))
        html_msg = html_table_with_changes(filtered_changes)
        send_changes_email(subject, intro_text, html_msg, outro_text, to_email=student.email)


def html_table_with_changes(filtered_changes):
    msg = "<table>"
    titles = filtered_changes[0].keys()
    msg += f"<tr> "
    for title in list(titles):
        msg += f"<th> {_(title)} </th>"
    msg+= "</tr>\n"
    for fc in filtered_changes:
        values = list(fc.values())
        mode = values[0]
        msg += f"<tr class='{mode}'>"
        msg += f"<td> {gettext(mode)} </td>"
        for value in values[1:]:
            msg += f"<td> {value} </td>"
        msg += "</tr>\n"
    msg += "</table> <br />"
    return msg


def send_changes_email(subject, intro_text, html_msg, outro_text, to_email, from_email=""):
    html_message = f"""
         <html>
           <head>
            <style type="text/css">
            table {{border-collapse:collapse; margin:1em;}}
            th, td {{
                border:1px solid black; 
                text-align:center;
                padding-right:10px; 
                padding-left:10px;
            }}
            .Created {{background-color:lightgreen;}}
            .Deleted {{background-color:#ff6d50;}}
            </style>
           </head>
           <body>
             {intro_text}
             {html_msg}
             {outro_text}
           </body>
         </html>
         """
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)
