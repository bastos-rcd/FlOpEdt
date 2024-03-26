# coding: utf-8
# !/usr/bin/python

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

from django.core.mail import EmailMessage

from base.models import Course, Department
from people.models import Tutor


def concerned_tutors(week_list, department):
    liste = []
    for tutor in Tutor.objects.filter(departments=department):
        if Course.objects.filter(week__in=week_list, tutor=tutor, type__department=department):
            liste.append(str(tutor.username) + ' <' + str(tutor.email) + '>')
    liste.sort()
    return liste


def send_reminder_email(week_list, department, date=None, tutors=None,
                        school_name=None, url=None,
                        sender_email=None):
    if len(week_list) == 1:
        week_text = f"de la semaine {week_list[0].nb}"
    else:
        week_text = f"des semaines {', '.join(week_list[i].nb for i in range(len(week_list)-1))}" + \
                    f" et {week_list[-1].nb}"

    subject = f"[flop!EDT-{department.abbrev}] Génération {week_text}"

    msg = f"Bonjour, \n" \
        f"Ce message pour vous annnoncer la (re)génération de l'emploi du temps {week_text} " \
        f"du département {department.name}"
    if school_name is not None:
        msg += f"de {school_name}.\n"
    if url is not None:
        msg += f"Merci de mettre à jour vos disponibilités sur le site" \
               f" {url}/edt/{department.abbrev}/ " \

    if date is None:
        msg += "dans les 48 heures.\n"
    else:
        import locale
        locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
        msg += f"avant le {date.strftime('%A %d %B')}.\n"

    msg += "Merci, et comme d'habitude n'hésitez pas à nous écrire pour toute remarque/question.\n" \
           "Les gestionnaires de l'EDT\n\n"
    msg += "NB: Ceci est un message automatique envoyé par flop!EDT, gestionnaire d'emploi du temps " \
           "flexible et opensource. https://flopedt.org"

    if tutors is None:
        recipients = concerned_tutors(week_list, department)
    else:
        recipients = [str(tutor.username) + ' <' + str(tutor.email) + '>' for tutor in tutors]
    email = EmailMessage(
        subject,
        msg,
        to=[sender_email],
        bcc=recipients)
    email.send(fail_silently=False)
