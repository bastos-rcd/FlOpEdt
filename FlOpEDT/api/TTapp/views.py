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

import json
import os
import pkgutil
import re
from pathlib import Path

from django.apps import apps
from django.conf import settings as ds
from django.contrib.postgres.fields.array import ArrayField
from django.http import FileResponse, HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.exceptions import APIException
from rest_framework.response import Response

import TTapp.TimetableConstraints.visio_constraints as ttv
from api.permissions import IsAdminOrReadOnly
from api.shared.params import dept_param, week_param, year_param
from api.TTapp import serializers
from base.models import Department
from base.timing import Day, all_possible_start_times
from base.weeks import current_year
from MyFlOp.colors import Tcolors
from TTapp.FlopConstraint import FlopConstraint, all_subclasses

DOC_DIR = os.path.join(
    os.path.dirname(pkgutil.get_loader("TTapp").get_filename()),
    "TimetableConstraints/doc",
)
IMG_DIR = os.path.join(
    os.path.dirname(pkgutil.get_loader("TTapp").get_filename()),
    "TimetableConstraints/doc/images",
)
CORRUPTED_JSON_PATH = os.path.join(ds.TMP_DIRECTORY, "discarded.json")
EN_DIR_NAME = "en"
REGEX_IMAGE = r"(?:[!]\[(.*?)\])\(((\.\.)(.*?))\)"
# ---------------
# ---- TTAPP ----
# ---------------
""" 

class TTCustomConstraintsViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the TTCustomConstraints.

    Can be filtered as wanted with every field of a CustomContraint object.
    
    queryset = ttm.CustomConstraint.objects.all()
    serializer_class = serializers.TTCustomConstraintsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTLimitCourseTypeTimePerPeriodsViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the LimitCourseTypeTimePerPeriods.

    Can be filtered as wanted with every field of a LimitCourseTypeTimePerPeriods object.
    
    queryset = ttm.LimitCourseTypeTimePerPeriod.objects.all()
    serializer_class = serializers.TTLimitCourseTypeTimePerPeriodsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTReasonableDaysViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the ReasonableDays.

    Can be filtered as wanted with every field of a ReasonableDay object.
    
    queryset = ttm.ReasonableDays.objects.all()
    serializer_class = serializers.TTReasonableDayssSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTStabilizeFilter(filters.FilterSet):
    
    Custom filter for ArrayField fixed_days
    
    fixed_days = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ttm.Stabilize
        fields = ('group', 'module', 'tutor', 'fixed_days')


class TTStabilizeViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the Stabilize objects from TTapp.

    Can be filtered as wanted with "fixed_days"
    of a Stabilize object by calling the function TTStabilizeFilter
    
    queryset = ttm.Stabilize.objects.all()
    serializer_class = serializers.TTStabilizeSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_class = TTStabilizeFilter


class TTMinHalfDaysViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the MinHalfDays.

    Can be filtered as wanted with every field of a MinHalfDay object.
    
    queryset = ttm.MinHalfDays.objects.all()
    serializer_class = serializers.TTMinHalfDaysSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTMinNonPreferedSlotsViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the MinNonPreferedSlots.

    Can be filtered as wanted with every field of a MinNonPreferedSlots object.
    
    queryset = ttm.MinNonPreferedSlot.objects.all()
    serializer_class = serializers.TTMinNonPreferedSlotsSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTAvoidBothTimesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the AvoidBothTimesSameDay.

    Can be filtered as wanted with every field of a AvoidBothTime object.
    
    queryset = ttm.AvoidBothTimesSameDay.objects.all()
    serializer_class = serializers.TTAvoidBothTimesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTSimultaneousCoursesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the SimultaneousCourses.

    Can be filtered as wanted with every field of a SimultaneousCourse object.
    
    queryset = ttm.SimultaneousCourses.objects.all()
    serializer_class = serializers.TTSimultaneousCoursesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'


class TTLimitedFilter(filters.FilterSet):
    
    Custom filter for ArrayField possible_start_times
    
    possible_start_times = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = ttm.LimitedStartTimeChoices
        fields = ('module', 'tutor', 'group', 'type', 'possible_start_times')


class TTLimitedStartTimeChoicesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the LimitedStartTimeChoices.

    Can be filtered as wanted with "possible_start_times"
    of a LimitedStartChoices object by calling the function TTLimitedFilter
    
    queryset = ttm.LimitedStartTimeChoices.objects.all()
    serializer_class = serializers.TTLimitedStartTimeChoicesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_class = TTLimitedFilter


class TTLimitedRoomChoicesViewSet(viewsets.ModelViewSet):
    
    ViewSet to see all the LimitedRoomChoices.

    Can be filtered as wanted with every field of a LimitedRoomChoice object.
    
    queryset = ttm.LimitedRoomChoices.objects.all()
    serializer_class = serializers.TTLimitedRoomChoicesSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = '__all__'
 """


