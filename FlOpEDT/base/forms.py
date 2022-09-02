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

from django import forms
from people.models import Tutor, FullStaff
from base.models import Module, EnrichedLink
from django.utils.translation import gettext as _


class ContactForm(forms.Form):
    sender = forms.EmailField(label=_('Your e-mail address :'),
                              required=True)
    recipient = forms.CharField(
        label=_('Recipient :'),
        max_length=20,
        help_text=_("Pseudo"))
    subject = forms.CharField(
        label=_('Subject of the e-mail :'),
        max_length=100,
        help_text=_("100 characters max"))
    message = forms.CharField(label=_('Body of the message :'),
                              max_length=2000,
                              widget=forms.Textarea())

    def clean_recipient(self):
        recipient = self.cleaned_data['recipient']
        if not Tutor.objects.filter(username=recipient).exists():
            raise forms.ValidationError(_("This person doesn't exist."))
        return recipient


class PerfectDayForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(PerfectDayForm, self).__init__(*args, **kwargs)
        self.fields['pref_hours_per_day'] =\
            forms.IntegerField(label=_("Ideally"),
                               min_value=1,
                               max_value=9,
                               required=False,
                               initial=4)
        self.fields['max_hours_per_day'] = \
            forms.IntegerField(label=_("Maximum"),
                               min_value=1,
                               max_value=9,
                               required=False,
                               initial=6)


class ModuleDescriptionForm(forms.ModelForm):

    def __init__(self, module, dept, *args, **kwargs):
        # first call parent's constructor
        super(ModuleDescriptionForm, self).__init__(*args, **kwargs)
        m = Module.objects.get(train_prog__department=dept, abbrev=module)
        self.fields['description'].initial = m.description


    class Meta:
        model = Module
        fields = ['description']


class EnrichedLinkForm(forms.ModelForm):
    class Meta:
        model = EnrichedLink
        fields = '__all__'
