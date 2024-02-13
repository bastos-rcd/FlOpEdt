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

- [ ] Création automatique de la semaine type à la création d'un `Tutor` ?
- [x] Un `User` en `ForeignKey` plutôt qu'un `Tutor`
- [x] ajout d'un index sur les User/ --> [automatiquement](https://docs.djangoproject.com/en/4.2/ref/models/fields/#foreignkey)
- [ ] Passer les start_time et duration des Availability en vrai temps

### \*Availability

Après les migrations :

- [ ] \*AvailabilityAdmin: corriger
- [ ] \*DefaultAvailability à rediriger vers A1-S1
- [ ] is_same de Availability ? + Si semaine par défaut + terminologie < ? before ? euh toutes les fonctions, en fait

## Autre

- attention people/0037, TTapp/0077, base/0093 viennent de migrations non commitées précédentes
