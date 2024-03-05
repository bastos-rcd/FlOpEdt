# When ready to change database structure

see `TODO V1-DB`

## Temps flop / temps standard

### EdtVersion

Dans v0: associé à une semaine

Maintenant:

- créer un EdtVersion à la génération, avec un temps début et temps fin
- récupérer les EdtVersion en même temps que les edt
- faire une opération atomique avec toutes les EdtVersion en jeu?
  ?

## Minor rename

Rename:

- [x] `models/preferences.py`
  - filename -> `models/availability.py`
  - `userPreference` -> `userAvailability`

## Nettoyage

### UserPreference

- [x] Création automatique de la semaine type à la création d'un `Tutor` ? split_availability, fill_default_user_availability
- [x] Un `User` en `ForeignKey` plutôt qu'un `Tutor`
- [x] ajout d'un index sur les User/ --> [automatiquement créé](https://docs.djangoproject.com/en/4.2/ref/models/fields/#foreignkey)
- [x] Passer les start_time et duration des Availability en vrai temps
- [x] RoomAvailability
- [ ] tests
  - [ ] création dispos par défaut
  - [ ] si appel API en post avec des timezones -> ignorer ou bad request?
- [ ] changer le param de département en department_id
- [ ] gestion des timezone
  - [x] décider -> tout en naive
  - [ ] vérifier les conséquences sur les ical
  - [ ] vérifier les conséquences sur le qcalendar
- [ ] Finir changement de temps sauf dans TTapp

### \*Availability

Après les migrations :

- [x] \*AvailabilityAdmin: corriger
- [ ] \*DefaultAvailability à rediriger vers A1-S1
  - [x] get
  - [ ] create/update
- [x] ASK PABLO is_same de Availability ? + Si semaine par défaut + terminologie < ? before ? toutes les fonctions, en fait

## Rights/belts

### Permission

- [x] UserAvailability (both normal and default week)
  - [x] push_my_useravailability -> serializer create
  - [x] push_any_useravailability -> serializer create
  - [x] view_my_useravailability -> viewset queryset
  - [x] view_any_useravailability -> viewset queryset
- RoomAvailability
  - [ ] view_roomavailability -> viewset
  - [ ] push_roomavailability -> serializer

## Performance

- [ ] tester si utile de mettre un index sur le date de Availability

## Améliorations

- [ ] mettre plutôt les validations du serializer du post de UserAvailability dans le `is_valid`
- [ ] permission plus fine sur ajout de dispo : ne pas utiliser tout le monde à pousser une dispo de n'importe qui d'autre -> dans le serializer

## Reste du temps

- [ ] TimeGeneralSettings: \*
  - [ ] Faire une entrée d'api pour remplacer get_department_settings(dept) (appelé dans base/views) (NB : les formats des start_time ont changé)
  - [x] Modifier database_description_checker | database_description_xlsx | make_filled_database_file
  - [ ] modifier tous les flopdate_to_datetime et réciproquement
  - [ ] Modifier hyperplanning.py (Pas sûr)
- [x] Period -> TrainingPeriod
  - [x] models and migrations
  - [x] refactor
- [x] SchedulingPeriod
  - [x] models et migrations
  - [x] remplacer (presque) partout où apparaît une semaine
  - [x] supprimer `Week` des models
  - [x] comment combiner TrainingPeriod et SchedulingPeriod? (liste de périodes, import excel ok)
- [-] Duration Course-CourseType
  - [x] models and migrations
  - [x] remplacer où apparaissait coursetype.duration et .pay_duration dans django
  - [x] dans le solveur
    - [x] checker le type datetime.time / timedelta dans les TTConstraints
  - [x] dans flopEditor
  - [x] dans l'import-export excel
        - [x] export_planif_file
    - [ ] revoir la view pour qu'elle permette de sélectionner les périodes du département
  - [x] modifier courseStartTimeConstraints en incluant une duration au lieu d'un course_type
  - [x] corriger la migration base/111 pour qu'elle transfère le département et la durée des types
- [ ] Les TTConstraints
  - [x] Transformer toutes les minutes en TimeField ou DurationField
  - [x] StartTimeConstraints : clarifier le rôle des possible_start_times (Time) et des possible week_days
- [ ] RoomReservation
  - [ ] Passer de TimeField et DateField en DateTimeField + api
- [ ] ics (et virer isoweek)

## Rien à voir

- [ ] interdire caractères spéciaux dans abbrev de Dept (et dans tout ce qui peut apparaître dans une url)
- [ ] setup.cfg pour les tests vs migrations
- [ ] discarded.json

## Performance

Plusieurs leviers :

- cache niveau serveur
- requêtes SQL
  - select_related: join
  - prefetch_related:
- cache niveau client
- plusieurs niveaux de endpoints dans l'API

## Des trucs à savoir

- [x] attention people/0037, TTapp/0077, base/0093 viennent de migrations non commitées précédentes
- la création de la semaine par défaut se fait automatiquement à la création d'un `Tutor`
