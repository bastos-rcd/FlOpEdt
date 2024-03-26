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


from random import randint

from django.http import HttpResponse
from django.shortcuts import render

from base.views import edt
from quote.admin import QuoteResource
from quote.forms import QuoteForm  # ProfForm, UserForm
from quote.models import Quote


def submit(req):
    visu = ''
    if req.method == 'POST':
        form = QuoteForm(req.POST)
        if form.is_valid():
            if req.POST.get('but') == 'Visualiser':
                visu = str(form.save(commit=False))
            elif req.POST.get('but') == 'Envoyer':
                form.save()
                return edt(req, None, None, 2)
            # dat = form.cleaned_data
            # return edt(req, None, None, 2)
    else:
        form = QuoteForm()  # initial = {}
    imgtxt = "Créateur d'emploi du temps <span id=\"flopPasRed\">Fl" \
             "</span>exible et <span id=\"flopRed\">Op</span>enSource"
    return render(req, 'quote/submit.html',
                  {'form': form,
                   'visu': visu,
                   'image': imgtxt})


def moderate(req):
    pass


def fetch_all_quotes(req):

    dataset = QuoteResource() \
        .export(Quote.objects.filter(status='A'))
    response = HttpResponse(dataset.json,
                            content_type='text/json')
    return response
