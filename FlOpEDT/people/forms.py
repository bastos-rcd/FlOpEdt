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
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.db import transaction

from base.models import StructuralGroup

from .models import BIATOS, FullStaff, Student, SupplyStaff, Tutor, User


class GroupChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.full_name

class AddStudentForm(UserCreationForm):
    gps = GroupChoiceField(
        queryset=StructuralGroup.objects.filter(basic=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text='Les groupes auquels vous appartenez'
    )

    class Meta(UserCreationForm.Meta):
        model = Student

    @transaction.atomic
    def save(self):
        student = super(AddStudentForm, self).save(commit=False)
        student.is_student = True
        student.save()
        student.generic_groups.add(*self.cleaned_data.get('gps'))
        # save_m2m is automatically called
        return student


class ChangeStudentForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Student


class ChangeFullStaffTutorForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = FullStaff


class ChangeSupplyStaffTutorForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = SupplyStaff

class ChangeBIATOSTutorForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = BIATOS



class AddFullStaffTutorForm(UserCreationForm):
    pref_slots_per_day = forms.IntegerField(required=False,
                                            help_text='Nombre de créneaux préférés par jour')
    is_iut = forms.BooleanField()

    class Meta(UserCreationForm.Meta):
        model = FullStaff
        fields = ('email', 'username', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(AddFullStaffTutorForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
            
    @transaction.atomic
    def save(self):
        fs = super(AddFullStaffTutorForm, self).save(commit=False)
        data = self.cleaned_data
        fs.is_tutor = True
        fs.status = Tutor.FULL_STAFF
        fs.pref_slots_per_day = data.get('pref_slots_per_day')
        fs.is_iut = data.get('is_iut')
        fs.save()
        return fs

    
class AddSupplyStaffTutorForm(UserCreationForm):
    employer = forms.CharField(max_length=50, help_text='Employeur')
    position = forms.CharField(max_length=50,
                               help_text='Qualité')
    field = forms.CharField(max_length=50,
                             help_text="Domaine")

    class Meta(UserCreationForm.Meta):
        model = SupplyStaff
        fields = ('email', 'username', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(AddSupplyStaffTutorForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
            
    @transaction.atomic
    def save(self):
        sus = super(AddSupplyStaffTutorForm, self).save(commit=False)
        data = self.cleaned_data
        sus.is_tutor = True
        sus.status = Tutor.SUPP_STAFF
        sus.employer = data.get('employer')
        sus.position = data.get('position')
        sus.field = data.get('field')
        sus.save()
        return sus

    
class AddBIATOSTutorForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = BIATOS
        fields = ('email', 'username', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(AddBIATOSTutorForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
            
    @transaction.atomic
    def save(self):
        bi = super(AddBIATOSTutorForm, self).save(commit=False)
        bi.is_tutor = True
        bi.status = Tutor.BIATOS
        bi.save()
        return bi

    

