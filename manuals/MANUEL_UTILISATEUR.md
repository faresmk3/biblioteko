# Biblioteko - Manuel Utilisateur

**Biblioteko** est un système de bibliothèque numérique sécurisé incluant modération par IA et gestion des droits d'auteur.

---

## Table des Matières

1. [Installation & Configuration](#1-installation--configuration)
2. [Guide de l'Interface Web](#2-guide-de-linterface-web)
3. [Guide Administrateur](#3-guide-administrateur)
4. [Interface en Ligne de Commande (CLI)](#4-interface-en-ligne-de-commande-cli)
5. [Dépannage](#5-dépannage)

---

## 1. Installation & Configuration

/ ! \ Sous Windows, il peut être préférable d'écrire « python » lorsque vous exécutez certaines commandes, car parfois, lorsque vous écrivez « python3 », Windows ne reconnaît pas la commande et vous indique que Python n'existe pas ou n'est pas installé.

### Prérequis

- **Python 3.9** ou version supérieure.
- Une **Clé API Google Gemini** (pour l'analyse automatique).

### Installation pas-à-pas

1.  **Ouvrez un terminal** dans le dossier du projet.

2.  **Créez et activez l'environnement virtuel** :

    - _Windows_ :
      ```powershell
      python -m venv venv
      venv\Scripts\activate
      ```
    - _Mac/Linux_ :
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Installez les dépendances** :

    ```bash
    pip install pyramid waitress google-generativeai python-dotenv chameleon
    ```

4.  **Configuration de la clé API** :
    Créez un fichier `.env` à la racine et ajoutez cette ligne :

    ```ini
    GOOGLE_API_KEY=AIzaSy... (Votre clé ici)
    ```

5.  **Initialisation de la base de données** :
    Cette commande crée les dossiers nécessaires et le compte Admin par défaut.

    ```bash
    python cli.py init
    ```

6.  **Lancer le serveur** :

    ```bash
    python main_web.py
    ```

    Ouvrez votre navigateur sur : **`http://localhost:6543`**

7.  Pour vous faciliter la tâche, un fichier nommé `requirements.txt` contient toutes les dépendances nécessaires au bon fonctionnement du programme. Il vous suffit d'écrire dans le terminal, tout en vous trouvant dans le répertoire racine du projet, et d'exécuter la commande suivante :

sous Mac/Linux :

```bash
pip install -r requirements.txt
```

même commande pour les machines Windows.

---

## 2. Guide de l'Interface Web

### Inscription & Connexion

- **S'inscrire** : Créez un compte. Vous obtiendrez automatiquement le rôle **Membre** (Droit de déposer et d'emprunter).
- **Connexion** : Utilisez votre email et mot de passe.
  - _Admin par défaut_ : `admin@biblio.com` / `admin123`

### Soumettre une Œuvre (Dépôt)

1.  Allez sur la page **"Dépôt"**.
2.  (Optionnel) Remplissez Titre et Auteur. Si vide, l'IA essaiera de les détecter.
3.  Sélectionnez un **fichier PDF**.
4.  Cliquez sur **"Soumettre"**.
    - _Note_ : L'IA analyse le texte pour déterminer le statut juridique (Domaine Public ou Privé).

### Consulter & Emprunter

Le catalogue est divisé en deux sections :

- ** Domaine Public** : Œuvres gratuites. Vous pouvez voir le PDF ou le texte Markdown immédiatement.
- ** Catalogue Séquestre** : Œuvres sous droits. Le fichier est chiffré sur le serveur.
  - **Pour lire** : Cliquez sur **"Emprunter"**. L'œuvre passe dans "Mes Emprunts Actifs".
  - **Lecture** : Cliquez sur **"Lire"** pour déchiffrer et ouvrir le PDF dans le navigateur.

---

## 3. Guide Administrateur

_Accès réservé aux utilisateurs ayant le rôle `admin`._

### Le Panneau de Modération (`/moderation`)

Quand un utilisateur dépose un fichier, il arrive dans la file **"À Modérer"**.

1.  **Analyse IA** : Le système affiche les métadonnées et une recommandation (ex: "Auteur décédé en 1900 -> Domaine Public").
2.  **Édition** : Vous pouvez corriger le Titre, l'Auteur ou les Catégories.
3.  **Définir le Statut Juridique** :
    - ** Sous Droits ** : Chiffre le fichier (Emprunt requis).
    - ** Domaine Public ** : Fichier ouvert à tous.
4.  **Action** :
    - **Valider** : Traite le fichier et le déplace.
    - **Rejeter** : Supprime le fichier.

### Gestion Automatique des Droits

Les œuvres peuvent être déplacées automatiquement vers le Domaine Public si leur date de publication dépasse 70 ans.

- **URL** : `http://localhost:6543/admin/check_rights`

---

## 4. Interface en Ligne de Commande (CLI)

Vous pouvez gérer le système sans navigateur via `cli.py`.

| Commande       | Description                    | Exemple                                                    |
| :------------- | :----------------------------- | :--------------------------------------------------------- |
| `init`         | Réinitialise la BDD et l'Admin | `python cli.py init`                                       |
| `register`     | Créer un utilisateur           | `python cli.py register "Nom" "email" "mdp"`               |
| `submit`       | Uploader un PDF                | `python cli.py submit "email" "file.pdf" "Titre" "Auteur"` |
| `list_pending` | Voir la file de modération     | `python cli.py list_pending`                               |
| `check_rights` | Vérifier expiration droits     | `python cli.py check_rights`                               |

---

## 5. Dépannage

### "Access Denied" lors du dépôt

- **Cause** : Le compte utilisateur n'a pas la permission `peut_proposer_oeuvre`.
- **Solution** : Si vous avez mis à jour le code récemment, supprimez `bibliotheque_data/users.json` et relancez le serveur pour recréer les utilisateurs avec la bonne structure de Rôles.

### Erreur 500 sur la page Modération

- **Cause** : Un fichier JSON corrompu (sortie IA invalide) bloque le chargement.
- **Solution** : Allez dans `bibliotheque_data/a_moderer/` et supprimez manuellement tous les fichiers `.json` et `.pdf`.

### Le lien PDF renvoie une erreur 404

- **Cause** : Mauvais préfixe d'URL.
- **Solution** : Assurez-vous que le template utilise `/data/` et non `/static/` pour les liens fichiers.
