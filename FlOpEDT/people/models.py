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
from django.contrib.auth.models import AbstractUser
from base.models import Department
from base.timing import Day
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    rights = models.PositiveSmallIntegerField(verbose_name="Droits particuliers",
                                              default=0)
    departments = models.ManyToManyField(
        Department, through='UserDepartmentSettings')

    # 0b azmyx en binaire
    # x==1 <=> quand "modifier Cours" coché, les cours sont colorés
    #          avec la dispo du prof
    # y==1 <=> je peux changer les dispos de tout le monde
    # m==1 <=> je peux modifier l'emploi du temps comme bon me semble
    # FUTUR
    # z==1 <=> je peux changer les dispos des vacataires d'un module dont
    #          je suis responsable
    # a==1 <=> je peux surpasser les contraintes lors de la modification
    #          de cours

    def has_department_perm(self, department, admin=False):
        """
        Does the user have access to a specific department

        admin=True    Check if the user can access to the
                      department admin
        """
        if self.is_superuser:
            return True

        return (self.is_tutor
                and department in self.departments.all()
                and (not admin
                     or
                     UserDepartmentSettings.objects \
                     .get(user=self,
                          department=department) \
                     .is_admin
                     )
                )

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_staff

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return self.is_staff

    def uni_extended(self):
        ret = self.username + '<'
        if self.is_student:
            ret += 'S'
        if self.is_tutor:
            ret += 'T'
        ret += '>'
        ret += '(' + str(self.rights) + ')'
        return ret

    ###
    #   #Allows to get the user's preferred theme in the "base.html" file
    ###
    @property
    def get_theme(self):
        return self.themes_preference.theme

    class Meta:
        ordering = ['username', ]


