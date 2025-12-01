# Journal d’activité – Projet encadré

## Informations générales
- **Nom :** Assane Kane
- **Projet :** Projet D
- **Encadrant :** [Nom]
- **Période :** [Dates]

---

<h2>Jour  – 22/09</h2>

<table border="1" cellspacing="0" cellpadding="5">
  <tr>
    <th>Objectifs fixés</th>
    <th>Activités réalisées</th>
    <th>Problèmes rencontrés</th>
    <th>Solutions / Pistes</th>
    <th>Temps passé</th>
  </tr>
  <tr>
    <td>Transformer un PDF d'un livre d'image en texte et en extraire des informations</td>
    <td>
      Premier essai avec les bibliothèques Python : pdf2image, pikepdf, PIL, cv2, ...<br>
      Ensuite essayer avec l'API Gemini
    </td>
    <td>Les images ne sont pas bien découpées, ni bien rognées</td>
    <td>Pour la prochaine fois, améliorer les scripts</td>
    <td>4h</td>
  </tr>
</table>

---

<h2>Jour  03/11/2025</h2>

<table border="1" cellspacing="0" cellpadding="5">
  <tr>
    <th>Activités réalisées</th>
    <th>Problèmes rencontrés</th>
    <th>Solutions / Pistes</th>
    <th>Temps passé</th>
  </tr>
  <tr>
    <td>Discussion sur les différentes stratégies pour protéger les oeuvres qui sont sous droit d'auteur, réalistation du gragramme des cas d'utilisation avec drow.io, puis conversion du diagramme vers mermaid,</td>
    <td>conversion du fichier drow.io vers mermaid</td>
    <td>fichier mermaid obtenu</td>
    <td>4h</td>
  </tr>
</table>
---

<h2>Jour  10/11/2025</h2>

<table border="1" cellspacing="0" cellpadding="5">
  <tr>
    <th>Activités réalisées</th>
    <th>Problèmes rencontrés</th>
    <th>Solutions / Pistes</th>
    <th>Temps passé</th>
  </tr>
  <tr>
    <td>Enumération des classes avec l'aide des glossaies métier et techniques et aussi le digramme de cas d'utilisation réalisé précédemment, Réalisation du diagramme de classe du pattern STATE pour gérer les différents états et opérations qu'on peut avoir au cours de la modération d'une ouvre.Ajout de classes comment ServiceLocation, DroitAuteur pour permetre une meilleur séparation des responsabilités dans le code, Supression de la classe Bibliothécaire et ajout des classes Role et Permission pour mieux gérer les rôles et les permissions </td>
    <td>Compréhension du Patern State</td>
    <td>Patern state fait</td>
    <td>4h</td>
  </tr>
</table>
---


<h2>Jour  17/11/2025</h2>

<table border="1" cellspacing="0" cellpadding="5">
  <tr>
    <th>Activités réalisées</th>
    <th>Problèmes rencontrés</th>
    <th>Solutions / Pistes</th>
    <th>Temps passé</th>
  </tr>
  <tr>
    <td>
      mise à jour du diagramme de classe en intétégrand le concept de Service Layer pour mieux séparer les responsabilités, entre la location, le dépôt d'oeuvres, la modération, réalisation des digramees de séquence déposer une oeuvre, et modérer une oeuvre.
      les rôles sont gérer maintenant par le concept de RBAC(ROLE BASED ACCESS CONTROL
    </td></td>
    <td>Patern Service Layer fait</td>
    <td>4h</td>
  </tr>
</table>
---

<h2>Jour  1/12/2025</h2>

<table border="1" cellspacing="0" cellpadding="5">
  <tr>
    <th>Activités réalisées</th>
    <th>Problèmes rencontrés</th>
    <th>Solutions / Pistes</th>
    <th>Temps passé</th>
  </tr>
  <tr>
    <td>
      Choix : React est un framework JavaScript moderne basé sur des composants réutilisables, ce qui facilite le développement modulaire et la maintenabilité du code. Il permet de créer des interfaces utilisateurs dynamiques et réactives, indispensables pour une bibliothèque numérique interactive. Ses composants isolés simplifient la réalisation de tests unitaires et d’intégration. Son écosystème et sa large communauté offrent un accès facile à des bibliothèques tierces pour la gestion d’état, les formulaires ou les graphiques. React s’adapte parfaitement aux méthodes Agile, favorisant un développement incrémental et collaboratif. Il s’intègre aisément aux outils de documentation et de CI/CD, garantissant traçabilité et qualité du code. Son architecture modulaire répond aux besoins d’indépendance des fonctionnalités du projet. Enfin, React offre une expérience utilisateur fluide et moderne, en adéquation avec les attentes d’une bibliothèque numérique en ligne.

Réalisation de la fonctionalité d'authentification par rôle avec des interfaces différentes pour chaque rôle avec un fake_api.

Réalisation de dépôt d'une oeuvre avec un fake_api. 
      </td>
    </td>Confuiguration du projet pour bien définir les context d'authentification et de rôle</td>
    <td></td>
    <td>4h</td>
  </tr>
</table>
---