class FlopConstraintListViewSet(viewsets.ViewSet):
    """
    ViewSet to see all the constraints and their parameters

    Result can be filtered by week, year and dept
    """

    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = "__all__"

    @extend_schema(parameters=[week_param(), year_param(), dept_param()])
    def list(self, request, **kwargs):
        # Getting all the filters
        week = self.request.query_params.get("week", None)
        year = self.request.query_params.get("year", None)
        dept = self.request.query_params.get("dept", None)
        data = list()
        constraintlist = all_subclasses(FlopConstraint)

        for constraint in constraintlist:
            if constraint._meta.abstract == False:
                queryset = constraint.objects.all().select_related("department")

                if week is not None:
                    queryset = queryset.filter(weeks__nb=week)

                if year is not None:
                    queryset = queryset.filter(weeks__year=year)

                if dept is not None:
                    queryset = queryset.filter(department__abbrev=dept)

                for object in queryset:
                    serializer = serializers.TimetableConstraintSerializer(object)
                    data.append(serializer.data)

        return Response(data)


class FlopConstraintViewSet(viewsets.ViewSet):
    """
    ViewSet to see all the constraints and their parameters

    Result can be filtered by week, year and dept
    """

    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = "__all__"
    lookup_field = "id"
    lookup_value_regex = "[0-9]{1,32}"

    @extend_schema(parameters=[week_param(), year_param(), dept_param()])
    def list(self, request, **kwargs):
        name = kwargs["name"]
        # Getting all the filters
        week = self.request.query_params.get("week", None)
        year = self.request.query_params.get("year", None)
        dept = self.request.query_params.get("dept", None)
        data = list()

        constraint = apps.get_model("TTapp", name)
        if constraint._meta.abstract == False:
            queryset = constraint.objects.all().select_related("department")

            if week is not None:
                queryset = queryset.filter(weeks__nb=week)

            if year is not None:
                queryset = queryset.filter(weeks__year=year)

            if dept is not None:
                queryset = queryset.filter(department__abbrev=dept)

            for object in queryset:
                serializer = serializers.TimetableConstraintSerializer(object)
                data.append(serializer.data)
        return Response(data)

    @extend_schema(parameters=[week_param(), year_param(), dept_param()])
    def retrieve(self, request, name, id):
        # name = request.query_params.get('name', None)
        # Obtenir la contrainte à partir du nom
        constraint = apps.get_model("TTapp", name)

        instance = constraint.objects.get(pk=id)
        serializer = serializers.TimetableConstraintSerializer(instance)

        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        model = apps.get_model("TTapp", request.data["name"])
        serializer = serializers.flopconstraint_serializer_factory(model)(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def update(self, request, name, id):
        response = "{{'message': '{}'}}"

        try:
            model = apps.get_model("TTapp", name)
        except LookupError:
            return Response(response.format("Given constraint name does not exist"))
        try:
            instance = model.objects.get(id=id)
        except:
            return Response(
                response.format(f"Could not find constraint {name} with id {id}")
            )
        serializer = serializers.flopconstraint_serializer_factory(model)(
            instance, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, name, id):
        response = "{{'message': '{}'}}"

        try:
            model = apps.get_model("TTapp", name)
        except LookupError:
            return Response(response.format("Given constraint name does not exist"))
        try:
            instance = model.objects.get(id=id)
        except:
            return Response(
                response.format(f"Could not find constraint {name} with id {id}")
            )
        instance.delete()
        return Response(response.format("Deleted successfully"))


class FlopConstraintTypeViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request):
        classes = []
        excluded_fields = {
            "id",
            "class_name",
            "department",
            "weight",
            "title",
            "comment",
            "is_active",
            "modified_at",
            "courses",
        }

        for constraint_class in all_subclasses(FlopConstraint):
            fields = constraint_class._meta.get_fields()

            parameters_fields = set(
                [f for f in fields if f.name not in excluded_fields]
            )
            classes.append(
                {
                    "name": constraint_class.__name__,
                    "local_name": constraint_class._meta.verbose_name,
                    "parameters": parameters_fields,
                }
            )

        serializer = serializers.FlopConstraintTypeSerializer(classes, many=True)
        return Response(serializer.data)


