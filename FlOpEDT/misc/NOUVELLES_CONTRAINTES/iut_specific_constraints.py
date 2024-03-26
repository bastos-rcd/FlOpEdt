# coding:utf-8

# !/usr/bin/python

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


from base.models import CourseType, Day, Department, Module, ScheduledCourse, Time
from people.models import Tutor
from TTapp.ilp_constraints.constraint import Constraint
from TTapp.ilp_constraints.constraint_type import ConstraintType
from TTapp.models import MinTutorsHalfDays, days_filter, max_weight, slots_filter


def add_iut_specific_constraints(ttmodel):
    add_iut_blagnac_specials(ttmodel)
    if ttmodel.department.abbrev == "INFO":
        add_iut_blagnac_lp(ttmodel)
        add_iut_blagnac_info(ttmodel)
    elif ttmodel.department.abbrev == "RT":
        add_iut_blagnac_rt(ttmodel)
    elif ttmodel.department.abbrev == "GIM":
        add_iut_blagnac_gim(ttmodel)
    elif ttmodel.department.abbrev == "CS":
        add_iut_blagnac_cs(ttmodel)


def add_iut_blagnac_specials(ttmodel):
    print("adding IUT Blagnac's special constraints")
    CM = CourseType.objects.get(name="CM", department=ttmodel.department)
    if ttmodel.department.abbrev == "INFO":
        DS = CourseType.objects.get(name="DS", department=ttmodel.department)
    elif ttmodel.department.abbrev == "RT":
        DS = CourseType.objects.get(name="Examen", department=ttmodel.department)
    elif ttmodel.department.abbrev == "GIM":
        DS = CourseType.objects.get(name="CTRL", department=ttmodel.department)
    elif ttmodel.department.abbrev == "CS":
        DS = CourseType.objects.get(name="Exam", department=ttmodel.department)
    # Pas de cours le jeudi après-midi (sauf pour la LP APSIO)
    pas_jeudi_PM = ttmodel.data.courses.exclude(
        groups__train_prog__abbrev__in=["APSIO", "RT2A"]
    )
    pas_jeudi_PM = pas_jeudi_PM.exclude(tutor__username__in=["JLF", "JCA", "OT"])
    pas_jeudi_PM = pas_jeudi_PM.exclude(
        tutor__status="ss", tutor__departments__abbrev="INFO"
    )
    # if 19 not in ttmodel.weeks:
    if True:
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[(sl, c)]
                for c in pas_jeudi_PM
                for sl in slots_filter(
                    ttmodel.data.compatible_slots[c], weekday=Day.THURSDAY, apm=Time.PM
                )
            ),
            "==",
            0,
            Constraint(constraint_type=ConstraintType.PAS_COURS_JEUDI_APREM),
        )

    promos1 = ttmodel.data.train_prog.filter(abbrev__in=["RT1", "GIM1", "CS1", "INFO1"])

    sports = ttmodel.data.modules.filter(abbrev="SC", train_prog__in=promos1)
    for sport in sports:
        cours_de_sport = set(ttmodel.data.courses.filter(module=sport))
        if not cours_de_sport:
            continue
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for sl in set(
                    slot
                    for slot in ttmodel.data.courses_slots
                    if not (
                        slot.day.day in [Day.MONDAY, Day.TUESDAY]
                        and slot.start_time == 17 * 60 + 15
                    )
                )
                for c in cours_de_sport & ttmodel.data.compatible_courses[sl]
            ),
            "==",
            0,
            Constraint(
                constraint_type=ConstraintType.PAS_SPORT_SAUF_LUNDI_ET_MARDI,
                modules=sport,
            ),
        )

    if promos1.exists():
        if not ttmodel.department.abbrev == "RT":
            ttmodel.add_constraint(
                ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for sl in ttmodel.data.courses_slots
                    if sl.end_time > 17 * 60 + 15
                    and sl.day in [Day.MONDAY, Day.TUESDAY]
                    for c in set(
                        ttmodel.data.courses.filter(
                            group__train_prog__in=promos1
                        ).exclude(module__abbrev="SC")
                    )
                    & ttmodel.data.compatible_courses[sl]
                ),
                "==",
                0,
                Constraint(constraint_type=ConstraintType.PAS_COURS_PROMO1_SPORT),
            )
        else:
            for sl in ttmodel.data.courses_slots:
                if sl.end_time > 17 * 60 + 15 and sl.day in [Day.MONDAY, Day.TUESDAY]:
                    ttmodel.add_to_slot_cost(
                        sl,
                        10000
                        * ttmodel.sum(
                            ttmodel.scheduled[sl, c]
                            for c in set(
                                ttmodel.data.courses.filter(
                                    groups__train_prog__in=promos1
                                ).exclude(module__abbrev="SC")
                            )
                            & ttmodel.data.compatible_courses[sl]
                        ),
                    )

    if 41 in ttmodel.weeks and ttmodel.department.abbrev in ["RT", "INFO"]:
        C = ttmodel.data.courses.filter(
            groups__train_prog__abbrev__in=["INFO2", "RT2", "RT2A", "APSIO"]
        ).exclude(module__abbrev="CONF")
        mardi_11h = slots_filter(
            ttmodel.data.courses_slots, weekday=Day.TUESDAY, start_time=11 * 60, week=41
        ).pop()
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for sl in slots_filter(
                    ttmodel.data.courses_slots, simultaneous_to=mardi_11h
                )
                for c in set(C) & ttmodel.data.compatible_courses[sl]
            ),
            "==",
            0,
            Constraint(constraint_type=ConstraintType.CONF_SATELLITES),
        )

    # if 6 in ttmodel.weeks and ttmodel.year == 2020:
    #     mardi_4 = days_filter(ttmodel.data.days, week=6, day=Day.TUESDAY).pop()
    #     mardi_11h_16h = set(sl for sl in slots_filter(ttmodel.data.courses_slots, day=mardi_4)
    #                         if 11*60 <= sl.start_time < 15*60 + 45)
    #     # ttmodel.add_constraint(ttmodel.sum(ttmodel.scheduled[sl, c]
    #     #                                    for slot in mardi_11h_16h
    #     #                                    for sl in slots_filter(ttmodel.data.courses_slots, simultaneous_to=slot)]
    #     #                                    for c in ttmodel.data.compatible_courses[sl]),
    #     #                        '==',
    #     #                        0,
    #     #                        "Journee d'ateliers citoyens")
    #     for slot in mardi_11h_16h:
    #         ttmodel.add_to_slot_cost(slot, 100 * ttmodel.sum(ttmodel.scheduled[sl, c]
    #                                                          for sl in slots_filter(ttmodel.data.courses_slots, simultaneous_to=slot)]
    #                                                          for c in ttmodel.data.compatible_courses[sl]))
    #     for i in ttmodel.data.instructors:
    #         ttmodel.add_constraint(ttmodel.IBD[(i, mardi_4)],
    #                                '==',
    #                                1)


