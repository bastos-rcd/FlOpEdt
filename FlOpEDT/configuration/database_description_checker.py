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


##############
# PRINCIPLE  #
##############
#
# This code finds the list of problems in a description of a database
# in the form of structured Python data.
#
# The goal is that if there's any problem with what the user entered,
# it is seen, it is precisely diagnosed and explained : no need to ask.
#
# Each problem should be a string describing the problem. It should
# start with "D:" if it's a developer problem, otherwise it should be
# a very direct and explicit indication of what was wrong.
#
# The checks go from the very basic (structural, typing) to the more
# specific, in turn, as the more specific requires some assumptions to
# be already satisfied.

##################
# DATA STRUCTURE #
##################
#
# The main object is a dictionary with keys:
#
# 'rooms': a set of strings, the room identifiers - the
# brick-and-mortar rooms
#
# 'room_groups': a dictionary where a key is a group identifier and
# the data is a set of brick-and-mortar room identifiers
#
# 'room_categories': a dictionary where a key is a category identifier
# and the data is a set of room identifiers (both brick-and-mortar and
# groups)
#
# 'people': a dictionary where a key is a person identifier, and the
# data is itself a dictionary with explicit key names, giving strings:
# 'first_name', 'last_name', 'email', 'status' and 'employer'.
#
# 'modules': a dictionary where a key is an identifier, and the data
# is itself a dictionary with explicit key names, giving strings:
# 'PPN', 'short', 'name', 'promotion', 'period' and 'responsable'.
#
# 'courses': a dictionary where a key is an identifier, and the data is
# itself a dictionary, 'duration' an integer, 'group_types' a set of
# strings consisting of the concerned group types identifiers, and
# 'start_times' a set of integers consisting of the possible start
# times.
#
# 'settings': a dictionary with keys:
#
#   - 'day_start_time', 'day_finish_time', 'lunch_break_start_time' and
#     'lunch_break_finish_time' : integers with explicit meaning
#
#   - 'default_preference_duration': integer with explicit meaning
#
#   - 'days': a list of strings among 'm', 'tu', 'w', 'th', 'f', 'sa'
#     and 'su' (fixme)
#
#   - 'periods': a dictionary where a key is a period identifier, and
#     the data is a pair of integers : the start week and finish week.
#
# 'promotions': a dictionary where a key is an identifier and the
# associated data is the name of the promotion.
#
# 'group_types': a set of group type identifiers
#
# 'groups': a dictionary where a key is a pair promotion
# identifier-group identifier, and the data is itself a dictionary
# with keys:
#
#   - 'group_type': a group type identifier
#
#   - 'parent': a set containing either a group identifier or nothing

################
# ORGANISATION #
################
# The basic organisation of the file is the following :
# - helper functions for first level checkers
# - first level checkers
# - <helpers and checkers of higher levels>
# - main checker

import operator

people_sheet = 'Intervenants'
rooms_sheet = 'Salles'
groups_sheet = 'Groupes'
modules_sheet = 'Modules'
courses_sheet = 'Cours'
settings_sheet = 'Paramètres'

##########################################
#                                        #
#          Helper functions              #
#                                        #
##########################################

def check_identifiers(ids, name):
    result = []
    found_issue1 = False
    found_issue2 = False
    found_issue3 = False
    for id_ in ids:
        if not found_issue1 and id_ == None:
            result.append(f"D: (at least) one of the {name} has a None identifier!")
            found_issue1 = True
        elif not found_issue2 and not isinstance(id_, str):
            result.append(f"D: (at least) one of the {name} has a non-string identifier!")
            found_issue2 = True
        elif not found_issue3 and id_ == '':
            result.append(f"D: (at least) one of the {name} has an empty identifier!")
            found_issue3 = True
    return result


def check_type(obj, type_, name):
    result = []
    if not isinstance(obj, type_):
        result.append(f"D: {name} isn't a '{type_.__name__}'")
    return result

##########################################
#                                        #
#          Low level checks              #
#                                        #
##########################################

def check_rooms(rooms):
    result = []
    if not isinstance(rooms, set):
        result.append("D: the rooms chunk should be a 'set'")
    else:
        result.extend(check_identifiers(rooms, "rooms"))
    return result


