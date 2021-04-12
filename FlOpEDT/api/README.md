# Interface de programmation (API) REST

Le projet tutoré intitulé FlopREST avait pour objectif de créer une API REST pour le logiciel FlOpEDT, permettant aux applications clientes d’accéder aux ressources proposées par le serveur FlOp par des URLs normalisées. Dans ce document, vous trouverez toutes les ressources nécessaires pour comprendre comment nous avons implémenté l'API et ainsi pouvoir développer de nouvelles fonctionnalités.

## Implémentation
L'interface de programmation a été implémentée dans l'application FlOpEDT par le biais d'une nouvelle application Django appelée ```api```. Cette nouvelle application permet de séparer les scripts de l'API du reste du code source afin de ne pas interférer avec d'autres développements en cours.

Les modules utilisés sont les suivants :
* ``django-filter``
* ``django-rest-auth``
* ``djangorestframework``
* ``djangorestframework-csv``



## Fonctionnement
### Les vues (```views.py```)
Les vues représentent ce que l'utilisateur va voir apparaître sur son écran lorsqu'il demandera une ressource à l'API. Elles permettent de traiter et trier les données contenues dans la base de données, et c'est ainsi que nous allons définir nos filtres sur les données à rechercher dans la base.

#### Structure d'une vue
Une vue hérite de la classe ``viewsets.ModelViewSet`` et doit avoir au minimum une classe *serializer* de renseignée en tant qu'attribut ```serializer_class``` ainsi qu'une source de donnée dont elle se servira pour l'affichage. Pour cela, vous pouvez soit ajouter un attribut queryset ou bien redéfinir la méthode ```get_queryset(self)```. Si vous choisissez la dernière de ces options, il vous faudra rajouter un paramètre basename lors de la création d'une URL d'accès à la vue. 


#### Les filtres
Il existe actuellement deux types de filtrage des données :
* le filtrage simple : il s'agit d'un système de filtrage qui se base sur des égalités (``?attribut=valeur``) qui est géré automatiquement sur tous les attributs d'un objet sérialisé par le module ``django-filter``, lorsque l'on ajoute la ligne suivante à une vue : ``filterset_fields = '__all__'``.
* le filtrage personnalisé : plus complexe, il s'agit de filtres définis à la main dans une fonction ``get_queryset(self)``. Par exemple, pour un objet ``A``, on peut avoir :

```
class AViewSet(viewsets.ModelViewSet):
    """
    ViewSet to see all the A.

    Result can be filtered as wanted with attributes b, c and d.
    """
    serializer_class = serializers.ASerializer

    def get_queryset(self):
        # Creating queryset
        queryset_A = A.objects.all()

        # Getting filters from the URL params (?b=...&c=...&d=...)
        b = self.request.query_params.get('b', None)
        c = self.request.query_params.get('c', None)
        d = self.request.query_params.get('d', None)

        # Filtering
        if b is not None:
            queryset_A = queryset_A .filter(b=b)
        if c is not None:
            queryset_A = queryset_A .filter(c=c)
        if d is not None:
            queryset_A = queryset_A .filter(d=d)
            
        return queryset_A 

```
Ici, notre filtrage n'a pas beaucoup d'intérêt étant donné qu'il s'agit d'un filtrage ``attribut=valeur`` et qu'il peut être géré par ``django-filter``, mais on pourrait imaginer que l'on ait besoin d'effectuer des opérations de comparaison avec un autre jeu de donnée (``queryset``), ou que l'on souhaite définir un comportement par défaut lorsqu'un paramètre est obligatoire.

Pour comprendre concrètement le fonctionnement des filtres personnalisés, vous pouvez lire les commentaires du fichiers ``views.py``.

Les filtres sont à renseigner dans l'URL d'accès à la vue que l'on souhaite, c'est-à-dire sous cette forme :
``@FlOpEDT/api/.../?attribut1=valeur1&attribut2=valeur2&filtre_personnalise&...`` 


### Les *serializers* (```serializers.py```)
Les *serializers* permettent de mettre en forme des données récupérées dans la base de données par une vue. Ils peuvent être utilisés de manière imbriquée, c'est-à-dire que l'on peut faire apparaître un ou plusieurs attributs d'un objet dans un autre objet.


#### Créer un *serializer* simple
Un *serializer* est une classe qui hérite de ``serializers.Serializer``, qui définit des champs avec un type prédéfini et qui redéfinit obligatoirement la classe interne ``Meta`` avec le modèle ainsi que ses attributs à sérialiser.

Si l'on souhaite créer un *serializer* pour un modèle ``A``, on obtient une classe de cette forme :

```
class ASerializer(serializers.Serializer):
	# A's fields to serialize
	attribut_A_1 = serializer.CharField()
	attribut_A_2 = serializer.CharField()

	# Model and fields to take
	class Meta:
		model = A
		fields = ['attribut_1', 'attribut_2']
```

#### Imbriquer des *serializers*

Si un modèle ``A`` possède une référence à un modèle ``B``, on peut modéliser chaque objet ``A`` avec ses attributs augmentés des attributs de l'objet ``B`` auquel il fait référence. On a alors :