def add_iut_blagnac_info(ttmodel):
    DS = CourseType.objects.get(name="DS", department=ttmodel.department)
    CM = CourseType.objects.get(name="CM", department=ttmodel.department)
    TD = CourseType.objects.get(name="TD", department=ttmodel.department)
    print("finally, adding info specific constraints")

    # 2019 / 2020
    # Semaine 41 et 42: IC veut venir au moins 4 jours différents
    IC = Tutor.objects.get(username="IC")
    if IC in ttmodel.data.instructors:
        for week in {41, 42}:
            if week in ttmodel.weeks:
                ttmodel.add_constraint(
                    ttmodel.sum(
                        ttmodel.IBD[IC, d]
                        for d in days_filter(ttmodel.data.days, week=week)
                    ),
                    ">=",
                    4,
                    Constraint(
                        constraint_type=ConstraintType.QUATRE_JOURS_AU_MOINS_POUR_IC
                    ),
                )

        # IC : Si cours à 15h45, cours également à 17h15 (préférence)
        for d in ttmodel.data.days:
            sl15 = slots_filter(
                ttmodel.data.availability_slots, day=d, start_time=15 * 60 + 45
            ).pop()
            sl17 = slots_filter(
                ttmodel.data.availability_slots, day=d, start_time=17 * 60 + 15
            ).pop()
            B2 = ttmodel.add_conjunct(ttmodel.IBS[IC, sl15], ttmodel.IBS[IC, sl17])
            ttmodel.add_to_inst_cost(IC, ttmodel.IBS[IC, sl15] - B2, week=d.week)

    # si PDU vient à 8h, il ne vient pas ni à 11 ni à 14.
    PDU = Tutor.objects.get(username="PDU")
    if PDU in ttmodel.data.instructors:
        for day in ttmodel.data.days:
            sl8 = slots_filter(
                ttmodel.data.availability_slots, day=day, start_time=8 * 60
            ).pop()
            sl11 = slots_filter(
                ttmodel.data.availability_slots, day=day, start_time=11 * 60
            ).pop()
            sl14 = slots_filter(
                ttmodel.data.availability_slots, day=day, start_time=14 * 60 + 15
            ).pop()
            ttmodel.add_constraint(
                ttmodel.IBS[PDU, sl8]
                + 0.5 * (ttmodel.IBS[PDU, sl11] + ttmodel.IBS[PDU, sl14]),
                "<=",
                1,
                Constraint(constraint_type=ConstraintType.SPECIFICITE_PDU, days=day),
            )

    # Semaine 40 : WE d'intégration
    if 40 in ttmodel.weeks and ttmodel.year == 2019:
        print("WE d'intégration")
        for sl in slots_filter(
            ttmodel.data.courses_slots, weekday=Day.FRIDAY, apm=Time.PM, week=40
        ):
            for c in set(
                course
                for course in ttmodel.data.compatible_courses[sl]
                if course.module.train_prog.abbrev != "APSIO"
            ):
                if c.type.name == "TD":
                    coeff = 2
                elif c.type.name == "DS":
                    coeff = 10
                elif c.type.name == "CM":
                    coeff = 8
                else:
                    coeff = 1
                # coeff *= 10
                if sl.start_time > 14 * 60 + 15:
                    coeff *= 2
                ttmodel.add_to_slot_cost(sl, coeff * ttmodel.scheduled[(sl, c)])
    # Trucs du passé...

    # Les séances de réflexion pédagogiques ont lieu à 9h, 11h ou 14h pour les 2 train_progs en même temps
    cms_peda = ttmodel.data.courses.filter(module__abbrev="Réfl. Péda")
    if len(cms_peda) == 2:
        c1 = cms_peda[0]
        c2 = cms_peda[1]
        for sl in ttmodel.data.compatible_slots[c1]:
            if sl.start_time > 15 * 60 or sl.start_time < 9 * 60:
                ttmodel.add_constraint(
                    ttmodel.scheduled[(sl, c1)] + ttmodel.scheduled[(sl, c2)],
                    "==",
                    0,
                    Constraint(constraint_type=ConstraintType.REU_PEDA, slots=sl),
                )
            else:
                ttmodel.add_constraint(
                    ttmodel.scheduled[(sl, c1)] - ttmodel.scheduled[(sl, c2)],
                    "==",
                    0,
                    Constraint(constraint_type=ConstraintType.REU_PEDA, slots=sl),
                )

    # Éviter que EPE ait un cours à 8h et un à 15h45 le même jour...)
    # prof_epe = Tutor.objects.get(username='EPE')
    # if prof_epe in ttmodel.data.instructors:
    #     cours_epe = ttmodel.data.courses.filter(tutor=prof_epe)
    #     for sl1 in ttmodel.data.courses_slots.filter(heure__hours=8):
    #         for sl2 in ttmodel.data.courses_slots.filter(jour=sl1.jour, heure__hours=15):
    #             for c1 in cours_epe:
    #                 for c2 in cours_epe.exclude(id__lte=c1.id):
    #                     ttmodel.add_constraint(
    #                         ttmodel.scheduled[(sl1, c1)] + ttmodel.scheduled[(sl2, c2)],
    #                         '<=',
    #                         1)

    # Si MN vient le vendredi après-midi, elle ne vient pas un autre matin
    # prof_mn = Tutor.objects.get(username='MN')
    # if prof_mn in ttmodel.data.instructors:
    #     v = Day.objects.get(no=4)
    #
    #     # vérifie si c'est possible dans l'idéal
    #     avail_slots_before_friday_noon = 0
    #     for sl in ttmodel.avail_instr[prof_mn]:
    #         if (sl.jour.day != Day.FRIDAY or sl.heure.apm != Time.PM) and ttmodel.avail_instr[prof_mn][sl] != 0:
    #             avail_slots_before_friday_noon += 1
    #
    #     if len(ttmodel.data.courses.filter(tutor=prof_mn)) \
    #             < avail_slots_before_friday_noon:
    #         for d in ttmodel.data.days.exclude(no=4):
    #             ttmodel.add_constraint(
    #                 ttmodel.IBHD[(prof_mn, v, Time.PM)] + ttmodel.IBHD[(prof_mn, d, Time.AM)],
    #                 '<=',
    #                 1)

    # Eviter que PSO ait un TD/TP juste avant un amphi
    # prof_pso = Tutor.objects.get(username='PSO')
    # if prof_pso in ttmodel.data.instructors:
    #     cm_ds_pso = ttmodel.data.courses.filter(tutor=prof_pso,
    #                                            type__in=[CM, DS])
    #
    #     for c in cm_ds_pso:
    #         for sl in ttmodel.data.courses_slots.exclude(heure__hours=8) \
    #                 .exclude(heure__hours=14):
    #             slots_list = list(ttmodel.data.courses_slots)
    #             sl_rank = slots_list.index(sl)
    #             sl_precedent = slots_list[sl_rank-1]
    #             for c2 in ttmodel.data.courses.filter(tutor=prof_pso) \
    #                     .exclude(id__lte=c.id):
    #                 ttmodel.add_constraint(
    #                     ttmodel.scheduled[(sl, c)] + ttmodel.scheduled[(sl_precedent, c2)],
    #                     '<=',
    #                     1)

    # Si AJ a plus de 3 creneaux, il préfère venir 2 jours differents
    prof_aj = Tutor.objects.get(username="AJ")
    if len(ttmodel.data.courses.filter(tutor=prof_aj)) > 3:
        ttmodel.add_constraint(
            ttmodel.IBD_GTE[2][prof_aj],
            "==",
            1,
            Constraint(
                constraint_type=ConstraintType.SI_AJ_A_PLUS_DE_3_CRENEAUX_IL_PREFERE_VENIR_2_JOURS_DIFFERENT
            ),
        )

    # LN prefere ne pas avoir 2 TD de la meme matiere d'affilée avec deux groupes différents
    # prof_ln = Tutor.objects.get(username='LN')
    # if prof_ln in ttmodel.data.instructors:
    #     for c in ttmodel.data.courses.filter(tutor=prof_ln, type=TD):
    #         for c2 in ttmodel.data.courses.filter(tutor=prof_ln,
    #                                              module=c.module,
    #                                              type=TD) \
    #                 .exclude(group=c.group):
    #             slots_list = list(ttmodel.data.courses_slots)
    #
    #             for sl in ttmodel.data.courses_slots:
    #                 if sl.heure.hours < 17:
    #                     sl_rank = slots_list.index(sl)
    #                     sl_suivant = slots_list[sl_rank + 1]
    #
    #                     ttmodel.obj += ttmodel.add_conjunct(ttmodel.scheduled[(sl, c)], ttmodel.scheduled[(sl_suivant, c2)])

    # VG et AO sont toujours dans la même salle!

    # Semaine de réunion péda ou d'équipe
    if ttmodel.year == 2020:
        for week in [2, 5, 7, 14]:
            if week in ttmodel.data.weeks:
                for day in days_filter(ttmodel.data.days, week=week, day=Day.THURSDAY):
                    for i in set(
                        tutor
                        for tutor in ttmodel.data.instructors
                        if tutor.status == Tutor.FULL_STAFF
                    ):
                        ttmodel.add_constraint(
                            ttmodel.IBD[(i, day)],
                            "==",
                            1,
                            Constraint(
                                constraint_type=ConstraintType.SEMAINE_REU_PEDAGOGIQUE_OU_EQUIPE
                            ),
                        )

    #######################A REVOIR:
    # CDU veut venir une journée entière (et le lendemain à 8h) quand il a 6 créneaux (ou 7)
    prof_cdu = Tutor.objects.get(username="CDU")
    if prof_cdu in ttmodel.data.instructors:
        for week in ttmodel.weeks:
            cours_cdu = set(
                c for c in ttmodel.data.courses_for_tutor[prof_cdu] if c.week == week
            )
            if len(cours_cdu) >= 6:
                cdu6 = {}
                jours = [Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY, Day.THURSDAY]
                for rang, jour in enumerate([Day.MONDAY, Day.TUESDAY, Day.WEDNESDAY]):
                    cdu6[jour] = ttmodel.add_var("cdu6_%s" % jour)
                    slots = slots_filter(
                        ttmodel.data.courses_slots, weekday=jour, week=week
                    )
                    jour_sum = ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for sl in slots
                        for c in cours_cdu & ttmodel.data.compatible_courses[sl]
                    )
                    ttmodel.add_constraint(
                        jour_sum - cdu6[jour],
                        "<=",
                        5,
                        Constraint(
                            constraint_type=ConstraintType.CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_6_CRENEAUX
                        ),
                    )  # vaut 1 si day_sum = 6
                    ttmodel.add_constraint(
                        jour_sum - 6 * cdu6[jour],
                        ">=",
                        0,
                        Constraint(
                            constraint_type=ConstraintType.CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_6_CRENEAUX
                        ),
                    )  # vaut 0 si day_sum < 6
                    if len(cours_cdu) == 7:
                        suivant_8h = slots_filter(
                            ttmodel.data.courses_slots,
                            weekday=jours[rang + 1],
                            start_time=8 * 60,
                            week=week,
                        ).pop()
                        ttmodel.add_constraint(
                            cdu6[jour]
                            - ttmodel.sum(
                                ttmodel.scheduled[suivant_8h, c]
                                for c in cours_cdu
                                & ttmodel.data.compatible_courses[suivant_8h]
                            ),
                            "==",
                            0,
                            Constraint(
                                constraint_type=ConstraintType.CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_7_CRENEAUX
                            ),
                        )
                ttmodel.add_constraint(
                    ttmodel.sum(cdu6[jour] for jour in cdu6),
                    "==",
                    1,
                    Constraint(
                        constraint_type=ConstraintType.CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_7_CRENEAUX
                    ),
                )

    # Semaine 49, nuit de l'info
    # if 49 in ttmodel.weeks and ttmodel.year == 2018:
    #     for sl in slots_filter(ttmodel.data.courses_slots, weekday=Day.THURSDAY, week=49):
    #         for c in ttmodel.data.compatible_courses[sl]:
    #             if (c.module.train_prog.abbrev == 'INFO2' and c.group.name in {'2B'}) \
    #                     or (c.module.train_prog.abbrev == 'INFO1' and c.group.name in {'4A'}):
    #                 ttmodel.obj += ttmodel.scheduled[(sl, c)]
    #             ttmodel.obj += ttmodel.scheduled[(sl, c)]

    # Semaine 3 exam d'ISI
    if 3 in ttmodel.weeks and ttmodel.year == 2020:
        C = set(ttmodel.data.courses.filter(module__abbrev="ISI", type__name="TP"))
        used_slot = {}
        for sl in slots_filter(ttmodel.data.courses_slots, week=3):
            used_slot[sl] = ttmodel.add_var("ISI_%s" % sl)
            ttmodel.add_constraint(
                10 * used_slot[sl]
                - ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in C & ttmodel.data.compatible_courses[sl]
                ),
                ">=",
                0,
                Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
            )
        ttmodel.add_constraint(
            ttmodel.sum(used_slot[sl] for sl in ttmodel.data.courses_slots),
            "<=",
            2,
            Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
        )

    # TD de POO en parallèle
    C = set(ttmodel.data.courses.filter(module__abbrev="POO", type__name="TD"))
    if C:
        used_slot = {}
        for sl in slots_filter(ttmodel.data.courses_slots):
            used_slot[sl] = ttmodel.add_var("POO_%s" % sl)
            ttmodel.add_constraint(
                20 * used_slot[sl]
                - ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in C & ttmodel.data.compatible_courses[sl]
                ),
                ">=",
                0,
                Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
            )
        ttmodel.add_constraint(
            ttmodel.sum(used_slot[sl] for sl in ttmodel.data.courses_slots),
            "<=",
            3,
            Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
        )

    # TD de RES en parallèle
    C = set(ttmodel.data.courses.filter(module__abbrev="RES", type__name="TD"))
    if C:
        used_slot = {}
        for sl in slots_filter(ttmodel.data.courses_slots):
            used_slot[sl] = ttmodel.add_var("RES_%s" % sl)
            ttmodel.add_constraint(
                20 * used_slot[sl]
                - ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in C & ttmodel.data.compatible_courses[sl]
                ),
                ">=",
                0,
                Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
            )
        ttmodel.add_constraint(
            ttmodel.sum(used_slot[sl] for sl in ttmodel.data.courses_slots),
            "<=",
            2,
            Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
        )

    # TD de AMN en parallèle
    C = set(
        ttmodel.data.courses.filter(
            module__abbrev="AMN", type__name="TD", tutor__username__in=["PSE", "---"]
        )
    )
    if C:
        n = len(C)
        used_slot = {}
        for sl in slots_filter(ttmodel.data.courses_slots):
            used_slot[sl] = ttmodel.add_var("AMN_%s" % sl)
            ttmodel.add_constraint(
                20 * used_slot[sl]
                - ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in C & ttmodel.data.compatible_courses[sl]
                ),
                ">=",
                0,
                Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
            )
        ttmodel.add_constraint(
            ttmodel.sum(used_slot[sl] for sl in ttmodel.data.courses_slots),
            "<=",
            n / 2,
            Constraint(constraint_type=ConstraintType.SEMAINE_3_EXAM_ISI),
        )

    # Semaine 4 PTUT le jeudi et le vendredi

    if 4 in ttmodel.weeks and ttmodel.year == 2019:
        C = ttmodel.data.courses.filter(groups__train_prog__abbrev="INFO2")
        for day in [Day.THURSDAY, Day.FRIDAY]:
            ttmodel.add_constraint(
                ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in C
                    for sl in slots_filter(
                        ttmodel.data.courses_slots, weekday=day, week=4
                    )
                    & ttmodel.data.compatible_slots[c]
                ),
                "==",
                0,
                Constraint(constraint_type=ConstraintType.PTUT_NO_COURSES, days=day),
            )

    if 23 in ttmodel.weeks or 24 in ttmodel.weeks:
        pas_AM = ttmodel.data.courses.filter(
            groups__train_prog__abbrev__in=["INFO1"], week__in={23, 24}
        )
        # if 19 not in ttmodel.weeks:
        if True:
            ttmodel.add_constraint(
                ttmodel.sum(
                    ttmodel.scheduled[(sl, c)]
                    for c in pas_AM
                    for sl in slots_filter(
                        ttmodel.data.compatible_slots[c], apm=Time.AM
                    )
                ),
                "==",
                0,
                Constraint(constraint_type=ConstraintType.PAS_COURS_JEUDI_APREM),
            )

    # Paul et Pablo ont un créneau de libre le lundi à 11h, sauf s'ils n'ont aucun jours en commun...
    # Paul = Tutor.objects.get(username='PRG')
    # Pablo = Tutor.objects.get(username='PSE')
    # if False and Paul in ttmodel.data.instructors and Pablo in ttmodel.data.instructors:
    #     commun = {}
    #     Les_deux_pas_cours_a_11h = {}
    #     for d in ttmodel.data.days:
    #         sl_11h=ttmodel.data.courses_slots.get(jour=d, heure__hours=11)
    #         Pablo_11h = ttmodel.add_or([ttmodel.scheduled[sl_11h,c] for c in ttmodel.data.courses_for_tutor[Pablo]])
    #         Paul_11h = ttmodel.add_or([ttmodel.scheduled[sl_11h,c] for c in ttmodel.data.courses_for_tutor[Paul]])
    #         commun[d] = ttmodel.add_conjunct(ttmodel.IBD[(Paul, d)],ttmodel.IBD[(Pablo, d)])
    #         Les_deux_pas_cours_a_11h[d] = ttmodel.add_conjunct(ttmodel.add_neg(Pablo_11h), ttmodel.add_neg(Paul_11h))
    #     pas_de_commun = ttmodel.add_neg(ttmodel.add_or([commun[d] for d in ttmodel.data.days]))
    #     ttmodel.add_constraint(pas_de_commun +
    #                            ttmodel.sum([ttmodel.add_conjunct(commun[d], Les_deux_pas_cours_a_11h[d]) for d in ttmodel.data.days])
    #                            , '>=',
    #                            1)

    # Semaine 6, Jury le vendredi!
    if 6 in ttmodel.weeks and ttmodel.year == 2019:
        vendredi = ttmodel.data.days.get(day=Day.FRIDAY)
        for i in ttmodel.data.instructors:
            if i.status == Tutor.FULL_STAFF:
                ttmodel.add_constraint(
                    ttmodel.IBD[(i, vendredi)],
                    "==",
                    1,
                    Constraint(constraint_type="Semaine 6, Jury le vendredi"),
                )
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[(sl, c)]
                for i in ttmodel.data.instructors
                if i.status == Tutor.FULL_STAFF
                for c in ttmodel.data.courses_for_tutor[i]
                for sl in slots_filter(
                    ttmodel.data.courses_slots, weekday=Day.FRIDAY, apm=Time.PM, week=6
                )
                & ttmodel.data.compatible_slots[c]
            ),
            "==",
            0,
            Constraint(constraint_type=ConstraintType.JURY),
        )
    # Semaine FLOP
    if 9 in ttmodel.weeks and ttmodel.year == 2020:
        for c in ttmodel.data.courses.filter(module__abbrev="FLOP"):
            sc = ScheduledCourse.objects.get(course=c, work_copy=14)
            slots = slots_filter(
                ttmodel.data.courses_slots, weekday=sc.day, start_time=sc.start_time
            )
            ttmodel.add_constraint(
                ttmodel.sum(
                    ttmodel.located[(slot, c, sc.room)]
                    for slot in slots & ttmodel.data.compatible_slots[c]
                ),
                "==",
                1,
                Constraint(constraint_type=ConstraintType.SEMAINE_FLOP),
            )

    # SF veut venir une matinée entière et un autre jour à 8h
    # SF = Tutor.objects.get(username='SF')
    # if SF in ttmodel.data.instructors:
    #     cours_sf=ttmodel.data.courses_for_tutor[SF]
    #     if cours_sf.count() >= 4:
    #         sf3={}
    #         for jour in ttmodel.data.days:
    #             sf3[jour] = ttmodel.add_var("sf3_%s"%jour)
    #             slots = ttmodel.data.courses_slots.filter(jour=jour, heure__apm=Time.AM)
    #             jour_sum = ttmodel.sum(
    #                 ttmodel.scheduled[sl, c] for sl in slots for c in cours_sf)
    #             ttmodel.add_constraint(jour_sum - sf3[jour], '<=', 2)  # vaut 1 si jour_sum = 3
    #             ttmodel.add_constraint(jour_sum - 3 * sf3[jour], '>=', 0)  # vaut 0 si jour_sum < 3
    #
    #         slots_8h = ttmodel.data.courses_slots.filter(heure__hours=8)
    #         ttmodel.add_constraint(
    #             ttmodel.sum(sf3[jour] for jour in ttmodel.data.days),
    #             '==',
    #             1,
    #             name="SF_half_day")
    #         ttmodel.add_constraint(
    #             ttmodel.sum(ttmodel.scheduled[sl_8h, c] for c in cours_sf for sl_8h in slots_8h),
    #             '>=',
    #             2,
    #             name="SF_8h")


