```mermaid
classDiagram
  class Membre {
    -String nom
    -String prenom
    -String couriel
    -String mdp
  }

  class Bibliothecaire {
  }

  class Auteur {
    -String nom
    -String prenom
    -String date_de_naissance
  }

  class Oeuvre {
    -String nom
    -String prenom
    -String date_de_publication % TODO: créer une class Date ou laisser en tant que String ?%
    -Auteur auteur
  }

  class DroitAuteur { %TODO: à voir ce qu'on peut faire avec%

  }

  class Livre {
  }

  class Musique {

  }

  class Video {

  }

  class Article {

  }

  class Location {
    -Oeuvre oeuvre
    -Stirng date_de_emprunt
    -String date_de_retour
    -Boolean is_late %TODO: à voir%
    -Membre loueur
    -Membre locataire
  }

  class EtatOeuvre {
    <<abstract>>
    +soumettre() : void
    +traiter() : void
    +accepter() : void
    +refuser() : void
  }

  class EtatSoumise {

  }

  class EtatTraitement {

  }

  class EtatAccepter {

  }

  class EtatRefuser {

  }


  class ServiceLocation {
    -List~Location~ locations
    -ajouterLocation(location : Location)
    -supprimerLocatoin(location : Location)
    -getLocationsList() : List~Location~
  }

  class
EtatOeuvre <|.. EtatSoumise
EtatOeuvre <|.. EtatTraitement
EtatOeuvre <|.. EtatAccepter
EtatOeuvre <|.. EtatRefuser

Membre --> EtatOeuvre : soumet >
Bibliothecaire --> EtatOeuvre : modère >

Membre <|.. Bibliothecaire

Oeuvre <|.. Musique
Oeuvre <|.. Livre
Oeuvre <|.. Video
Oeuvre <|.. Article

Auteur "1" --> "0..*" Oeuvre : possède >

ServiceLocation "1" --> "0..*" Location
Membre "1" --> "0..*" Location
Oeuvre "1" --> "0..*" Location

```