def check_room_groups(room_groups):
    result = []
    if not isinstance(room_groups, dict):
        result.append("D: the room_groups chunk should be a 'dict'")
    else:
        result.extend(check_identifiers(room_groups.keys(), "room groups"))
        for id_, rooms in room_groups.items():
            if isinstance(rooms, set):
                result.extend(check_identifiers(rooms, f"room identifier in room group '{id_}'"))
            else:
                result.extend(f"D: room group '{id_}' should be a set")
    return result

def check_room_categories(room_categories):
    result = []
    if not isinstance(room_categories, dict):
        result.append("D: the room categories chunk should be a 'dict'")
    else:
        result.extend(check_identifiers(room_categories.keys(), "room categories"))
        for id_, rooms in room_categories.items():
            if isinstance(rooms, set):
                result.extend(check_identifiers(rooms, f"room identifier in room category '{id_}'"))
            else:
                result.extend(f"D: room category '{id_}' should be a set")
    return result


def check_people(people):
    result = []
    if not isinstance(people, dict):
        result.append("D: the people chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(people.keys(), "people"))
    if len(result) > 0:
        return result
    for id_, person in people.items():
        if not isinstance(person, dict):
            result.append(f"D: person '{id_}' should be a 'dict'")
            continue
        if person.keys() != { 'first_name', 'last_name', 'email', 'status', 'employer' }:
            result.append(f"D: person '{id_}' doesn't have the expected keys")
            continue
    return result


def check_modules(modules):
    result = []
    if not isinstance(modules, dict):
        result.append("D: the modules chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(modules.keys(), "module"))
    if len(result) > 0:
        return result
    for id_, module in modules.items():
        if not isinstance(module, dict):
            result.append("D: module '{id_}' should be a 'dict'")
            continue
        if module.keys() != { 'short', 'PPN', 'name', 'promotion', 'period', 'responsable' }:
            result.append(f"D: module '{id_}' doesn't have the expected keys")
            continue
        for key, val in module.items():
            result.extend(check_type(val, str, f"field '{key}' of module '{id_}'"))
    return result


def check_cours(cours):
    result = []
    if not isinstance(cours, dict):
        result.append("D: the cours chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(cours.keys(), "cours"))
    if len(result) > 0:
        return result
    for id_, elem in cours.items():
        if not isinstance(elem, dict):
            result.append("D: cours '{id_}' should be a 'dict'")
            continue
        if elem.keys() != { 'duration', 'group_types', 'start_times' }:
            result.append(f"D: cours '{id_}' doesn't have the expected keys")
            continue
        result.extend(check_type(elem['duration'], int, f"duration of cours '{id_}'"))
        if isinstance(elem['group_types'], set):
            result.extend(check_identifiers(elem['group_types'],
                                            f"group types of cours {id_}"))
        else:
            result.append(f"D: group types of cours '{id_}' isn't a set")
        if isinstance(elem['start_times'], set):
            for time in elem['start_times']:
                result.extend(check_type(time, int, f"one of the start times of cours '{id_}'"))
        else:
            result.append(f"D: start times of cours '{id_}' isn't a 'set'")
    return result


def check_settings(settings):
    result = []
    if not isinstance(settings, dict):
        result.append("D: the settings chunk should be a 'dict'")
        return result
    if settings.keys() != { 'day_start_time', 'day_finish_time',
                            'lunch_break_start_time', 'lunch_break_finish_time',
                            'default_preference_duration', 'days', 'periods'}:
        result.append(f"D: settings doesn't have the expected keys")
        return result

    result.extend(check_type(settings['day_start_time'], int, "Day start time in settings"))
    result.extend(check_type(settings['day_finish_time'], int, "Day finish time in settings"))
    result.extend(check_type(settings['lunch_break_start_time'], int, "Lunch break start time in settings"))
    result.extend(check_type(settings['lunch_break_finish_time'], int, "Lunch break finish time in settings"))
    result.extend(check_type(settings['default_preference_duration'], int, "Default preference duration in settings"))
    if isinstance(settings['days'], list):
        if not set(settings['days']).issubset({'m', 'tu', 'w', 'th', 'f', 'sa', 'su'}):
            result.append("D: the days in settings contain invalid values")
    else:
        result.append("D: the days in settings should be a 'set'")

    if isinstance(settings['periods'], dict):
        for id_, val in settings['periods'].items():
            if isinstance(val, tuple) and len(val) == 2:
                result.extend(check_type(val[0], int, f"start week for period '{id_}' in settings"))
                result.extend(check_type(val[1], int, f"finish week for period '{id_}' in settings"))
            else:
                result.append(f"D: the data for period '{id_}' in settings should be a pair")
    else:
        result.append("D: the periods in settings should be a 'dict'")

    return result


def check_promotions(promotions):
    result = []
    if not isinstance(promotions, dict):
        result.append("D: the promotions chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(promotions.keys(), "promotions"))
    for id_, name in promotions.items():
        result.extend(check_type(name, str, f"name of promotion '{id_}'"))

    return result


def check_group_types(group_types):
    result = []
    if not isinstance(group_types, set):
        result.append("D: the group types chunk should be a 'set'")
        return result
    result.extend(check_identifiers(group_types, "group types"))
    return result


def check_structural_groups(groups):
    result = []
    if not isinstance(groups, dict):
        result.append("D: the groups chunk should be a 'dict'")
        return result
    result.extend(check_identifiers(map(lambda pair: pair[1], groups.keys()), "groups"))
    for (promotion, id_), group in groups.items():
        if isinstance(group, dict):
            if group.keys() != {'group_type', 'parent'}:
                result.append(f"D: group '{id_}' in promotion '{promotion}' doesn't have the expected keys")
            else:
                result.extend(check_type(promotion, str, f"promotion for group '{id_}'"))
                result.extend(check_type(group['group_type'], str, f"group type of group '{id_}'"))
                if isinstance(group['parent'], set):
                    if len(group['parent']) > 1:
                        result.append(f"D: group '{id_}' should have at most one parent")
                    elif len(group['parent']) == 1:
                        for parent in group['parent']: # how does one peek in a set?
                            result.extend(check_type(parent, str, f"parent of group '{id_}'"))
                else:
                    result.append(f"D: the parent of group '{id_}' isn't a set")
        else:
            result.append(f"Group '{id_}' in promotion '{promotion}' isn't a 'dict'")
    return result


def check_transversal_groups(transversal_groups):
    result = []
    if not isinstance(transversal_groups, dict):
        result.append("D: the transversal_groups chunk should be a 'dict'")
        return result
    return result
##########################################
#                                        #
#             Helper functions           #
#                                        #
##########################################

def check_duplicates(ids, name):
    result = []

    duplicates = set()
    for id_ in ids:
        if id_.startswith(':INVALID:'):
            _, _, reason, cell = id_.split(':')
            if reason == 'DUPLICATE':
                duplicates.add(cell)
            else:
                result.append(f"D: identifier in cell '{cell}' is invalid for unknown reason '{reason}'")
    if len(duplicates) > 0:
        result.append("Les identifiants de {0:s} dans ces cases sont des doublons : {1:s}".format(name,', '.join(duplicates)))

    return result

def check_non_overlapping_periods(periods):
    result = []

    periods.sort(key=operator.itemgetter(1))

    for ii in range(0, len(periods)):

        for jj in range(ii+1, len(periods)):

            if periods[jj][1] <= periods[ii][2]:
                result.append(f"Les périodes '{periods[ii][0]}' et '{periods[jj][0]}' se chevauchent dans '{settings_sheet}'")
    
    return result

##########################################
#                                        #
#         Higher level checks            #
#                                        #
##########################################

def check_settings_sheet(database):
    result = []

    #
    # check the time settings
    #
    day_start_time = database['settings']['day_start_time']
    day_finish_time = database['settings']['day_finish_time']
    lunch_break_start_time = database['settings']['lunch_break_start_time']
    lunch_break_finish_time = database['settings']['lunch_break_finish_time']

    if day_start_time < 0:
        result.append(f"L'heure de début de journée dans '{settings_sheet}' est invalide")
    elif day_finish_time < 0:
        result.append(f"L'heure de fin de journée dans '{settings_sheet}' est invalide")
    elif lunch_break_start_time < 0:
        result.append(f"L'heure de début de pause méridienne dans '{settings_sheet}' est invalide")
    elif database['settings']['lunch_break_finish_time'] < 0:
        result.append(f"L'heure de fin de pause méridienne '{settings_sheet}' est invalide")
    else:
        sane = True
        if not day_start_time < day_finish_time:

            result.append(f"Les horaires de début et de fin de journée dans '{settings_sheet}' sont incohérents")
            sane = False
        if not lunch_break_start_time <= lunch_break_finish_time:
            result.append(f"Les horaires de début et de fin de pause méridienne dans '{settings_sheet}' sont incohérents")
            sane = False
        if sane and not (day_start_time <= lunch_break_start_time
                       and lunch_break_start_time < day_finish_time):
            result.append(f"La pause méridienne dans '{settings_sheet}' ne commence pas pendant la journée")
        if sane and not (day_start_time < lunch_break_finish_time
                       and lunch_break_finish_time <= day_finish_time):
            result.append(f"La pause méridienne dans '{settings_sheet}' ne termine pas pendant la journée")

    #
    # check default duration
    #
    if database['settings']['default_preference_duration'] < 0:
        result.append(f"La granularité des séances dans '{settings_sheet}' est invalide")

    #
    # check days
    #
    if len(database['settings']['days']) == 0:
        result.append(f"Aucun jour ouvrable déclaré dans '{settings_sheet}'")

    #
    # check periods
    #
    periods = database['settings']['periods']
    if len(periods) == 0:
        result.append(f"Aucune période n'est définie dans '{settings_sheet}'")

    result.extend(check_duplicates(periods.keys(), f"périodes dans '{settings_sheet}'"))

    valid_periods = []
    for id_, (start, finish) in periods.items():
        if start < 0:
            result.append(f"Le début de la période '{id_}' dans '{settings_sheet}' est invalide")
        elif finish < 0:
            result.append(f"La fin de la période '{id_}' dans '{settings_sheet}' est invalide")
        elif not id_.startswith(':INVALID:'):
            valid_periods.append((id_, start, finish))
    # result.extend(check_non_overlapping_periods(valid_periods))

    return result


def check_rooms_sheet(database):
    result = []

    if len(database['rooms']) == 0:
        result.append(f"Votre liste de salles dans '{rooms_sheet}' est vide!")

    result.extend(check_duplicates(database['rooms'], "salle dans '{rooms_sheet}'"))
    result.extend(check_duplicates(database['room_groups'].keys(), f"groupes de salles dans '{rooms_sheet}'"))
    result.extend(check_duplicates(database['room_categories'].keys(), f"catégories de salles dans '{rooms_sheet}'"))

    empty = set()
    for id_, rooms in database['room_groups'].items():
        if len(rooms) == 0 and not id_.startswith(':INVALID:'):
            empty.add(id_)
    if len(empty) > 0:
        result.append("Les groupes de salles suivants dans '{0:s}' sont vides : {1:s}".format(rooms_sheet,
                                                                                             ', '.join(empty)))

    empty = set()
    for id_, rooms in database['room_categories'].items():
        if len(rooms) == 0 and not id_.startswith(':INVALID:'):
            empty.add(id_)
    if len(empty) > 0:
        result.append("Les catégories de salles suivantes dans '{0:s}' sont vides : {1:s}".format(rooms_sheet,
                                                                                                 ', '.join(empty)))

    # don't accept group names in groups
    group_names = database['room_groups'].keys()
    for id_, rooms in database['room_groups'].items():
        bad = rooms.intersection(group_names)
        if len(bad) > 0:
            result.append("Le groupe de salles '{0:s}' dans '{1:s}' contient des noms de groupe : {2:s}".format(id_, rooms_sheet, ', '.join(bad)))

    # don't accept category names in categories
    # cat_names = database['room_categories'].keys()
    # for id_, names in database['room_categories'].items():
    #     bad = set.intersection(names, cat_names)
    #     if len(bad) > 0:
    #         result.append("La catégorie de salles '{0:s}' dans '{1:s}' contient des noms de catégorie : {2:s}".format(id_, rooms_sheet, ', '.join(bad)))

    return result


def check_people_sheet(database):
    result = []

    people = database['people']

    if len(people) == 0:
        result.append(f"Votre liste d'intervenants dans '{people_sheet}' est vide!")

    result.extend(check_duplicates(people.keys(), f"personnes dans '{people_sheet}'"))

    for id_, person in database['people'].items():
        if person['status'] == '' and not id_.startswith(':INVALID:'):
            result.append(f"Le statut de la personne '{id_}' dans '{people_sheet}' n'est pas valide")
        if ' ' in id_:
            result.append(f"L'identifiant '{id_}' n'est pas valide : ne pas mettre d'espace")
        if ',' in id_ or ";" in id_ or "|" in id_ or "-" in id_:
            result.append(f"L'identifiant '{id_}' n'est pas valide : ne pas mettre les caractères suivants: , ; | -")
    return result


def check_groups_sheet(database):
    result = []

    #
    # check promotions
    #
    promotions = database['promotions']
    if len(promotions) == 0:
        result.append(f"Votre liste de promotions dans '{groups_sheet}' est vide!")

    result.extend(check_duplicates(promotions.keys(), f"promotion dans '{groups_sheet}'"))

    for promotion_id in promotions:
        root_nb = sum(1 for key, value in database['groups'].items()
                      if key[0] == promotion_id and value['parent'] == set())
        if root_nb == 0:
            result.append(f"La promotion '{promotion_id}' n'a pas de groupe racine (sans parent).")
        elif root_nb > 1:
            result.append(f"La promotion '{promotion_id}' a {root_nb} groupes racine (sans parent).")

    #
    # check group types
    #
    group_types = database['group_types']
    if len(group_types) == 0:
        result.append(f"Votre liste de natures de groupes dans '{groups_sheet}' est vide!")

    result.extend(check_duplicates(group_types, f"nature de groupes dans '{groups_sheet}'"))

    #
    # check groups
    #
    groups = database['groups']
    if len(groups) == 0:
        result.append(f"Votre liste de groupes dans '{groups_sheet}' est vide!")

    for (promotion, id_), group in groups.items():
        if not promotion in promotions.keys() and not id_.startswith(':INVALID:'):
            result.append(f"La promotion '{promotion}' du groupe '{id_}' dans '{groups_sheet}' n'est pas valide")
        if not group['group_type'] in group_types and not id_.startswith(':INVALID:'):
            result.append(f"La nature du groupe '{id_}' dans '{groups_sheet}' n'est pas valide")
        for parent in group['parent']:
            if not (promotion, parent) in groups.keys() and not id_.startswith(':INVALID:'):
                result.append(f"Le sur-groupe du groupe '{id_}' de la promotion '{promotion}' dans '{groups_sheet}' n'est pas valide")

    return result


def check_modules_sheet(database):
    result = []

    modules = database['modules']

    result.extend(check_duplicates(modules.keys(), f"modules dans '{modules_sheet}'"))

    for id_, module in modules.items():
        if module['short'] == '' and not id_.startswith(':INVALID:'):
            result.append(f"L'abréviation du module '{id_}' dans '{modules_sheet}' est vide")
        if not module['promotion'] in database['promotions'].keys() and not id_.startswith(':INVALID:'):
            result.append(f"La promotion du module '{id_}' dans '{modules_sheet}' est invalide")
        if not module['period'] in database['settings']['periods'].keys() and not id_.startswith(':INVALID:'):
            result.append(f"La période du module '{id_}' dans '{modules_sheet}' est invalide")
        if not module['responsable'] in database['people'].keys() and not id_.startswith(':INVALID:'):
            result.append(f"La personne responsable du module '{id_}' dans '{modules_sheet}' est invalide")

    return result


def check_courses_sheet(database):
    result = []

    courses = database['courses']

    result.extend(check_duplicates(courses.keys(), f"cours in '{courses_sheet}'"))

    for id_, course in courses.items():
        
        if course['duration'] <= 0 and not id_.startswith(':INVALID:'):
            result.append(f"Le cours '{id_}' dans '{courses_sheet}' a une durée invalide")
            
        invalid = course['group_types'].difference(database['group_types'])
        if len(invalid) > 0 and not id_.startswith(':INVALID:'):
            result.append("Certaines natures de groupe du groupe '{0:s}' dans '{1:s}' sont invalides: {2:s}".format(id_, courses_sheet, ', '.join(invalid)))
    
        settings = database['settings']
        day_start_time = settings['day_start_time']
        day_finish_time = settings['day_finish_time']
        lunch_break_start_time = settings['lunch_break_start_time']
        lunch_break_finish_time = settings['lunch_break_finish_time']
        flag_invalid = False
        flag_start_not_in_day = False
        flag_start_in_lunch_break = False
        flag_finish_not_in_day = False
        flag_finish_in_lunch_break = False
        for start_time in course['start_times']:
            if start_time < 0 and not flag_invalid:
                flag_invalid = True
                continue
            if not (start_time >= day_start_time and start_time < day_finish_time) and not flag_start_not_in_day:
                flag_start_not_in_day = True
                continue
            if start_time >= lunch_break_start_time and start_time < lunch_break_finish_time and not flag_start_in_lunch_break:
                flag_start_in_lunch_break = True
                continue
            if course['duration'] <= 0:
                continue
            end_time = start_time + course['duration']
            if not (end_time > day_start_time and end_time <= day_finish_time) and not flag_finish_not_in_day:
                flag_finish_not_in_day = True
                continue
            if end_time > lunch_break_start_time and end_time <= lunch_break_finish_time and not flag_finish_in_lunch_break:
                flag_finish_in_lunch_break = True
                continue
        if flag_invalid:
            result.append(f"L'heure de début du cours '{id_}' dans '{courses_sheet}' est invalide")
        if flag_start_not_in_day:
            result.append(f"L'heure de début du cours '{id_}' dans '{courses_sheet}' n'est pas dans la journée")
        if flag_start_in_lunch_break:
            result.append(f"L'heure de début du cours '{id_}' dans '{courses_sheet}' est dans la pause méridienne")
        # if flag_finish_not_in_day:
        #     result.append(f"L'heure de fin du cours '{id_}' dans '{courses_sheet}' n'est pas dans la journée")
        if flag_finish_in_lunch_break:
            result.append(f"L'heure de fin du cours '{id_}' dans '{courses_sheet}' est dans la pause méridienne")
    return result


##########################################
#                                        #
#        Main checker function           #
#                                        #
##########################################

def database_description_check (database):
    result = []

    if not isinstance(database, dict):
        result.append("D: the database description isn't even a dictionary!")
        return result

    separate_checkers = {
        'rooms': check_rooms,
        'room_groups': check_room_groups,
        'room_categories': check_room_categories,
        'people': check_people,
        'modules': check_modules,
        'courses': check_cours,
        'settings': check_settings,
        'promotions': check_promotions,
        'group_types': check_group_types,
        'groups': check_structural_groups,
        'transversal_groups': check_transversal_groups
    }

    invalid_keys = set(database.keys())
    invalid_keys.difference_update(separate_checkers.keys())
    if len(invalid_keys) > 0:
        result.append("D: the database description has invalid keys: {0:s}".format(', '.join(invalid_keys)))
        return result

    missing_keys = set(separate_checkers.keys())
    missing_keys.difference_update(database.keys())
    if len(missing_keys) > 0:
        result.append("D: the database description misses some keys: {0:s}".format(', '.join(invalid_keys)))
        return result

    for key, checker in separate_checkers.items():
        result.extend(checker(database[key]))

    # stop here, so the next tests can depend on a small amount of sanity
    if len(result) > 0:
        return result

    for checker in [check_settings_sheet, check_people_sheet,
                    check_rooms_sheet, check_groups_sheet,
                    check_modules_sheet, check_courses_sheet]:
        result.extend(checker(database))

    return result


if __name__ == '__main__':
    from configuration.database_description_xlsx import database_description_load_xlsx_file
    database = database_description_load_xlsx_file()
    remarks = database_description_check(database)
    if len(remarks) == 0:
        print("nil")
    else:
        for remark in remarks:
            print(remark)