def add_iut_blagnac_rt(ttmodel):
    print("finally, adding RT specific constraints")
    RT = Department.objects.get(abbrev="RT")
    local_var_un = ttmodel.add_var("UN")
    ttmodel.add_constraint(
        local_var_un, "==", 1, Constraint(constraint_type=ConstraintType.TECHNICAL)
    )

    # Les tp d'expression-Com. et d'anglais de 2h doivent être en quinconce
    # dans la mesure où y'en a le même nombre...
    M = Module.objects.filter(train_prog__department=RT)
    for i in range(1, 5):
        # J'annule!
        continue
        A = M.get(abbrev="ANG" + str(i))
        EC = M.get(abbrev="EC" + str(i))
        C_A = ttmodel.data.courses.filter(type__name="TP120", module=A)
        C_EC = ttmodel.data.courses.filter(type__name="TP120", module=EC)
        a = C_A.count()
        ec = C_EC.count()
        if a > 0:
            if a == ec:
                relation = "=="
            elif a < ec:
                relation = "<="
            else:
                relation = ">="
            contrainte = True
            for sl in ttmodel.data.compatible_slots[C_A[0]]:
                if contrainte:
                    ttmodel.add_constraint(
                        ttmodel.sum(ttmodel.scheduled[sl, c] for c in C_A)
                        - ttmodel.sum(ttmodel.scheduled[sl, c] for c in C_EC),
                        relation,
                        0,
                        Constraint(),
                    )
                else:
                    if a < ec:
                        ttmodel.add_to_slot_cost(
                            sl,
                            ttmodel.sum(ttmodel.scheduled[sl, c] for c in C_EC)
                            - ttmodel.sum(ttmodel.scheduled[sl, c] for c in C_A),
                        )
                    else:
                        ttmodel.add_to_slot_cost(
                            sl,
                            ttmodel.sum(ttmodel.scheduled[sl, c] for c in C_A)
                            - ttmodel.sum(ttmodel.scheduled[sl, c] for c in C_EC),
                        )

    # CONTRAINTE : Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière
    # PREFERENCE FORTE : LES TP240 sont en parallèle (dont au moins un permanent)
    ct = ttmodel.data.course_types.get(name="TP240")
    for week in ttmodel.weeks:
        for m in ttmodel.data.modules.filter(period__department=RT):
            assez_de_permanents = True
            courses = ttmodel.data.courses.filter(module=m, type=ct, week=week)
            if (
                courses.filter(tutor__status="fs").count()
                < courses.filter(tutor__status="ss").count()
            ):
                assez_de_permanents = False
            courses = set(courses)
            tp240unique = {}
            for sl in slots_filter(
                ttmodel.data.courses_slots, course_type=ct, week=week
            ):
                moins_de_2 = ttmodel.add_var("moins_de_deux%s_%s" % (m, sl))
                au_moins_1 = ttmodel.add_var("au_moins_1%s_%s" % (m, sl))
                ttmodel.add_constraint(
                    au_moins_1
                    - ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in courses & ttmodel.data.compatible_courses[sl]
                    ),
                    "<=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.VACATAIRE_FAIT_TP240_ALORS_TITULAIRE_FAIT_TP_EN_MEME_TEMPS_MEME_MATIERE
                    ),
                )
                ttmodel.add_constraint(
                    10 * au_moins_1
                    - ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in courses & ttmodel.data.compatible_courses[sl]
                    ),
                    ">=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.VACATAIRE_FAIT_TP240_ALORS_TITULAIRE_FAIT_TP_EN_MEME_TEMPS_MEME_MATIERE
                    ),
                )
                ttmodel.add_constraint(
                    2 * moins_de_2
                    + ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in courses & ttmodel.data.compatible_courses[sl]
                    ),
                    ">=",
                    2,
                    Constraint(
                        constraint_type=ConstraintType.VACATAIRE_FAIT_TP240_ALORS_TITULAIRE_FAIT_TP_EN_MEME_TEMPS_MEME_MATIERE
                    ),
                )
                ttmodel.add_constraint(
                    2 * moins_de_2
                    + ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in courses & ttmodel.data.compatible_courses[sl]
                    ),
                    "<=",
                    4,
                    Constraint(
                        constraint_type=ConstraintType.VACATAIRE_FAIT_TP240_ALORS_TITULAIRE_FAIT_TP_EN_MEME_TEMPS_MEME_MATIERE
                    ),
                )
                tp240unique[sl] = ttmodel.add_conjunct(moins_de_2, au_moins_1)
                ttmodel.add_to_slot_cost(sl, 100 * tp240unique[sl])
            if not assez_de_permanents:
                continue
            for sl in slots_filter(
                ttmodel.data.courses_slots, course_type=ct, week=week
            ):
                vacataires = ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in courses & ttmodel.data.compatible_courses[sl]
                    if c.tutor.status == "ss"
                )
                permanents = ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in courses & ttmodel.data.compatible_courses[sl]
                    if c.tutor.status == "fs"
                )
                vacataires_sans_permanents = ttmodel.add_var(
                    "vacataires_sans_permanents_%s_%s" % (m, sl)
                )
                ttmodel.add_constraint(
                    10 * vacataires_sans_permanents + permanents - vacataires,
                    "<=",
                    10,
                    Constraint(
                        constraint_type=ConstraintType.VACACATAIRE_SANS_PERMANENTS,
                        slots=sl,
                        modules=m,
                    ),
                )

                ttmodel.add_constraint(
                    vacataires - permanents - 10 * vacataires_sans_permanents,
                    "<=",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.VACACATAIRE_SANS_PERMANENTS,
                        slots=sl,
                        modules=m,
                    ),
                )
                ttmodel.add_to_slot_cost(sl, 100 * vacataires_sans_permanents)

    # Quand même par paire, et chaque vacataire doit avoir un permanent...

    # Eviter les trous pour les étudiants
    # --> A priori c'est ok avec les préférences des types de cours

    # Pas plus de 1 TD d'une matière par demie-journée pour chaque groupe sauf pour ENT1
    for m in ttmodel.data.modules.filter(period__department=RT).exclude(abbrev="ENT1"):
        for g in ttmodel.data.groups.filter(type__name="TD"):
            for d in ttmodel.data.days:
                for apm in [Time.AM, Time.PM]:
                    ttmodel.add_constraint(
                        ttmodel.sum(
                            ttmodel.scheduled[sl, c]
                            for c in ttmodel.data.courses.filter(
                                module=m, groups=g, type__name="TD"
                            )
                            for sl in slots_filter(
                                ttmodel.data.courses_slots, day=d, apm=apm
                            )
                            & ttmodel.data.compatible_slots[c]
                        ),
                        "<=",
                        2,
                        Constraint(
                            constraint_type=ConstraintType.PAS_PLUS_1_TD_PAR_DEMI_JOURNEE,
                            modules=m,
                            groups=g,
                            days=d,
                            apm=apm,
                        ),
                    )

    # minimiser les demie-journées pour tous les vacataires + regrouper les cours si 2 par demie-journée
    contrainte = False
    for t in ttmodel.data.instructors:
        if t.status == "ss":
            for week in ttmodel.weeks:
                heures = (
                    sum(
                        c.type.duration
                        for c in ttmodel.data.courses_for_tutor[t]
                        if c.week == week
                    )
                    / 60
                )
                nb_dj_min = heures / 4.5
                if nb_dj_min != int(nb_dj_min):
                    nb_dj_min = int(nb_dj_min) + 1
                total_dj = ttmodel.sum(
                    ttmodel.IBHD[(t, d, apm)]
                    for d in days_filter(ttmodel.data.days, week=week)
                    for apm in [Time.AM, Time.PM]
                )
                if contrainte:
                    ttmodel.add_constraint(
                        total_dj,
                        "<=",
                        nb_dj_min,
                        Constraint(
                            constraint_type=ConstraintType.MinHalfDays, instructors=t
                        ),
                    )
                else:
                    ttmodel.add_to_inst_cost(
                        t, 1000 * (total_dj - nb_dj_min * local_var_un), week=week
                    )

    # 4h max par demie journée pour PCOU, LAND
    for t in ttmodel.data.instructors:
        if t.username in ["PCOU", "LAND"]:
            for week in ttmodel.weeks:
                heures = (
                    sum(
                        c.type.duration
                        for c in ttmodel.data.courses_for_tutor[t]
                        if c.week == week
                    )
                    / 60
                )
                dispos = set(
                    a for a in ttmodel.data.availabilities[t][week] if a.value >= 1
                )
                heures_dispos = sum(up.duration for up in dispos) / 60
                if heures_dispos < 1.5 * heures:
                    continue
                for d in days_filter(ttmodel.data.days, week=week):
                    for apm in [Time.AM, Time.PM]:
                        ttmodel.add_constraint(
                            ttmodel.sum(
                                ttmodel.scheduled[sl, c] * c.type.duration
                                for sl in slots_filter(
                                    ttmodel.data.courses_slots, day=d, apm=apm
                                )
                                for c in ttmodel.data.courses_for_tutor[t]
                                & ttmodel.data.compatible_courses[sl]
                            ),
                            "<=",
                            4 * 60,
                            Constraint(
                                constraint_type=ConstraintType.PAS_PLUS_4_COURS_PAR_DEMI_JOURNEE,
                                instructors=t,
                                days=d,
                                apm=apm,
                            ),
                        )

    # # Pas plus de 2 examens par jour!
    # DS = CourseType.objects.get(name='Examen', department=ttmodel.department)
    # pas_plus_de_1_exam_par_demie_journee = True
    # if pas_plus_de_1_exam_par_demie_journee:
    #     for promo in ttmodel.train_prog:
    #         L, created = LimitCourseTypeTimePerPeriod.objects.get_or_create(max_hours=2,
    #                                          course_type=DS,
    #                                          period=LimitCourseTypeTimePerPeriod.HALF_DAY,
    #                                          train_prog=promo, department=ttmodel.department)
    #         if created:
    #             L.save()
    #             for week in ttmodel.weeks:
    #                 L.enrich_model(ttmodel, week)
    #         # L.delete()

    if 36 in ttmodel.weeks:
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for sl in slots_filter(
                    ttmodel.data.courses_slots,
                    start_time=8 * 60,
                    week=36,
                    weekday=Day.MONDAY,
                )
                for c in set(
                    ttmodel.data.courses.filter(
                        groups__train_prog__abbrev__in=["RT2", "RT2A"]
                    ).exclude(module__abbrev="SC")
                )
                & ttmodel.data.compatible_courses[sl]
            ),
            "==",
            0,
            Constraint(constraint_type=ConstraintType.PAS_COURS_LUNDI_8H_POUR_RT2),
        )


