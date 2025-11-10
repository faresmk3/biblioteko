sequenceDiagram
    participant Membre
    participant Application
    participant Bibliothecaire

    Note over Membre,Application: Prérequis : le membre doit être inscrit

    Membre->>Application: Demande à devenir bibliothécaire
    Application->>Application: Enregistre la demande
    Application->>Bibliothecaire: Soumet la demande pour examen

    alt Bibliothécaire accepte
        Bibliothecaire->>Application: Accepte la demande
        Application->>Membre: Met à jour état de la demande (Acceptée)
        Application->>Membre: Notification pour accepter les conditions
        Membre->>Application: Accepte les conditions
        Application->>Membre: Attribue les droits de bibliothécaire
    else Bibliothécaire rejette
        Bibliothecaire->>Application: Rejette la demande
        Application->>Membre: Met à jour état de la demande (Rejetée)
    else Bibliothécaire met en attente
        Bibliothecaire->>Application: Demande en attente
        Application->>Membre: Met à jour état de la demande (En attente)
    end

    Note over Application,Membre: Le membre peut consulter l'état de sa demande à tout moment

    %% Scénario erreur
    alt Erreur : décision corrigée
        Bibliothecaire->>Application: Modifie décision (ex. de rejet à acceptation)
        Application->>Membre: Met à jour état de la demande
    end

