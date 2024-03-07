# /!\ DISCLAIMER /!\

La branche `master` suit de loin [la branche
`dev`](https://framagit.org/flopedt/FlOpEDT/-/tree/dev).

Utilisez donc cette branche (`git checkout dev` après clonage) et [son
README](https://framagit.org/flopedt/FlOpEDT/-/blob/dev/README.md).



![Logo](./FlOpEDT/base/static/base/img/flop2.png)

FlOpEDT/FlOpScheduler est un outil de gestion
d'emplois du temps comprenant :
- une application web permettant aux utilisateurs
  * d'exprimer leurs contraintes et préférences
  * de modifier l'emploi du temps
- un moteur de génération d'emplois du temps qui respectent les contraintes et
maximisent la satisfaction générale.

![Aperçu de la vue d'accueil](./img/edt-accueil.jpg)
![Aperçu de la vue de changement des disponibilités (/préférences)](./img/edt-dispos.jpg)

## Licence

[AGPL v3](https://www.gnu.org/licenses/agpl-3.0.html)

## Principales dépendances
- [Django](https://www.djangoproject.com/) pour la partie back du site
- [PostgreSQL](https://www.postgresql.org/) pour la base de données
- [PuLP](https://github.com/coin-or/pulp) pour la modélisation en ILP (Integer Linear Programming)
- Un solveur de ILP, e.g. [CBC](https://projects.coin-or.org/Cbc), [Gurobi](gurobi.com)
- [Redis](https://redis.io) pour le cache de Django (optionnel)
- [Vue.js](https://vuejs.org/) Pour la partie front du site

## Installation et lancement de l'application
Voir le wiki du projet [ici](https://framagit.org/flopedt/FlOpEDT/-/wikis/home).

## Interface de programmation (API) REST
Voir [la documentation dédiée](./FlOpEDT/api/README.md)

## Contributions
- [Discuter](https://framateam.org/flopedt/)
- [Soulever une issue](https://framagit.org/FlOpEDT/FlOpEDT/issues)


