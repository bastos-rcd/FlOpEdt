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

from rest_framework import serializers
from base.models import CourseType

class VolumeAgrege:
    conditions_pour_continue = []
    facteur_continue = {}

    def __init__(self, agg_dict):
        self.module_id = agg_dict['module_id']
        self.tutor_id = agg_dict['tutor__id']
        self.course_type_id = agg_dict['course_type_id']
        self.module_ppn = agg_dict['module_ppn']
        self.nom_matiere = agg_dict['nom_matiere']
        self.abbrev_intervenant = agg_dict['abbrev_intervenant']
        self.prenom_intervenant = agg_dict['prenom_intervenant']
        self.nom_intervenant = agg_dict['nom_intervenant']
        self.type_cours = agg_dict['type_cours']
        self.formation_reguliere = 0
        self.formation_continue = 0
        self.conditional_add(agg_dict, True)

    def conditional_add(self, agg_dict, ok):
        if ok:
            course_type_id = agg_dict["type_id"]
            course_type = CourseType.objects.get(id=course_type_id)
            dept_abbrev = course_type.department.abbrev
            duree = course_type.pay_duration
            if duree is None:
                duree = course_type.duration
            duree /= 60
            volume = agg_dict['nb_creneau'] * duree
            toadd_continue = 0
            for cpc in self.conditions_pour_continue:
                if all(agg_dict[key] == cpc[key] for key in cpc):
                    ct_name = course_type.name
                    toadd_continue = volume
                    if dept_abbrev in self.facteur_continue:
                        if ct_name in self.facteur_continue[dept_abbrev]:
                            toadd_continue *= self.facteur_continue[dept_abbrev][ct_name]
            self.formation_continue += toadd_continue
            self.formation_reguliere += volume - toadd_continue
            return None
        else:
            return VolumeAgrege(agg_dict)
            
    def add(self, agg_dict):
        return self.conditional_add(
            agg_dict,
            self.module_id == agg_dict['module_id'] \
            and self.tutor_id == agg_dict['tutor__id'] \
            and self.course_type_id == agg_dict['course_type_id']
        )

    def __str__(self):
        return f"{self.abbrev_intervenant} {self.module_ppn} {self.type_cours} ({self.formation_reguliere}|{self.formation_continue})"
        

class ScheduledCoursePaySerializer(serializers.Serializer):
    module_ppn = serializers.CharField()
    nom_matiere = serializers.CharField()
    abbrev_intervenant = serializers.CharField()
    prenom_intervenant = serializers.CharField()
    nom_intervenant = serializers.CharField()
    type_cours = serializers.CharField()
    formation_reguliere = serializers.FloatField()
    formation_continue = serializers.FloatField()


class DailyVolumeSerializer(serializers.Serializer):
    month = serializers.CharField()
    date = serializers.DateField()
    other = serializers.FloatField()
    td = serializers.FloatField()
    tp = serializers.FloatField()


class RoomDailyVolumeSerializer(serializers.Serializer):
    date = serializers.DateField()
    volume = serializers.FloatField()