class UserDepartmentSettings(models.Model):
    """
    This model allows to add additionnal settings to the
    relation between User and Department
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    is_main = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return (f'U:{self.user.username}, D:{self.department.abbrev}, {"main" if self.is_main else "secondary"}, '
                f'{"admin" if self.is_admin else "regular"}')


class Tutor(User):
    FULL_STAFF = 'fs'
    SUPP_STAFF = 'ss'
    BIATOS = 'bi'
    TUTOR_CHOICES = ((FULL_STAFF, "Full staff"),
                     (SUPP_STAFF, "Supply staff"),
                     (BIATOS, "BIATOS"))
    status = models.CharField(max_length=2,
                              choices=TUTOR_CHOICES,
                              verbose_name="Status",
                              default=FULL_STAFF)

    def uni_extended(self):
        ret = super(Tutor, self).uni_extended()
        ret += '-' + self.status
        return ret

    class Meta:
        verbose_name = 'Tutor'

    def save(self, *args, **kwargs):
        self.is_tutor = True
        super(Tutor, self).save(*args, **kwargs)


class FullStaff(Tutor):
    is_iut = models.BooleanField(default=True)

    def uni_extended(self):
        ret = super(FullStaff, self).uni_extended()
        if not self.is_iut:
            ret += '-n'
        ret += '-IUT'
        return ret

    class Meta:
        verbose_name = 'FullStaff'


class SupplyStaff(Tutor):
    employer = models.CharField(max_length=50,
                                verbose_name="Employeur ?",
                                default=None, null=True, blank=True)
    position = models.CharField(max_length=50,
                                default=None, null=True, blank=True)
    field = models.CharField(max_length=50,
                             verbose_name="Domaine ?",
                             default=None, null=True, blank=True)

    def uni_extended(self):
        ret = super(SupplyStaff, self).uni_extended()
        ret += '-Emp:' + self.employer + '-'
        ret += '-Pos:' + self.position + '-'
        ret += '-Dom:' + self.field
        return ret

    class Meta:
        verbose_name = 'SupplyStaff'


class BIATOS(Tutor):
    def uni_extended(self):
        return super(BIATOS, self).uni_extended()

    class Meta:
        verbose_name = 'BIATOS'


class TutorPreference(models.Model):
    tutor = models.OneToOneField('Tutor',
                                 on_delete=models.CASCADE,
                                 related_name='preferences')
    pref_hours_per_day = models.PositiveSmallIntegerField(
        verbose_name="How many hours per day would you prefer ?",
        default=4)
    max_hours_per_day = models.PositiveSmallIntegerField(
        verbose_name="How many hours per day can you suffer ?",
        default=9)
    min_hours_per_day = models.PositiveSmallIntegerField(
        verbose_name="Under how many hours would you prefer to avoid to have class?",
        default=0)

    def __str__(self):
        ret = f"{self.tutor} - P{self.pref_hours_per_day} - M{self.pref_hours_per_day} - m{self.min_hours_per_day}"
        return ret


# --- Notes sur Prof ---
#    MinDemiJournees=models.BooleanField(
#       verbose_name="Min Demi-journées?", default=False)
#    unparjour=models.BooleanField(verbose_name="Un créneau par jour?",
#                                  default=False)
# # (biatos | vacataire) => TPeqTD=false (donc 3h TP <=> 2h TD)
# # 1h CM <=> 1.5h TD
# TPeqTD = models.BooleanField()self.periode


class Student(User):  # for now: representative
    generic_groups = models.ManyToManyField('base.GenericGroup',
                                            blank=True)

    def __str__(self):
        return str(self.username)

    def __repr__(self):
        return str(self.username) + ' (G:' + ', '.join([group.name for group in self.generic_groups.all()]) + ')'

    class Meta:
        verbose_name = 'Student'


class Preferences(models.Model):
    morning_weight = models.DecimalField(
        default=.5, blank=True, max_digits=3, decimal_places=2)
    free_half_day_weight = models.DecimalField(
        default=.5, blank=True, max_digits=3, decimal_places=2)
    hole_weight = models.DecimalField(
        default=.5, blank=True, max_digits=3, decimal_places=2)
    eat_weight = models.DecimalField(
        default=.5, blank=True, max_digits=3, decimal_places=2)

    def get_morning_weight(self):
        return float(self.morning_weight)

    def get_evening_weight(self):
        return float(1 - self.morning_weight)

    def get_free_half_day_weight(self):
        return float(self.free_half_day_weight)

    def get_light_day_weight(self):
        return float(1 - self.free_half_day_weight)

    class Meta:
        abstract = True


class StudentPreferences(Preferences):
    student = models.OneToOneField('people.Student',
                                   related_name='preferences',
                                   on_delete=models.CASCADE)


class GroupPreferences(Preferences):
    group = models.OneToOneField('base.StructuralGroup',
                                 related_name='preferences',
                                 on_delete=models.CASCADE)

    def calculate_fields(self):
        # To pull students from the group
        students_preferences = StudentPreferences.objects.filter(student__generic_groups=self.group)

        # To initialise variables and getting the divider to get the average
        local_morning_weight = 0
        local_free_half_day_weight = 0
        local_hole_weight = 0
        local_eat_weight = 0
        nb_student_prefs = len(students_preferences)
        if nb_student_prefs == 0:
            self.morning_weight = 0.5
            self.free_half_day_weight = 0.5
            self.hole_weight = 0.5
            self.eat_weight = 0.5
        else:
            # To range the table
            for student_pref in students_preferences:
                local_morning_weight += student_pref.morning_weight
                local_free_half_day_weight += student_pref.free_half_day_weight
                local_hole_weight += student_pref.hole_weight
                local_eat_weight += student_pref.eat_weight
            # To calculate the average of each attributs
            self.morning_weight = local_morning_weight / nb_student_prefs
            self.free_half_day_weight = local_free_half_day_weight / nb_student_prefs
            self.hole_weight = local_hole_weight / nb_student_prefs
            self.eat_weight = local_eat_weight / nb_student_prefs
            self.save()


class NotificationsPreferences(models.Model):
    user = models.OneToOneField('User',
                                on_delete=models.CASCADE,
                                related_name='notifications_preference')
    nb_of_notified_weeks = models.PositiveSmallIntegerField(default=0)

###
# Save the user's preferred theme in the data base
###
class ThemesPreferences(models.Model):
    user = models.OneToOneField('User',
                                on_delete=models.CASCADE,
                                related_name='themes_preference')
    theme = models.CharField(max_length=50, default='White')

class UserPreferredLinks(models.Model):
    user = models.OneToOneField('User',
                                on_delete=models.CASCADE,
                                related_name='preferred_links')
    links = models.ManyToManyField('base.EnrichedLink',
                                   related_name='user_set')

    def __str__(self):
        return self.user.username + ' : ' + \
               ' ; '.join([str(l) for l in self.links.all()])


class PhysicalPresence(models.Model):
    user = models.ForeignKey('people.User', on_delete=models.CASCADE, related_name='physical_presences')
    day = models.CharField(max_length=2, choices=Day.CHOICES, default=Day.MONDAY)
    week = models.ForeignKey('base.Week', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} is present {self.day} of week {self.week}"