def add_iut_blagnac_gim(ttmodel):
    GIM = Department.objects.get(abbrev="GIM")
    print("Finally, adding GIM' specific constraints")
    for bg in ttmodel.data.basic_groups.filter(train_prog__abbrev="GIM1").exclude(
        name__in=["1AA", "1AM"]
    ):
        for sl1 in ttmodel.data.courses_slots:
            for sl2 in slots_filter(ttmodel.data.courses_slots, simultaneous_to=sl1) - {
                sl1
            }:
                name = (
                    "simul_slots_1AA_1AM_" + str(bg) + "_" + str(sl1) + "_" + str(sl2)
                )
                ttmodel.add_constraint(
                    ttmodel.sum(
                        ttmodel.scheduled[(sl1, c1)]
                        for g1 in ttmodel.data.groups.filter(name__in=["1AA", "1AM"])
                        for c1 in ttmodel.data.courses_for_group[g1]
                        & ttmodel.data.compatible_courses[sl1]
                    )
                    * 0.5
                    + ttmodel.sum(
                        ttmodel.scheduled[(sl2, c2)]
                        for c2 in ttmodel.data.courses_for_basic_group[bg]
                        & ttmodel.data.compatible_courses[sl2]
                    ),
                    "<=",
                    1,
                    Constraint(
                        constraint_type=ConstraintType.SIMUL_SLOT,
                        groups=bg,
                        slots=[sl1, sl2],
                    ),
                )

    TPB1 = ttmodel.data.groups.filter(name="TPB1", train_prog__abbrev="GIM2")
    TPB2 = ttmodel.data.groups.filter(name="TPB2", train_prog__abbrev="GIM2")
    for m in ttmodel.data.modules:
        G1 = TPB1
        G2 = TPB2
        if m.abbrev in ["OMM4-STA4", "MTS4-STA3"]:
            G1 = [
                ttmodel.data.groups.get(name="TPA2", train_prog__abbrev="GIM2"),
                ttmodel.data.groups.get(name="TPB2", train_prog__abbrev="GIM2"),
            ]
            G2 = [
                ttmodel.data.groups.get(name="TPB1", train_prog__abbrev="GIM2"),
                ttmodel.data.groups.get(name="TPC1", train_prog__abbrev="GIM2"),
            ]
        for nb in range(len(G1)):
            C1 = list(
                c for c in ttmodel.data.courses_for_group[G1[nb]] if c.module == m
            )
            if C1:
                C2 = list(
                    c for c in ttmodel.data.courses_for_group[G2[nb]] if c.module == m
                )
                if len(C1) != len(C2):
                    print("G1 et G2 n'ont pas le meme nombre de cours %s !" % m)
                    continue
                for i in range(len(C1)):
                    c1 = C1[i]
                    c2 = C2[i]
                    for sl in ttmodel.data.compatible_slots[c1]:
                        ttmodel.add_constraint(
                            ttmodel.scheduled[sl, c1] - ttmodel.scheduled[sl, c2],
                            "==",
                            0,
                            Constraint(
                                constraint_type=ConstraintType.SIMUL_FAKE,
                                groups=[G1[nb], G2[nb]],
                                modules=m,
                                slots=sl,
                            ),
                        )

    # TPB = ttmodel.data.groups.get(name='TPB', train_prog__abbrev='GIM2')
    # # TPCm = ttmodel.data.groups.get(name='TPCm', train_prog__abbrev='GIM2')
    # # TPC = ttmodel.data.groups.get(name='TPC', train_prog__abbrev='GIM2')
    # # TPDm = ttmodel.data.groups.get(name='TPDm', train_prog__abbrev='GIM2')
    # TD2 = ttmodel.data.groups.get(name='TD2', train_prog__abbrev='GIM2')
    # for g1,g2 in [(TPB, TD2)]: #(TPC, TPDm), (TPB, TPCm), (TPB, TD2)]:
    #     for sl1 in ttmodel.data.courses_slots:
    #         for sl2 in slots_filter(ttmodel.data.courses_slots, simultaneous_to=sl1) - {sl1}:
    #             name = 'simul_slots_%s_%s_%s_%s_%g' % (g1, g2, sl1, sl2, ttmodel.constraint_nb)
    #             ttmodel.add_constraint(ttmodel.sum(ttmodel.scheduled[(sl1, c1)]
    #                                                for c1 in ttmodel.data.courses_for_group[g1]
    #                                                & ttmodel.data.compatible_courses[sl1]) +
    #                                    ttmodel.sum(ttmodel.scheduled[(sl2, c2)]
    #                                                for c2 in ttmodel.data.courses_for_group[g2]
    #                                                & ttmodel.data.compatible_courses[sl2]),
    #                                    '<=', 1, name=name)

    # Pas de cours le lundi 8h pour GIM 2

    if 36 in ttmodel.weeks:
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for sl in slots_filter(
                    ttmodel.data.courses_slots,
                    start_time=8 * 60,
                    weekday=Day.MONDAY,
                    week=36,
                )
                for c in set(
                    ttmodel.data.courses.filter(groups__train_prog__abbrev__in=["GIM2"])
                )
                & ttmodel.data.compatible_courses[sl]
            ),
            "==",
            0,
            Constraint(constraint_type=ConstraintType.PAS_COURS_LUNDI_8H_GIM2),
        )

    # Pas plus de 2 cours par jour du même module
    for m in ttmodel.data.modules.filter(period__department=GIM).exclude(
        abbrev__in=["OMM4-STA4", "MTS4-STA3"]
    ):
        for bg in ttmodel.data.basic_groups:
            for d in ttmodel.data.days:
                ttmodel.add_constraint(
                    ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for c in ttmodel.data.courses_for_basic_group[bg]
                        if c.module == m
                        for sl in slots_filter(ttmodel.data.courses_slots, day=d)
                        & ttmodel.data.compatible_slots[c]
                    ),
                    "<=",
                    2,
                    Constraint(
                        constraint_type=ConstraintType.PAS_PLUS_SEANCE_MEME_MODULE_PAR_JOUR,
                        modules=m,
                        groups=bg,
                        days=d,
                    ),
                )

    # semaine 2 Les cours de NBE de PPP3 sont le vendredi
    if 2 in ttmodel.weeks:
        C = ttmodel.data.courses.filter(tutor__username="NBE", module__abbrev="PPP3")
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for c in C
                for sl in ttmodel.data.compatible_slots[c]
                if sl.day.day != Day.FRIDAY
            ),
            "==",
            0,
            Constraint(
                constraint_type=ConstraintType.SEMAINE_2_COURS_NBE_PPP3_VENDREDI
            ),
        )
    if 6 in ttmodel.weeks:
        CDBE = ttmodel.data.courses.filter(tutor__username="DBE", module__abbrev="PPP2")
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for c in CDBE
                for sl in ttmodel.data.compatible_slots[c]
                if sl.day.day != Day.MONDAY or sl.apm != Time.PM
            ),
            "==",
            0,
            Constraint(
                constraint_type=ConstraintType.SEMAINE_6_COURS_DBE_PPP2_LUNDI_MATIN
            ),
        )
        CPR = ttmodel.data.courses.filter(tutor__username="CPR", module__abbrev="PPP2")
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for c in CPR
                for sl in ttmodel.data.compatible_slots[c]
                if sl.day.day != Day.MONDAY or sl.apm != Time.PM
            ),
            "==",
            0,
            Constraint(
                constraint_type=ConstraintType.SEMAINE_6_COURS_CPR_PPP2_LUNDI_MATIN
            ),
        )
        CMPH = ttmodel.data.courses.filter(tutor__username="MPH", module__abbrev="PPP2")
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for c in CMPH
                for sl in ttmodel.data.compatible_slots[c]
                if sl.day.day != Day.THURSDAY or sl.apm != Time.AM
            ),
            "==",
            0,
            Constraint(
                constraint_type=ConstraintType.SEMAINE_6_COURS_MPH_PPP2_JEUDI_APRES_MIDI
            ),
        )
        CEPI = ttmodel.data.courses.filter(tutor__username="EPI", module__abbrev="PPP2")
        ttmodel.add_constraint(
            ttmodel.sum(
                ttmodel.scheduled[sl, c]
                for c in CEPI
                for sl in ttmodel.data.compatible_slots[c]
                if sl.day.day != Day.TUESDAY or sl.apm != Time.PM
            ),
            "==",
            0,
            Constraint(
                constraint_type=ConstraintType.SEMAINE_6_COURS_EPI_PPP2_MARDI_MATIN
            ),
        )


