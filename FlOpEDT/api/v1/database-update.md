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

- [ ] `models/preferences.py`
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

## Performance

- [ ] tester si utile de mettre un index sur le date de Availability

## Améliorations

- [ ] mettre plutôt les validations du serializer du post de UserAvailability dans le `is_valid`

## Reste du temps

- [ ] TimeGeneralSettings: \*
- [ ]

## Des trucs à savoir

- attention people/0037, TTapp/0077, base/0093 viennent de migrations non commitées précédentes
- la création de la semaine par défaut se fait automatiquement à la création d'un `Tutor`