class NoVisioViewSet(viewsets.ModelViewSet):
    queryset = ttv.NoVisio.objects.all()
    serializer_class = serializers.NoVisioSerializer
    permission_classes = [IsAdminOrReadOnly]


class FlopConstraintFieldViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(parameters=[dept_param(required=True)])
    def list(self, request):
        dept = self.request.query_params.get("dept", None)
        if dept is None:
            raise APIException(detail="Department not provided")
        try:
            department = Department.objects.get(abbrev=dept)
        except Department.DoesNotExist:
            raise APIException(detail="Unknown department")
        flop_constraints_fields = set()
        # exclude useless fields
        excluded_fields = {
            "id",
            "class_name",
            "department",
            "weight",
            "title",
            "comment",
            "is_active",
            "modified_at",
            "courses",
        }

        for constraint_class in all_subclasses(FlopConstraint):
            fields = constraint_class._meta.get_fields()
            # Exclude already considered fields
            excluded_fields |= set(f.name for f in flop_constraints_fields)
            parameters_fields = set(
                [f for f in fields if f.name not in excluded_fields]
            )
            flop_constraints_fields |= parameters_fields

        fields_list = list(flop_constraints_fields)
        """
        [<django.db.models.fields.PositiveSmallIntegerField: time2>, <django.db.models.fields.PositiveSmallIntegerField: nb_max>, 
        <django.db.models.fields.PositiveSmallIntegerField: nb_min>, <django.db.models.fields.BooleanField: join2courses>, 
        <django.db.models.fields.PositiveSmallIntegerField: slot_start_time>, <django.db.models.fields.PositiveSmallIntegerField: curfew_time>, 
        <django.db.models.fields.related.ManyToManyField: weeks>, <django.db.models.fields.PositiveSmallIntegerField: slot_end_time>, 
        <django.db.models.fields.PositiveSmallIntegerField: max_number>, <django.db.models.fields.PositiveSmallIntegerField: max_holes_per_day>, 
        <django.db.models.fields.PositiveSmallIntegerField: max_holes_per_week>, <django.db.models.fields.PositiveSmallIntegerField: limit>, 
        <django.db.models.fields.PositiveSmallIntegerField: min_time_per_period>, <django.db.models.fields.PositiveSmallIntegerField: max_time_per_period>, 
        <django.db.models.fields.PositiveSmallIntegerField: tolerated_margin>, <django.db.models.fields.PositiveSmallIntegerField: max_hours>, 
        <django.db.models.fields.CharField: period>, <django.db.models.fields.PositiveSmallIntegerField: number_of_weeks>, 
        <django.db.models.fields.related.ManyToManyField: guide_tutors>, <django.db.models.fields.PositiveSmallIntegerField: min_days_nb>, 
        <django.db.models.fields.PositiveSmallIntegerField: lower_bound_hours>, <django.db.models.fields.PositiveSmallIntegerField: work_copy>, 
        <django.contrib.postgres.fields.array.ArrayField: fixed_days>, <django.db.models.fields.related.ManyToManyField: train_progs>, 
        <django.db.models.fields.related.ForeignKey: module>, <django.db.models.fields.related.ForeignKey: tutor>, 
        <django.db.models.fields.related.ForeignKey: group>, <django.db.models.fields.related.ForeignKey: course_type>, 
        <django.db.models.fields.related.ManyToManyField: possible_rooms>, <django.db.models.fields.PositiveSmallIntegerField: start_time>, 
        <django.db.models.fields.PositiveSmallIntegerField: end_time>, <django.db.models.fields.related.ManyToManyField: tutors>, 
        <django.db.models.fields.PositiveSmallIntegerField: lunch_length>, <django.db.models.fields.CharField: weekday>, 
        <django.db.models.fields.PositiveSmallIntegerField: min_break_length>, <django.db.models.fields.CharField: tutor_status>, 
        <django.contrib.postgres.fields.array.ArrayField: possible_week_days>, <django.contrib.postgres.fields.array.ArrayField: possible_start_times>,
         <django.contrib.postgres.fields.array.ArrayField: forbidden_week_days>, <django.contrib.postgres.fields.array.ArrayField: weekdays>, 
         <django.db.models.fields.related.ManyToManyField: groups>, <django.db.models.fields.related.ManyToManyField: course_types>, 
         <django.db.models.fields.related.ManyToManyField: modules>, <django.contrib.postgres.fields.array.ArrayField: forbidden_start_times>, 
         <django.db.models.fields.BooleanField: pre_assigned_only>, 
        <django.db.models.fields.PositiveSmallIntegerField: percentage>, <django.db.models.fields.PositiveSmallIntegerField: time1>]"""

        for field in fields_list:
            acceptable = []
            if not field.many_to_one and not field.many_to_many:
                typename = type(field).__name__

                # Récupère les validators dans acceptable
                if typename == "BooleanField":
                    acceptable = [True, False]

                elif typename == "CharField":
                    choices = field.choices
                    if choices is not None:
                        if "day" in field.name:
                            acceptable_days = department.timegeneralsettings.days
                            acceptable = [
                                choice[0]
                                for choice in Day.CHOICES
                                if choice[0] in acceptable_days
                            ]
                        else:
                            acceptable = [c[0] for c in choices]

                elif typename == "TimeField":
                    acceptable = all_possible_start_times(department)

                elif type(field) is ArrayField:
                    typename = type(field.base_field).__name__
                    # Récupère les choices de l'arrayfield dans acceptable
                    choices = field.base_field.choices
                    # Si c'est des timme, on récupère les start times possibles
                    if "time" in field.name:
                        acceptable = all_possible_start_times(department)
                    elif "day" in field.name:
                        acceptable_days = department.timegeneralsettings.days
                        acceptable = [
                            choice[0]
                            for choice in Day.CHOICES
                            if choice[0] in acceptable_days
                        ]
                    elif choices is not None:
                        acceptable = [c[0] for c in choices]

            else:
                # Récupère le modele en relation avec un ManyToManyField ou un ForeignKey
                mod = field.related_model
                typenamesplit = str(mod)[8:-2].split(".")
                typename = typenamesplit[0] + "." + typenamesplit[2]
                acceptablelist = mod.objects.values("id")

                # Filtre les ID dans acceptable list en fonction du department
                if field.name in [
                    "tutor",
                    "tutors",
                    "room",
                    "rooms",
                    "possible_rooms",
                    "guide_tutors",
                ]:
                    acceptablelist = acceptablelist.filter(departments=department)

                elif field.name in [
                    "train_progs",
                    "course_type",
                    "course_types",
                    "room_type",
                    "room_types",
                ]:
                    acceptablelist = acceptablelist.filter(department=department)

                elif field.name in ["modules", "module", "groups", "group"]:
                    acceptablelist = acceptablelist.filter(
                        train_prog__department=department
                    )

                # Accept only periods that are in the current year, and on the week mode
                # FIXME accept other modes!
                elif field.name == "periods":
                    acceptablelist = acceptablelist.filter(
                        mode="w", start_date__year__in=[current_year, current_year + 1]
                    )

                for element in acceptablelist:
                    acceptable.append(element["id"])

            field.type = typename
            field.acceptable = acceptable
        serializer = serializers.FlopConstraintFieldSerializer(fields_list, many=True)
        return Response(serializer.data)


