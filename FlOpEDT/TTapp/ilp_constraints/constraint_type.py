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

from enum import Enum


class ConstraintType(Enum):
    UNDEFINED = "Undefined"
    # From TTModel
    # TECHNICAL
    TECHNICAL = "Technical"
    IBS_SUP = "IBS supérieur"
    IBS_INF = "IBS inférieur"
    IBD_INF = "IBD inférieur"
    IBD_EQ = "IBD égal"
    forced_IBD = "forced_IBD"
    IBHD_INF = "IBHD_inférieur"
    IBHD_EQ = "IBHD_égal"
    IBHD_SUP = "IBHD_supérieur"
    GBHD_INF = "GBHD_inférieur"
    GBHD_SUP = "GBHD_supérieur"
    CONJONCTION = "Conjonction"
    SEUIL = "Seuil"
    CEILING_BOUND = "CEILING_BOUND"
    FLOOR_BOUND = "FLOOR_BOUND"
    SI_A_ALORS_NON_B = "Si a alors non b"

    # CORE
    PAS_PLUS_1_COURS_PAR_CRENEAU = "Pas plus d'un cours par créneau"
    COURS_DOIT_ETRE_PLACE = "Le cours doit être placé"
    COURS_DOIT_AVOIR_PROFESSEUR = "Le cours doit avoir un professeur"
    PRE_ASSIGNED_TUTORS_ONLY = "PRE_ASSIGNED_TUTORS_ONLY"
    PROFESSEUR_NE_PEUT_DONNER_2_COURS_EN_MEME_TEMPS = "Le professeur ne peut pas donner 2 cours en même temps"
    CORE_ROOMS = "Core rooms"
    SUPP_TUTOR = "Supp tutor"

    # SPECIFIC
    PAS_DE_COURS_DE_DEMI_JOURNEE = "Pas de cours de demi-journée"
    PAS_DE_PROFESSEUR_DISPONIBLE = "Pas de professeur disponible"
    SIMUL_SLOT = "Simul slot"
    SALLE_PAS_DISPONIBLE = "La salle n'est pas disponible"
    SALLE_PREFEREE_NON_DISPONIBLE = "La salle préférée n'est pas disponible"
    DEPENDANCE = "Problème de dépendance"
    PIVOT = "Pivot"
    DEPENDANCE_SALLE = "Problème de dépendance entre les salles"
    DEPARTEMENT_BLOQUE_SLOT = "Les autres départements bloquent le slot"
    PROFESSEUR_A_DEJA_COURS_EN_AUTRE_DEPARTEMENT = "Le professeur a déjà un cours dans un autre département"
    PROFESSEUR_A_DEJA_COURS_EN_AUTRE_DEPARTEMENT_IBD = "Le professeur a déjà un cours dans un autre département IBD"
    MODULETUTORREPARTITION = "Module Tutor Repartition"
    ROOMTYPE_BOUND = "ROOMTYPE_BOUND"

    # Visio
    VISIO = "Visio"
    MIN_PHYSICAL_HALF_DAYS = "MIN_PHYSICAL_HALF_DAYS"
    MAX_PHYSICAL_HALF_DAYS = "MAX_PHYSICAL_HALF_DAYS"
    NO_VISIO = "NO_VISIO"
    VISIO_ONLY = "VISIO_ONLY"
    VISIO_LIMIT_GROUP_PRESENCE = "VISIO_LIMIT_GROUP_PRESENCE"
    NO_VISIO_FOR_ALL_HALF_DAY = "NO_VISIO_FOR_ALL_HALF_DAY"
    NO_VISIO_FOR_ALL_DAY = "NO_VISIO_FOR_ALL_DAY"
    PHYSICAL_PRESENCE_SUP = "PHYSICAL_PRESENCE_SUP"
    PHYSICAL_PRESENCE_INF = "PHYSICAL_PRESENCE_INF"
    HAS_VISIO = "HAS_VISIO"
    CURFEW = "CURFEW"


    # From iut
    MAX_HOURS_PER_DAY = "Max hours per day"
    MIN_HOURS_PER_DAY = "Min hours per day"
    PAS_COURS_JEUDI_APREM = "Pas_de_cours_le_jeudi_aprem"
    PAS_SPORT_SAUF_LUNDI_ET_MARDI = "Pas de sport sauf lundi et mardi"
    PAS_COURS_PROMO1_SPORT = "pas de cours de promo1 sur un creneau de sport"
    CONF_SATELLITES = "Conference sattelites"
    B219_TO_LP = "B219 to LP"
    QUATRE_JOURS_AU_MOINS_POUR_IC = "4 jours au moins pour IC"
    SPECIFICITE_PDU = "spécificites PDU"
    REU_PEDA = "reu peda"
    SI_AJ_A_PLUS_DE_3_CRENEAUX_IL_PREFERE_VENIR_2_JOURS_DIFFERENT = "Si AJ a plus de 3 creneaux, il préfère venir 2 jours differents"
    VG_ET_AO_SONT_TOUJOURS_DANS_LA_MEME_SALLE = "VG et AO sont toujours dans la même salle"
    SEMAINE_REU_PEDAGOGIQUE_OU_EQUIPE = "Semaine de réunion pédagogique ou d'équipe"
    CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_6_CRENEAUX = "CDU veut venir une journée entière quand il a 6 créneaux"
    CDU_VEUT_VENIR_1_JOUR_ENTIER_QUAND_7_CRENEAUX = "CDU veut venir une journée entière quand il a 7 créneaux"
    SEMAINE_3_EXAM_ISI = "Semaine 3 exam d'ISI"
    SEMAINE_5_MODULE_PR_GROUPE_1_4 = "Semaine 5 module PR groupe 1 et 4"
    PTUT_NO_COURSES = "PTUT_no_Courses"
    SEMAINE_6_JURY_VENDREDI = "Semaine 6, Jury le vendredi"
    JURY = "Jury"
    SEMAINE_FLOP = "Semaine FLOP"
    VACATAIRE_FAIT_TP240_ALORS_TITULAIRE_FAIT_TP_EN_MEME_TEMPS_MEME_MATIERE = "Si un vacataire fait un TP240, un titulaire fait un TP en même temps de la même matière"
    VACACATAIRE_SANS_PERMANENTS = "Vacataires_sans_permanents"
    PAS_PLUS_1_TD_PAR_DEMI_JOURNEE = "Pas plus d'un TD par demie-journee"
    MIN_HALF_DAYS = "Min half days"
    PAS_PLUS_4_COURS_PAR_DEMI_JOURNEE = "Pas plus de 4 heures par demie_journee"
    PAS_COURS_LUNDI_8H_POUR_RT2 = "Pas de cours lundi 8h pour RT2"
    SIMUL_FAKE = "Simul fake"
    PAS_COURS_LUNDI_8H_GIM2 = "pas de cours lundi 8h pour GIM2"
    PAS_PLUS_SEANCE_MEME_MODULE_PAR_JOUR = "Pas plus de seance du meme module par jour"
    SEMAINE_2_COURS_NBE_PPP3_VENDREDI = "semaine 2 Les cours de NBE de PPP3 sont le vendredi"
    SEMAINE_6_COURS_DBE_PPP2_LUNDI_MATIN = "semaine 6 Les cours de DBE et PPP2 sont le lundi matin"
    SEMAINE_6_COURS_CPR_PPP2_LUNDI_MATIN = "semaine 6 Les cours de CPR et PPP2 sont le lundi matin"
    SEMAINE_6_COURS_MPH_PPP2_JEUDI_APRES_MIDI = "semaine 6 Les cours de MPH et PPP2 sont le jeudi après-midi"
    SEMAINE_6_COURS_EPI_PPP2_MARDI_MATIN = "semaine 6 Les cours de EPI et PPP2 sont le mardi matin"
    TECH_MARDI_APREM = "Tech le mardi aprem"
    PAS_PLUS_5_CRENEAU = "Pas_plus_de_5_creneau"
    G1_G2_COURS_MEME_JOUR = "G1 et G2 ont cours le meme jour"

    # From TTApp/models
    MAX_HOURS = "Max hours"
    STABILIZE_ENRICH_MODEL = "Stabilize : enrich model"
    STABILIZE_THROUGH_WEEKS = "Stabilization through weeks"
    SIMULTANEOUS_COURSES = "Simultaneous courses"
    LIMITED_ROOM_CHOICES = "LIMITED_ROOM_CHOICES"
    LOCATE_ALL_COURSES = "LOCATE_ALL_COURSES"
    LIMITED_START_TIME_CHOICES = "LIMITED_START_TIME_CHOICES"
    LowerBoundBusyDays = "LowerBoundBusyDays"
    LUNCH_BREAK = "Lunch Breaks"
    BREAK_AROUND_COURSE = "Break around course"
    NO_TUTOR_COURSE_ON_DAY = "No tutor course on day"
    NO_GROUP_COURSE_ON_DAY = "No group course on day"
    TRAIN_PROG_FORBIDDEN_SLOT = "TRAIN_PROG_FORBIDDEN_SLOT"
    Undesired_slots_limit = "Undesired_slots_limit"
    LimitSimultaneousCoursesNumber = "LimitSimultaneousCoursesNumber"
    MinimizeBusyDays = "MinimizeBusyDays"
    AVOID_BOTH_TIME_SAME_DAY = "AVOID_BOTH_TIME_SAME_DAY"
    NOT_ALONE = "NOT_ALONE"

    # From minhalfdays
    MIN_HALF_DAYS_LIMIT = "Min Half Days limit"
    MIN_HALF_DAYS_LOCAL = "Min Half Days local"
    MIN_HALF_DAYS_JOIN_AM = "Min Half Days join AM"
    MIN_HALF_DAYS_JOIN_PM = "Min Half Days join PM"
    MIN_HALF_DAYS_SUP = "MIN_HALF_DAYS_SUP"
    MIN_HALF_DAYS_INF = "MIN_HALF_DAYS_INF"

    # From Cosmo
    JOURS_CONSECUTIFS = "Jours consécutifs"
    jours_de_repos_par_semaine = "jours_de_repos_par_semaine"
    COSMO = "Cosmo - to be defined"
    TRAVAILLE_ASSEZ = "TRAVAILLE_ASSEZ"
    TRAVAILLE_ASSEZ_PAR_SEMAINE = "TRAVAILLE_ASSEZ_PAR_SEMAINE"
    MOD_PER_DAY = "MOD_PER_DAY"
    TUTOR_PER_DAY = "TUTOR_PER_DAY"
    module_by_bloc = "module_by_bloc"
    END_OF_BLOC = "END_OF_BLOC"
    MAX_HOLES = "MAX_HOLES"
    MENAGE = "MENAGE"
    PATRONS_SEMAINE_MOINS_DEUX = "PATRONS_SEMAINE_MOINS_DEUX"
    DIFF_MAX_ENTRE_PATRONS = "DIFF_MAX_ENTRE_PATRONS"
    UN_SEUL_PATRON = "UN_SEUL_PATRON"
    TEAM_MEETING = "TEAM_MEETING"
    REST_DAYS_PER_WEEK = "REST_DAYS_PER_WEEK"
    CONSECUTIVE_REST_DAYS_PER_WEEK = "CONSECUTIVE_REST_DAYS_PER_WEEK"
    SUSPENS_HOURS = "SUSPENS_HOURS"
    IF_MOD_A_THEN_NOT_MOD_B = "IF_MOD_A_THEN_NOT_MOD_B"
    LONG_ENOUGH_EVENINGS = "LONG_ENOUGH_EVENINGS"
    WORKS_ON_EVENING = "WORKS_ON_EVENING"
    AT_LEAST_ONCE_ON_MOD = "AT_LEAST_ONCE_ON_MOD"
    NOT_ON_MOD = "NOT_ON_MOD"
    MAX_AMPLITUDE_PER_DAY = "MAX_AMPLITUDE_PER_DAY"
    NIGHT_BREAK = "NIGHT_BREAK"
    MIN_WE = "MIN_WE"
    TRAVAILLE_PAS_TROP = "TRAVAILLE_PAS_TROP"
    max_time_per_week = "max_time_per_week"
    min_time_per_week = "min_time_per_week"

    # Gardes
    GARDES = "Gardes"
    SOIR_AUBE = "Soir et Aube"
    PAUSE_APRES_NUIT = "PAUSE_APRES_NUIT"
    PAS_TROP_D_HEURES = "Pas trop d'heures par jours glissants"
    PAS_TROP_DE_NUITS = "Pas trop de nuits par jours glissants"
    TECHNICAL_WE = 'TECHNICAL_WE'
    ASSEZ_DE_WE = 'ASSEZ_DE_WE libres'
    ASSEZ_DE_quasiWE = 'ASSEZ_DE_quasiWE libres '
    ASSEZ_DE_WE_OU_QUASI = 'ASSEZ_DE_WE_OU_QUASI libres'
    ASSEZ_DE_dimanches = 'Assez dimanches travaillés'
    PAS_TROP_DE_dimanches = 'Pas trop de dimanches travaillés'
    ASSEZ_DE_SAMEDIS = 'Assez de samedis travaillés'
    PAS_TROP_DE_SAMEDIS = 'Pas trop de samedis travaillés'
    ASSEZ_DE_SAMEDIS_ET_DIM = 'Assez de samedis/dimanches travaillés'
    PAS_TROP_DE_SAMEDIS_ET_DIM = 'Pas trop de samedis/dimanches travaillés'
    GARDES_DE_24H = "GARDES_DE_24H"
    AU_MOINS_UNE_GARDE = "AU_MOINS_UNE_GARDE"
    AU_PLUS_DEUX_GARDES = "AU_PLUS_DEUX_GARDES"
    EGALITE_GARDES = "EGALITE_GARDES"
    AU_MOINS_DEUX_GARDES = "AU_MOINS_DEUX_GARDES"
    JOUR_GARDE = "JOUR_GARDE"
    PAS_QUE_CES_POSTES = "PAS_QUE_CES_POSTES"