```
class BSerializer(serializers.Serializer):
	# B's fields to serialize and their representation's type
	attribut_B_1 = serializer.IntegerField()
	attribut_B_2 = serializer.CharField()
	
	# Model and fields to take (same order as before)
	class Meta:
		model = B
		fields = ['attribut_1', 'attribut_2']

class ASerializer(serializers.Serializer):
	# A's fields to serialize
	attribut_A_1 = serializer.CharField()
	attribut_A_2 = serializer.CharField()

	# B's serializer
	attribut_B = BSerializer(serializers.Serializer)

	# Model and fields to take
	class Meta:
		model = A
		fields = ['attribut_1', 'attribut_2', 'attribut_B']
	

```

D'après l'exemple précédent, si le format des données demandé est JSON et qu'on appelle la vue qui utilise le *serializer* de ``A``, on aura un résultat de cette forme pour chaque objet ``A`` contenu dans la base de données :
```
{
  "attribut_A_1": <char>,
  "attribut_A_2": <char>,
  "attribut_B": {
    "attribut_B_1": <integer>,
    "attribut_B_2": <char>
  }
}
```


### Les URLs (```urls.py```)
Avant tout, afin de maintenir une bonne séparation du code source, nous avons inséré une redirection des liens ``@FlOpEDT/api`` vers le fichier ``urls.py`` de l'application Django ``api``.
Dans ``FlOpEDT/FlOpEDT/urls.py`` :
```
urlpatterns = [
	...
    url('api/', include('api.urls')),
]
```

Ainsi, pour accéder aux vues, nous avons besoin de définir le lien par lequel elles seront appelées. Pour cela, nous allons utilisé des objets ``SimpleRouter`` et créer une arborescence de liens. L'exemple suivant, dans ``api/urls.py`` :
```
routeur = routers.SimpleRouter()

routeur.register(r'a', views.AViewSet)
routeur.register(r'b', views.BViewSet)

urlpatterns = [
    path('aetb/', include(routeur.urls)),
    url('c', views.CViewSet),
]
```
rendra les vues des modèles ``A``, ``B``, et ``C`` respectivement accessibles par les URLs :
* ``@FlOpEDT/api/aetb/a``
* ``@FlOpEDT/api/aetb/b``
* ``@FlOpEDT/api/c``

Comme dit précédemment, il pourra être utile de passer un paramètre basename lors de la génération d'une URL. Pour cela, il vous suffit de procéder comme ceci:

```
routeur.register(r'a', views.AViewSet, basename="A")
```

L'attribut basename est facultatif si votre ViewSet contient un attribut ``queryset``. Cependant si, par nécessité, vous avez besoins de créer un filtre personnalisé ou de réaliser un traitemet de données dans la vue vous obligeant à surcharger la méthode get_queryset, cet attribut est obligatoire.

De plus, cet attribut permet de retrouver les requêtes au sein de templates par exemple. Ce qui peut être utile afin d'utiliser l'API au sein du logiciel. Pour cela il vous suffit de renommer l'attribut queryset par la valeur de l'attribut basename.

```
# Dans la vue
class ViewSet(...):
    ...
    # Nouvel attribut remplaçant queryset
    ceci_est_un_basename = Model.objects.all()
    ...

# Dans les urls
routerModel.register(r'url_de_la_vue', views.ViewSet, basename='ceci_est_un_basename')
```

### L'authentification
Les données qui ne sont pas accessibles lors de la consultation publique du client web FlOpEDT ne le sont pas non plus par l'API. Pour protéger ces données, nous avons utilisé le module ```django-rest-auth```

Pour accéder aux données protégées, l'utilisateur doit faire une requête afin d'obtenir un token d'authentification.
Ce token doit être ajouter à la requête pour que les données soient accessibles.

Exemple de l’utilisateur ```admin``` :

Récupération d’un token (dans un shell)
```
http post http://127.0.0.1:8000/api/api-token-auth/ username=admin password=admin
```

L’API fournit un token, exemple ```39005e0129fcddf93f7aaf054300403dfd8c```


* Requête Python :
```
#Le token est ajouté à la requête
url = 'http://127.0.0.1:8000/api/base/users/ 
headers = {'Authorization': 'Token 39005e0129fcddf93f7aaf054300403dfd8c'} 
r = requests.get(url, headers=headers) 
```


* Ou dans un shell :
```
http http://127.0.0.1:8000/hello/ 'Authorization: Token 39005e0129fcddf93f7aaf054300403dfd8c ' 
```


Grâce au token les données sont maintenant accessibles.




## Améliorations envisageables
Les données n'étant actuellement accessibles qu'en lecture, on peut imaginer étendre l'API à la création, modification et suppression de données dans la base de données.

 De plus, on pourrait certainement optimiser les accès à la base de données dans le traitement des filtres personnalisés, dans le cas où il faut plusieurs *querysets*.


## Liens utiles

[Django REST framework](https://www.django-rest-framework.org/)

[Faire des requêtes avec la base de données](https://docs.djangoproject.com/fr/2.2/topics/db/queries/)

[Configurer l'authentification à l'API](https://www.django-rest-framework.org/api-guide/authentication/)


## L'équipe FlOpREST
L'équipe FlOpREST, qui a réalisé les fonctionnalités mentionnées ci-dessus (création de l'API, accès en lecture aux modèles, filtrage, protection des données par authentification), la mise en place d'un générateur de documentation ``Swagger`` et qui a refactoré intégralement le code source en anglais, est composée de :
* Pierre LOTTE
* Lalie ARNOUD
* Paul BEZNOSIUK
* Maxime RUMEAU