class CustomUrl:
    # Class to better handle url
    def __init__(self, request):
        self.domain = request.get_host()
        self.protocol = request.scheme
        self.full_domain = self.protocol + "://" + self.domain
        self.splited_path = request.path.split("/")
        self.lang = self.splited_path[1]


class FlopDocVisu(viewsets.ViewSet):
    def list(self, request, **kwargs):
        name = kwargs["name"]
        name_no_extensions = name.split(".")[0]
        url = CustomUrl(request)
        dir_lang = os.path.join(DOC_DIR, url.lang)

        # Try to check if file is not in the forbidden file
        try:
            data = json.load(open(CORRUPTED_JSON_PATH))
        except:
            return HttpResponse(status=500)
        forbidden_files = data["discarded"]

        if name in forbidden_files:
            print(
                f"{Tcolors.FAIL}{Tcolors.BOLD}Attempt to access forbidden file : {name}{Tcolors.ENDC}"
            )
            return HttpResponse(status=404)

        # if doc not found in language will try to find it in english
        if url.lang != EN_DIR_NAME:
            f_path = recursive_search(dir_lang, name)
            if len(f_path) == 0:
                dir_lang = os.path.join(DOC_DIR, EN_DIR_NAME)
                f_path = recursive_search(dir_lang, name)
                if len(f_path) == 0:
                    return HttpResponse(status=404)
        # english doc
        else:
            f_path = recursive_search(dir_lang, name)
            if len(f_path) == 0:
                return HttpResponse(status=404)

        # will replace image path and interpolate file
        # return json_file containing text and map
        json_file = check_file(f_path, url, name_no_extensions)

        return HttpResponse(json_file, content_type="application/json; charset=utf-8")

    def create(self, request, **kwargs):
        return HttpResponse(status=403)

    def update(self, request, **kwargs):
        return HttpResponse(status=403)

    def destroy(self, request, **kwargs):
        return HttpResponse(status=403)


