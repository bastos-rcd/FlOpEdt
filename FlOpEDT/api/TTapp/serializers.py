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

from collections import OrderedDict

from django.contrib.postgres.fields.array import ArrayField
from django.db import models
from rest_framework import serializers
from rest_framework.fields import Field
from rest_framework.serializers import ModelSerializer

import TTapp.TimetableConstraints.tutors_constraints as ttt
import TTapp.TimetableConstraints.visio_constraints as ttv
from base.models import Department
from TTapp.flop_constraint import FlopConstraint


def serializer_factory(mdl: models.Model, fields=None, **kwargss):
    """
    Taken and adapted from Sebastian Wozny at https://stackoverflow.com/a/33137535

    Generalized serializer factory to increase DRYness of code.

    :param mdl: The model class that should be instanciated
    :param fields: the fields that should be exclusively present on the serializer
    :param kwargss: optional additional field specifications
    :return: An awesome serializer
    """

    def _get_declared_fields(attrs):
        declared_fields = [
            (field_name, attrs.pop(field_name))
            for field_name, obj in list(attrs.items())
            if isinstance(obj, Field)
        ]
        declared_fields.sort(key=lambda x: x[1]._creation_counter)
        return OrderedDict(declared_fields)

    # Create an object that will look like a base serializer
    class Base(object):
        pass

    Base._declared_fields = _get_declared_fields(kwargss)

    class MySerializer(Base, ModelSerializer):
        class Meta:
            model = mdl

        meta_fields = []
        if fields:
            meta_fields = fields
        setattr(Meta, "fields", meta_fields)

        def to_internal_value(self, data):
            formatted_data = {}
            # Replace department string by its id (i.e 'INFO' by 2)
            data["department"] = Department.objects.get(abbrev=data["department"]).id

            meta_fields = getattr(self.Meta, "fields")
            for field in meta_fields:
                if field in data:
                    formatted_data[field] = data[field]
            parameters = data["parameters"]
            for parameter in parameters:
                if "id_list" in parameter:
                    # Handle single value parameters
                    if not parameter["multiple"]:
                        if not parameter["id_list"]:
                            value = None
                        else:
                            value = parameter["id_list"][0]
                    else:
                        value = parameter["id_list"]
                    formatted_data[parameter["name"]] = value

            return super().to_internal_value(formatted_data)

    return MySerializer


def flopconstraint_serializer_factory(mdl: models.Model):
    fields = [field.name for field in mdl._meta.get_fields()]
    myserializer = serializer_factory(mdl, fields=fields)
    return myserializer


class FlopConstraintSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    parameters = serializers.SerializerMethodField()

    class Meta:
        abstract = True
        model = FlopConstraint
        fields = "__all__"

    def get_name(self, obj):
        return obj.__class__.__name__

    def get_periods(self, obj):
        periodlist = []
        periods = getattr(obj, "periods").values("name")

        for i in periods:
            periodlist.append(i)

        return periodlist

    def get_parameters(self, obj):
        paramlist = []

        fields = self.Meta.fields

        for field in obj._meta.get_fields():
            if field.name not in fields:
                parameters = {}
                id_list = []
                multiple = False

                if not field.many_to_one and not field.many_to_many:
                    typename = type(field).__name__

                    if type(field) == ArrayField:
                        multiple = True
                        typename = type(field.base_field).__name__
                        # Remplace la liste vide par la liste des valeurs
                        attr = getattr(obj, field.name)
                        if "start_time" in field.name:
                            id_list = list(st.strftime("%H:%M") for st in attr)
                        else:
                            id_list = attr

                    else:
                        # Insère la valeur de l'attribut unitaire
                        attr = getattr(obj, field.name)
                        id_list = [attr]

                else:
                    # Récupère le modele en relation avec un ManyToManyField ou un ForeignKey
                    mod = field.related_model
                    typenamesplit = str(mod)[8:-2].split(".")
                    typename = typenamesplit[0] + "." + typenamesplit[2]
                    attr = getattr(obj, field.name)

                    if field.many_to_one:
                        if str(attr) != "None":
                            id_list.append(attr.id)

                    if field.many_to_many:
                        multiple = True
                        listattr = attr.values("id")
                        for id in listattr:
                            id_list.append(id["id"])

                parameters["name"] = field.name
                parameters["type"] = typename
                parameters["required"] = not field.blank
                parameters["multiple"] = multiple
                parameters["id_list"] = id_list

                paramlist.append(parameters)

        return paramlist


class FlopConstraintTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    local_name = serializers.CharField()
    parameters = serializers.SerializerMethodField()

    def get_parameters(self, obj):
        fields = []
        for field in obj["parameters"]:
            multiple = False
            if not (field.many_to_one or field.many_to_many):
                typename = type(field).__name__

                if isinstance(field, ArrayField):
                    multiple = True
                    typename = type(field.base_field).__name__
            else:
                mod = field.related_model
                typenamesplit = str(mod)[8:-2].split(".")
                typename = typenamesplit[0] + "." + typenamesplit[2]
                if field.many_to_many:
                    multiple = True
            fields.append(
                {
                    "name": field.name,
                    "type": typename,
                    "multiple": multiple,
                    "required": not field.blank,
                }
            )
        return fields


class TimetableConstraintSerializer(FlopConstraintSerializer):
    class Meta:
        model = ttt.MinTutorsHalfDays
        fields = [
            "id",
            "title",
            "name",
            "weight",
            "is_active",
            "comment",
            "modified_at",
            "parameters",
        ]


class NoVisioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ttv.NoVisio
        fields = "__all__"


class FlopConstraintFieldSerializer(serializers.Serializer):
    name = serializers.CharField()
    type = serializers.CharField()
    acceptable = serializers.ListField(child=serializers.CharField())
