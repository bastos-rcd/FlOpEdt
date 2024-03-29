#!/bin/bash

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

echo Abbrev du département ?
read dep
echo Année ?
read year
echo Semaines ?
read weeks
time=$(date +%Y_%m_%d-%H-%M)

python -m cProfile -o misc/logs/c_profile/solve\_$dep\_$year\_$weeks\_$time.profile solve.py -d $dep -w $weeks -y $year

pyprof2calltree -i misc/logs/c_profile/solve\_$dep\_$year\_$weeks\_$time.profile -o misc/logs/c_profile/solve\_$dep\_$year\_$weeks\_$time.calltree