class FlopImgVisu(viewsets.ViewSet):
    # Work the same as FlopDocVisu
    def list(self, request, **kwargs):
        name = kwargs["name"]
        f_path = recursive_search(IMG_DIR, name)
        if len(f_path) == 0:
            return HttpResponse(status=404)
        file_handle = open(f_path, "rb")
        return FileResponse(file_handle)

    def create(self, request, **kwargs):
        return HttpResponse(status=403)

    def update(self, request, **kwargs):
        return HttpResponse(status=403)

    def destroy(self, request, **kwargs):
        return HttpResponse(status=403)


#################################################


def recursive_search(path, filename):
    liste = list(Path(path).rglob(filename))
    if len(liste) == 0:
        return []
    else:
        return str(liste[0])


def check_file(path, url, name):
    name = name + ".json"
    json_path = None
    found = True

    temp_path = os.path.join(ds.TMP_DIRECTORY, url.lang)
    file_temp_path = os.path.join(temp_path, name)

    # Create the temp subdirectory if it doesn't exists
    if not os.path.isdir(temp_path):
        os.makedirs(temp_path)

    # test if cached file exist
    try:
        json_path = open(file_temp_path)
    except:
        found = False

    if found:
        # if cached file exist we return it
        json_file = json.load(json_path)
        print(f"{Tcolors.OKGREEN}Opened cached file{Tcolors.ENDC}")
        return json.dumps(json_file)
    else:
        # create json and attempt to write it in cache
        file_handle = open(path, "r")
        text = image_interpolation(file_handle, url.full_domain)
        text, dico_inter = doc_interpolation(text)

        full_dico = {"text": text, "inter": dico_inter}
        json_file = json.dumps(full_dico)
        try:
            json_path = open(file_temp_path, "x")
            json_path.write(json_file)
        except:
            print(
                f"{Tcolors.FAIL}{Tcolors.BOLD}CAN'T WRITE FILE INTO TEMP, BAD PERFORMANCE EXPECTED{Tcolors.ENDC}"
            )
            return json_file

        print(f"{Tcolors.OKGREEN}Created json file {name} {Tcolors.ENDC}")
        return json_file


def image_interpolation(file, domain):
    text = file.read()
    # use 4th group (image name, identified by r\4) from regex image and add the domain
    image_path = domain + "/fr/api/ttapp" + r"\4"
    full_link = "![" + r"\1" + "](" + image_path + ")"  # rebuild

    replaced = re.sub(REGEX_IMAGE, full_link, text)
    return replaced


def doc_interpolation(docu):
    # will replace in the doc every {{xx}} with <span id=xxDisplayer>...
    reg = r"({{(.*?)}})"

    pattern = re.compile(reg)
    paramCallCount = {}
    newstring = ""
    start = 0
    for m in re.finditer(pattern, docu):
        ###
        end, newstart = m.span()
        newstring += docu[start:end]
        ###

        name = m.group(2).strip()
        if paramCallCount.get(name) == None:
            paramCallCount[name] = 0

        paramCallCount[name] = paramCallCount.get(name) + 1
        rep = (
            '<span id="'
            + name
            + "Displayer"
            + str(paramCallCount.get(name))
            + '"></span>'
        )

        ###
        newstring += rep
        start = newstart
        ###

    newstring += docu[start:]
    return (newstring, paramCallCount)
