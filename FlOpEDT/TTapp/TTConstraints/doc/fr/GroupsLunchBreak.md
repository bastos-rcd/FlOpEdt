### Description
Garantit que les groupes {{ groups }} ont une pause repas (ou autre) d'au moins {{ lunch_length }} minutes
entre {{ start_lunch_time }} et {{ end_lunch_time }} les {{ weekdays }}.
### Exemples
| Contexte | OK | Not Ok |
|:--:|:--:|:--:|
| groups : All <br> start_time : 12h30 <br> end_time : 14h  <br> lunch_length : 60 minutes | ![Situation autorisée](../images/ok_tutors_lunch_break.png) | ![Situation interdite](../images/forbidden_tutors_lunch_break.png)|

### Paramètres:
- start_time: minutes depuis minuit (entier)
- end_time: minutes depuis minuit (entier)
- lunch_length : minutes (entier)