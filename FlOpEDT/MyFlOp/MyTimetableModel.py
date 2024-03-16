#!/usr/bin/env python3
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

import importlib

from TTapp.TimetableModel import TimetableModel, GUROBI_NAME

from MyFlOp.MyTimetableUtils import number_courses, print_differences


class MyTimetableModel(TimetableModel):
    def __init__(self, department_abbrev, periods,
                 train_prog=None,
                 stabilize_version_nb=None,
                 min_nps_i=1.,
                 min_bhd_g=1.,
                 min_bd_i=1.,
                 min_bhd_i=1.,
                 min_nps_c=1.,
                 max_stab=5.,
                 lim_ld=1.,
                 core_only=False,
                 send_mails=False,
                 slots_step=None,
                 keep_many_solution_files=False,
                 min_visio=0.5,
                 pre_assign_rooms=False,
                 post_assign_rooms=True):
        """
        If you shall change something in the database ahead of creating the
        problem, you must write it here, before calling TimetableModel's constructor.

        """
        TimetableModel.__init__(self, department_abbrev, periods,
                         train_prog=train_prog,
                         stabilize_version_nb=stabilize_version_nb,
                         min_nps_i=min_nps_i,
                         min_bhd_g=min_bhd_g,
                         min_bd_i=min_bd_i,
                         min_bhd_i=min_bhd_i,
                         min_nps_c=min_nps_c,
                         max_stab=max_stab,
                         lim_ld=lim_ld,
                         core_only=core_only,
                         send_mails=send_mails,
                         slots_step=slots_step,
                         keep_many_solution_files=keep_many_solution_files,
                         min_visio=min_visio,
                         pre_assign_rooms=pre_assign_rooms,
                         post_assign_rooms=post_assign_rooms)

    def add_specific_constraints(self):
        """
        The speficic constraints stored in the database are added by the
        TimetableModel class.
        If you shall add more specific ones, you may write it down here.
        """
        TimetableModel.add_specific_constraints(self)

    def solve(self, time_limit=None, target_version_nb=None,
              solver=GUROBI_NAME, threads=None, ignore_sigint=True, send_gurobi_logs_email_to=None,
              with_numerotation=True):
        """
        If you shall add pre (or post) processing apps, you may write them down
        here.
        """
        result_version = TimetableModel.solve(self,
                                         time_limit=time_limit,
                                         target_version_nb=target_version_nb,
                                         solver=solver,
                                         threads=threads,
                                         ignore_sigint=ignore_sigint,
                                         send_gurobi_logs_email_to=send_gurobi_logs_email_to)

        if result_version is not None and self.stabilize_version_nb is not None:
            print_differences(self.department, self.periods,
                              self.stabilize_version_nb, target_version_nb, self.wdb.instructors)

        if with_numerotation:
            number_courses(self.department, periods=self.periods,
                           version_majour=result_version)
            
        return result_version