def add_iut_blagnac_cs(ttmodel):
    CS = Department.objects.get(abbrev="CS")
    print("Finally, adding CS' specific constraints")
    # - libérer au moins un après-midi (qui peut être le vendredi) à 15h40 (+)

    # TECH : NVIG et FV le mardi aprem
    for week in ttmodel.weeks:
        FV = ttmodel.data.courses.filter(
            module__abbrev="TECH", tutor__username="FV", week=week
        )
        NVIG = ttmodel.data.courses.filter(
            module__abbrev="TECH", tutor__username="NVIG", week=week
        )
        if FV.count() == 2 or NVIG.count() == 2:
            ttmodel.add_constraint(
                ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in FV | NVIG
                    for sl in ttmodel.data.compatible_slots[c]
                    - slots_filter(
                        ttmodel.data.compatible_slots[c],
                        weekday=Day.TUESDAY,
                        apm=Time.PM,
                        week=week,
                    )
                ),
                "==",
                0,
                Constraint(constraint_type=ConstraintType.TECH_MARDI_APREM),
            )

    # TECH : G1 avec NVIG et en parallèle G2 avec FV et on inverse le créneau d'après.
    # for week in range(1,51):
    #     FV = Course.objects.filter(module__abbrev='TECH', week=week, tutor__username='FV')
    #     NVIG = Course.objects.filter(module__abbrev='TECH', week=week, tutor__username='NVIG')
    #     if FV.count()!=2 or NVIG.count()!=2:
    #         continue
    #     else:
    #         FV = list(FV)
    #         NVIG = list(NVIG)
    #         d1=Dependency(cours1=FV[0], cours2=FV[1], successifs=True)
    #         d2=Dependency(cours1=FV[0], cours2=NVIG[0], successifs=True)
    #         d3=Dependency(cours1=NVIG[1], cours2=NVIG[0], successifs=True)
    #         d1.save()
    #         d2.save()
    #         d3.save()

    #  pour le module DROIT 3 du S3, je voulais mettre Exam et CC à la suite sur une demi journée
    # for week in range(1,51):
    #         Cs=list(Course.objects.filter(module__abbrev='DROIT3',week=week, type__name__in=['Exam','CC']))
    #         if not Cs:
    #             continue
    #         d1=Dependency(cours1=Cs[0], cours2=Cs[1], successifs=True)
    #         d2=Dependency(cours1=Cs[1], cours2=Cs[2], successifs=True)
    #         d1.save()
    #         d2.save()

    # Pas plus de 5 créneaux par jour pour les étudiant⋅e⋅s
    # (Pour les profs, c'est dans leur pref_...)
    for bg in ttmodel.data.basic_groups.filter(train_prog__department=CS):
        for day in ttmodel.data.days:
            ttmodel.add_constraint(
                ttmodel.sum(
                    ttmodel.scheduled[sl, c]
                    for c in ttmodel.data.courses_for_basic_group[bg]
                    for sl in slots_filter(ttmodel.data.compatible_slots[c], day=day)
                ),
                "<=",
                5,
                Constraint(
                    constraint_type=ConstraintType.PAS_PLUS_5_CRENEAU,
                    days=day,
                    groups=bg,
                ),
            )

    # si 3h d'intervention dans la semaine et dispo sur 2 demi-journées, concentrer sur 1 seule demi-journée (++)
    for week in ttmodel.weeks:
        M = MinTutorsHalfDays(
            join2courses=True, weight=max_weight, department=ttmodel.department
        )
        M.save()
        for i in ttmodel.data.instructors:
            if (
                sum(
                    c.type.duration / 60
                    for c in ttmodel.data.courses_for_tutor[i]
                    if c.week == week
                )
                <= 180
            ):
                M.tutors.add(i)
        M.save()

        M.enrich_ttmodel(ttmodel, week, ponderation=1000)
        M.delete()

    # - libérer le vendredi à 17h (++) --> Mis en indispo des train prog

    # - TD d'un même module la même demi-journée ou dans la journée = G1 et G2 auront TD le même jour  (++)
    for m in ttmodel.data.modules.filter(period__department=CS):
        g1 = ttmodel.data.groups.get(train_prog=m.train_prog, name__in=["1G1", "2G1"])
        g2 = ttmodel.data.groups.get(train_prog=m.train_prog, name__in=["1G2", "2G2"])
        Cg1 = ttmodel.data.courses_for_group[g1]
        Cg2 = ttmodel.data.courses_for_group[g2]
        if len(Cg1) == len(Cg2):
            for d in ttmodel.data.days:
                ttmodel.add_constraint(
                    ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for sl in slots_filter(ttmodel.data.courses_slots, day=d)
                        for c in Cg1 & ttmodel.data.compatible_courses[sl]
                    )
                    - ttmodel.sum(
                        ttmodel.scheduled[sl, c]
                        for sl in slots_filter(ttmodel.data.courses_slots, day=d)
                        for c in Cg2 & ttmodel.data.compatible_courses[sl]
                    ),
                    "==",
                    0,
                    Constraint(
                        constraint_type=ConstraintType.G1_G2_COURS_MEME_JOUR,
                        modules=m,
                        days=d,
                    ),
                )
