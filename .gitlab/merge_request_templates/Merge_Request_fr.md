<!-- inspiré très fortement de https://github.com/bchavez/RethinkDb.Driver/blob/master/.github/PULL_REQUEST_TEMPLATE.md -->

## Liste des choses à vérifier

Merci de vérifier is votre Merge Request (MR) satisfait bien aux conditions suivantes (mettre un 'x' pour cocher la case) :
- [ ] Le code et les commentaires sont en anglais
- [ ] Nous avons ajouté nos noms dans le fichier `AUTHORS.md`
- [ ] Nous avons ajouté quelques mots d'anglais dans le `CHANGELOG.md` pour résumer notre travail
- [ ] Si nous avons utilisé de nouveaux modules python, nous les avons ajoutés dans le fichier `requirements.txt`
- [ ] Nous avons effectué quelques tests
  - [ ] et les avons ajoutés au dépôt
  - [ ] rapidement, en local
- [ ] L'intégration continue reste satisfaite
- [ ] Nous avons ajouté, modifié et revu la documentation, si nécessaire. On peut effectuer une MR sur la page wiki de FlOpEDT, comme expliqué ici : https://stackoverflow.com/a/38537453
- [ ] Nous n'avons pas ajouté d'affichage dans les consoles (ni dans celle de django (avec `print`), ni dans celle du navigateur (avec des `console.log`))


## Nouvelles dépendances

### Des dépendances nouvelles ont-elles été ajoutées ?

- Côté back
  - [ ] Oui
  - [ ] Non
- Côté front
  - [ ] Oui
  - [ ] Non

Si oui, lesquelles ?

### Licences

Si de nouvelles dépendances ont été ajoutées, leurs licences sont compatibles avec une inclusion dans un logiciel sous AGPL version 3.0 ou ultérieure.

- [ ] Tout à fait
- [ ] J'ai regardé, mais j'ai un doute. Franchement, les licences, c'est compliqué.
- [ ] Non, mais il existe une alternative.

Si non, quelle(s) alternative(s) ?


## Type de Merge Request

<!-- Merci de ne faire que des MR à type unique ; soumettre plusieurs MRs au besoin. --> 

Merci d'indiquer le type de votre MR (mettre un 'x' pour cocher la case) :
- [ ] Réparation de bug
- [ ] Fonctionnalité
- [ ] Passage de la v0 à la v1
- [ ] Mise à jour de style sur le code (formatage, renommage)
- [ ] Refactoring (pas de changement fonctionnel, ni de changement d'API)
- [ ] Autre (à décrire) : 


## Quel est le comportement actuel ?
<!-- Décrire le comportement que vous modifiez, ou donner le numéro d'issue associé. -->


## Quel est le nouveau comportement ?
<!-- Décrire le comportement ou les changements induits par la MR. -->

-
-
-

## Est-ce que cette MR casse une autre fonctionnalité ?

- [ ] Oui
- [ ] Non

<!-- Si une rupture est introduite, merci d'en décrire l'impact. -->


## Est-ce que cette MR contient de nouvelles migrations de base ?

- [ ] Oui
- [ ] Non


## Informations supplémentaires ?

<!-- N'importe quelle information utile, comme une capture écran qui comparerait le comportement initial et le nouveau comportement -->
<!-- Ou alors : on a cassé la CI, mais on a une très bonne raison. -->
