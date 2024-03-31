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


from django.db import models
from django.utils.translation import gettext_lazy as _

from TTapp.helpers.minhalfdays import MinHalfDaysHelperModule
from TTapp.TimetableConstraints.timetable_constraint import TimetableConstraint

from base.models import Module


class MinModulesHalfDays(TimetableConstraint):
    """
    All courses will fit in a minimum of half days
    """

    modules = models.ManyToManyField("base.Module", blank=True)

    class Meta:
        verbose_name = _("Minimize used half-days for modules")
        verbose_name_plural = verbose_name

    def considered_modules(self, ttmodel=None):
        if ttmodel is not None:
            modules_to_consider = set(ttmodel.data.modules)
        else:
            modules_to_consider = set(
                Module.objects.filter(train_prog__department=self.department)
            )
        if self.modules.exists():
            modules_to_consider &= set(self.modules.all())
        return modules_to_consider

    def enrich_ttmodel(self, ttmodel, period, ponderation=1):
        helper = MinHalfDaysHelperModule(ttmodel, self, period, ponderation)
        for module in self.considered_modules(ttmodel):
            helper.enrich_model(module=module)

    def get_viewmodel(self):
        view_model = super().get_viewmodel()
        details = view_model["details"]

        if self.modules.exists():
            details.update(
                {"modules": ", ".join([module.abbrev for module in self.modules.all()])}
            )

        return view_model

    def one_line_description(self):
        text = "Minimise les demie-journées"

        if self.modules.exists():
            text += " de : " + ", ".join([str(module) for module in self.modules.all()])
        else:
            text += "de chaque module"

        if self.train_progs.exists():
            text += " de " + ", ".join(
                [train_prog.abbrev for train_prog in self.train_progs.all()]
            )
        else:
            text += " pour toutes les promos."

        return text

    def is_satisfied_for(self, period, version):
        unsatisfied_min_half_days_modules = []
        for module in self.considered_modules():
            considered_courses = self.get_courses_queryset_by_parameters(
                period=period, module=module
            )
            if not MinHalfDaysHelperModule.is_satisfied_for_one_object(
                period, version, considered_courses
            ):
                unsatisfied_min_half_days_modules.append(module)
        assert not unsatisfied_min_half_days_modules, (
            f"{self} is not satisfied for period {period} and version {version} :"
            f"{unsatisfied_min_half_days_modules}"
        )
