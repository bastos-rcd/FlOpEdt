## Pour ajouter un thème :
- Créer un fichier css dans `FlOpEDT/base/static/base/Themes` en reprenant un exemple d'un thème existant pour plus de faciliter
- Dans `FlOpEDT/base/models.py` ajouter une paire clé valeur pour la classe Theme correspondant à votre thème
- Dans `FlOpEDT/templates/base.html` ajouter une condition à la suite des autres en haut du fichier pour charger le fichier que vous avez créé


##In order to add a new theme :
- Create a css file in `FlOpEDT/base/static/base/Themes` using an example of an existing theme for ease of use
- In `FlOpEDT/base/models.py`, add a value key pair for the Theme class corresponding to your theme
- In `FlOpEDT/templates/base.html` add a condition to the top of the file to load the file you have created