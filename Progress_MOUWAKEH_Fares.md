# 1 le 22 Septembre

- J'ai pu consulter le cours de Génie logiciel du prof, j'ai commencé à comprendre comment à partir d'un text ou un cahier des charges d'analyser le text, savoir identifier les choses et à partir des verbes ou des besoins d'imaginer à quoi cela va correspondre dans le logiciel et avoir une idée générale de comment établir les bases ou les idées principales avant d'établir l'architécture du logiciel.
- On a appris aussi comment intérroger l'IA afin de transformer une image avec du text à un fichier en format `md` ou autres formats, un point essentiel à prendre en compte pour ce logiciel et pour l'avenir.

# 3

Le 6 Octobre

- J'ai pu avancer sur le glossaire, distingution d'actions et le glossaire de métier pour organiser les mots clés et les débuts du glossaire technique.

Le 20 Octobre

- Comment faire pour protéger les oeuvres??
- pour moi la manière la plus simple qui ne nécessite pas beaucoup de temps c'est de faire les choses avec les deux choses suivantes :

1. chiffrement de l'oeuvre with : le nom de l'oeuvre avec le nom+prénom de la personne.
2. mettre une sorte de watermark basique avec python (il existe des bibliothèques pour ce genre de choses). (forensic watermark) pourrait être une bonne idée (dans l'avenir) pour améliorer la sécurité. donc pour watermark, sur chaque page on peut mettre une sorte de **downloaded book X by Y at Date from biblioteko**. on peut même pousser cela un peut plus loin en laissant les modérateurs (bibliothécaire) eux donner l'authorisation à la personne?

Le 3 Novembre

- on a commencé par utiliser `draw.io` pour définir les choses et avoir un schéma pour commencer voilà le lien : https://drive.google.com/file/d/15zmeYrO9jNQ8QWuu1AjE7ieH8mVVRpMz/view?usp=sharing
- on a travaillé sur les diagrammes de scénarios, on n'a pas tout les scénarios mais on a inclu ce que l'on avait déjà ce qui était 15 scénarios.

Le 10 Novembre

- on a commencé à faire les diagrammes de classes. pour cela on a choisi finalement d'aller avec le Design pattern `State` pour les oeuvre afin de décrire l'état dans lequel l'oeuvre est. car chaque oeuvre passe par plusieurs états lorsqu'un utilisateur veut soumettre un livre. Le design pattern `State` a été choisi afin de faciliter l'implémentation des différents états et faciliter la modification ou l'ajout d'autres états dans l'avenir.
  les états que l'on a eu à la fin :
- soumise
- en train de traitement
- acceptée
- refusée

Le 17 Novembre:

- on a repris le travail sur les diagrammes de classes. on a implémenté le design pattern `State` pour l'état de l'oeuvre au niveau de la modératin ainsi que l'état d'une demande de changement de rôle (passer d'un utilisateur lambda à un bibliothécaire par exemple) car ces deux derniers ils ont un état similaire au niveau du traitement donc on a apperçu que cela est logique à implémenter comme cela. pour les rôles cela facilite l'implémentation et le passage aux autres rôles si jamais ajoutés dans l'avenir.
- On passe au `Service Layer` dans cette séance: `qui fait l'action de coordonner la vérification des droits, la modification de l'œuvre et l'enregistrement dans Git ?

Si vous mettez tout cela dans le contrôleur Web (Pyramid), votre code devient dépendant du framework Web. Si vous le mettez dans la classe Oeuvre, votre objet métier devient dépendant de Git (ce qui est une mauvaise pratique).

Le Service Layer (ServiceOeuvre) sert de tampon et garantit la Modularité.

Ses responsabilités exactes :
Orchestration : Il ne fait pas le travail métier "dur" (c'est l'objet Oeuvre qui change son propre état via le Pattern State), mais il enchaîne les étapes.

Sécurité (RBAC) Role-Based Access Control : C'est le point d'entrée unique pour vérifier : "Est-ce que cet utilisateur a la permission peut_moderer ?" avant de lancer l'action.

Transaction & Persistance : C'est lui qui dit à la couche technique : "Maintenant que l'œuvre est validée, déplace le fichier dans le dossier fond_commun du dépôt Git".

Abstraction : Il permet de changer l'interface (passer de Pyramid à une ligne de commande comme demandé dans le sujet) sans changer le code métier. La ligne de commande appellera le même ServiceOeuvre que le site web.`
