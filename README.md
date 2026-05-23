# Daily Music Randomizer

## Développeuse

- [Sofia CETIN](https://github.com/SofiaCetin)

## Présentation

Le "Daily Music Randomizer" est un bot Discord visant à envoyer chaque jour un titre aléatoire d'une des playlist Spotify des utilisateurs enregistrés dans la base de données du robot. L'utilisateur peut donner le droit à l'application d'effectuer des requêtes API sur les playlists de son compte Spotify. Le but est de pouvoir découvrir les titres écoutés par les autres personnes du serveur de manière complètement aléatoire.

Chaque jour à une heure précise, le bot choisit un utilisateur au hasard, puis choisit un titre aléatoire dans la playlist qu'il a enregistré dans la base de données du bot.

<img src="assets/image_readme2.png" width="300" alt="Un exemple de message envoyé chaque jour">

## Utilisation

### Fonctionnement

Afin de pouvoir récupérer les informations concernant une playlist Spotify d'un utilisateur spécifique, le programme python reçoit et envoie des requêtes HTTP via les modules Flask et requests. 

Flask permet de créer un serveur web en Python et établir des routes pour recevoir des requêtes HTTP, notamment dans le cas où il nous faut un endpoint. Requests permet d'envoyer des requêtes HTTP vers des API externes. Ils permettent donc un modèle complèmentaire d'une architecture API: le serveur HTTP(Flask), et le client HTTP(requests).

<img src="assets/image_readme2.png" width="300" alt="Une illustration pour mieux comprendre">

Spotify renvoie la réponse de chaque requête au format JSON. On peut donc y extraire les tokens d'accès ou d'actualisation d'un utilisateur, qui nous permettent de faire une nouvelle requête pour obtenir les informations de l'utilisateur Spotify en question.

### Commandes Discord

Pour se concentrer plus sur la partie façade que back-end, le coeur de ce projet est un bot Discord avec lequel les utilisateurs peuvent interagir. Nous avons donc à notre disposition, une série de commandes possibles. Les commandes s'effectuent dans le chat avec le préfixe "!".

<details>
<summary><u>link</u></summary>

Prototype:
```
!link
```

Permet d'obtenir un lien envoyé par le bot en message privé, afin de donner les autorisations(ou "scopes") Spotify nécessaires pour lui permettre d'enregistrer des playlist.

</details>

<details>
<summary><u>register_playlist</u></summary>

Prototype:
```
!register_playlist PLAYLIST_ID
```

Permet d'enregistrer la playlist où le bot piochera un titre au hasard. La playlist peut être privée ou public du moment qu'elle a été crée par l'utilisateur de la commande. Il faut que l'utilisateur ait lié son compte Spotify au bot au préalable.

L'ID d'une playlist Spotify se situe dans son lien.

```
Exemple:

https://open.spotify.com/playlist/37i9dQZF1DZ06evO3RZl6M?si=f30b2a8c822b45ba
                                  ----------------------
                                    id de la playlist

L'ID est 37i9dQZF1DZ06evO3RZl6M.
La commande s'utilisera ainsi:

!register_playlist 37i9dQZF1DZ06evO3RZl6M
```

</details>

<details>
<summary><u>change_playlist</u></summary>

Prototype:
```
!change_playlist PLAYLIST_ID
```

Permet à l'utilisateur de changer la playlist enregistrée dans la base de données. A noter qu'un utilisateur ne peut enregistrer qu'une seule playlist à la fois.

</details>

<details>
<summary><u>my_playlist_info</u></summary>

Prototype:
```
!my_playlist_info
```

Permet à l'utilisateur d'obtenir les informations de la playlist qu'il a enregistré dans la base de données.

</details>

<details>
<summary><u>remove_playlist</u></summary>
Prototype:
```
!remove_playlist
```

Permet à l'utilisateur de retirer la playlist enregistrée dans la base de données.

</details>

<details>
<summary><u>unlink</u></summary>

Prototype:
```
!unlink
```

Retire l'utilisateur de la base de données, y compris les playlist enregistrées. L'utilisateur devra de nouveau se lier avec la commande !link s'il souhaite se ré-enregistrer.

</details>

## Implémenter ce bot sur mon propre serveur

Ce projet utilisant l'API Web de Spotify en mode développement, il n'est pas possible de pouvoir interagir et stocker des tokens à grande échelle. Nous ne pouvons autoriser que 6 utilisateurs/tokens(y compris la personne qui a crée l'application) à effectuer des requêtes API dans une application Spotify en cours de développement pour des raisons de sécurité.

Si vous souhaitez utiliser ce bot sur votre serveur, il vous faudra donc déployer vos propres applications Discord et Spotify basées sur ce code source, mais également héberger la base de données.

<details>
<summary><u>Etapes nécessaires</u></summary>

1. Créer une application Discord pour ce bot, pour obtenir le token du bot
2. Créer une application Spotify pour obtenir le token du client et le token secret
3. Cloner ce dépôt sur votre machine ou votre serveur distant
4. Initialiser les variables d'environnements nécessaires au code source

</details>

