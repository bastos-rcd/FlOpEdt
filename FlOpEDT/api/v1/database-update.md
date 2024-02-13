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

- `models/preferences.py`
  - filename -> `models/availability.py`
  - `userPreference` -> `userAvailability`

## Nettoyage

### UserPreference

- [ ] Un `User` en `ForeignKey` plutôt qu'un `Tutor`
- [ ] Création automatique de la semaine type à la création d'un `Tutor` ?
- [x] ajout d'un index sur les User/

## Autre

- attention people/0037, TTapp/0077, base/0093 viennent de migrations non commitées précédentes
