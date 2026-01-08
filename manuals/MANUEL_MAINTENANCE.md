# Biblioteko - Manuel de Maintenance

Ce manuel est destiné aux Administrateurs Système et Développeurs responsables de la maintenance de l'application Biblioteko.

---

## Table des Matières

1. [Vue d'ensemble du Système](#1-vue-densemble-du-système)
2. [Tâches de Maintenance Courante](#2-tâches-de-maintenance-courante)
3. [Sauvegarde & Restauration](#3-sauvegarde--restauration)
4. [Sécurité & Mises à jour](#4-sécurité--mises-à-jour)
5. [Logs & Monitoring](#5-logs--monitoring)
6. [Procédures d'Urgence](#6-procédures-durgence)

---

## 1. Vue d'ensemble du Système

### Architecture

- **Backend** : Python 3.9+ (Framework Pyramid).
- **Base de Données** : Fichiers plats JSON situés dans le dossier `bibliotheque_data/`. Aucune base SQL n'est requise.
- **Stockage** : Système de fichiers local (sous-dossiers de `bibliotheque_data/`).
- **Service Externe** : API Google Gemini (utilisée pour l'OCR et l'analyse des métadonnées).

### Répertoires Critiques

| Chemin                           | Description                               | Criticité    |
| :------------------------------- | :---------------------------------------- | :----------- |
| `src/`                           | Code source de l'application              | Haute        |
| `bibliotheque_data/users.json`   | Base utilisateurs & Rôles RBAC            | **Critique** |
| `bibliotheque_data/fond_commun/` | Fichiers PDF publics (non chiffrés)       | Haute        |
| `bibliotheque_data/sequestre/`   | Fichiers PDF privés (chiffrés)            | Haute        |
| `bibliotheque_data/a_moderer/`   | Fichiers en attente (stockage temporaire) | Moyenne      |

---

## 2. Tâches de Maintenance Courante

### Vérifications Quotidiennes/Hebdomadaires

1.  **Espace Disque** : Vérifier qu'il y a suffisamment d'espace sur le serveur pour les nouveaux uploads PDF.
2.  **Quota API** : Surveiller l'utilisation de l'API Google Gemini pour éviter d'atteindre les limites de taux ou de facturation.
3.  **File de Modération** : Vérifier périodiquement l'interface web (`/moderation`) pour s'assurer que le dossier `a_moderer` n'accumule pas de fichiers ignorés ou en échec.

### Tâches Annuelles (Tâche Cron)

- **Vérification de l'Expiration des Droits** : Lancer le script automatisé pour déplacer les œuvres entrées dans le domaine public (auteur décédé > 70 ans) du catalogue Séquestre vers le catalogue Public.
  **Commande :**
  ```bash
  python cli.py check_rights
  ```
  _Recommandation : Planifier cette tâche via `cron` (Linux) ou le Planificateur de tâches (Windows) pour s'exécuter une fois par an, le 1er Janvier._

---

## 3. Sauvegarde & Restauration

Puisque Biblioteko utilise un système de fichiers plats, les sauvegardes sont de simples copies de fichiers.

### Procédure de Sauvegarde

1.  Arrêter le serveur web pour éviter les conflits d'écriture.
2.  Copier tout le dossier `bibliotheque_data` vers un emplacement sécurisé et distant (ex: S3, disque externe, ou un autre serveur).

    **Exemple (Linux/Mac) :**

    ```bash
    cp -r bibliotheque_data /chemin/vers/backups/biblioteko_backup_$(date +%F)
    ```

3.  Redémarrer le serveur.

### Procédure de Restauration

1.  Arrêter le serveur web.
2.  Supprimer le dossier `bibliotheque_data` actuel (potentiellement corrompu).
    ```bash
    rm -rf bibliotheque_data
    ```
3.  Restaurer le dossier de sauvegarde à la racine du projet.
4.  Vérifier que les permissions de fichiers permettent au processus Python de lire/écrire les fichiers restaurés.
5.  Redémarrer le serveur.

---

## 4. Sécurité & Mises à jour

### Mise à jour des Dépendances

Mettez régulièrement à jour les paquets Python pour corriger les failles de sécurité et assurer la compatibilité.

```bash
# 1. Activer l'environnement virtuel
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# 2. Mettre à jour les paquets principaux
pip install --upgrade pyramid waitress google-generativeai

# 3. Mettre à jour le fichier requirements
pip freeze > requirements.txt
```

### Rotation des Secrets

1. Clé API (API Key) Si la clé Google Gemini API est compromise :

- Révoquez-la dans la Console Google Cloud.

- Générez une nouvelle clé.

- Mettez à jour le fichier .env immédiatement.

- Redémarrez le serveur.

2. Secret de Session (Session Secret) Si vous devez forcer la déconnexion de tous les utilisateurs (ex: après une suspicion d'intrusion) :

- Ouvrez le fichier src/app/interface/web/**init**.py.

- Changez la chaîne secrète dans cette ligne :

```python
 my_session_factory = SignedCookieSessionFactory('NOUVELLE_CLE_SUPER_SECRETE')
```

- Redémarrez le serveur. Tous les cookies de session existants deviendront invalides.

## 5. Logs & Monitoring

### Logs Applicatifs

Biblioteko affiche les logs système directement sur la sortie standard (console).

- Configuration de Production : Il est hautement recommandé de rediriger la sortie vers un fichier pour la persistance à long terme et le débogage.

```bash
python main_web.py >> biblioteko.log 2>&1 &
```

- Recherche d'Erreurs : Utilisez grep (Linux/Mac) ou un éditeur de texte pour chercher des mots-clés spécifiques comme "Error", "Exception", ou "Traceback".

```bash
tail -f biblioteko.log | grep -i "Error"
```

### Messages de Log Courants & Significations

- ✅ AI Adapter loaded : Le système a démarré avec succès et s'est connecté à l'API Google.

- ⚠️ JSON invalide ou ⚠️ Corrupt file : L'IA a renvoyé des données mal formées ou un fichier est illisible. Le système ignore généralement ces fichiers automatiquement pour éviter de planter.

- ❌ Erreur critique : Une défaillance grave de l'application s'est produite (ex: permissions manquantes, disque plein). Une investigation est requise.

## 6. Procédures d'Urgence

### Scénario A : La Page Modération Plante (Erreur 500)

- Symptômes : L'administrateur ne peut pas accéder à la page /moderation ; le serveur renvoie une "Internal Server Error".

- Diagnostic : Un fichier JSON corrompu (souvent causé par une sortie IA invalide contenant des caractères non échappés) existe dans la file d'attente et bloque la fonction de listage des fichiers.

Correction :

1. Arrêter le serveur web.

2. Naviguer vers le dossier bibliotheque_data/a_moderer/.

3. Supprimer tous les fichiers (.json et .pdf) à l'intérieur de ce dossier.

4. Redémarrer le serveur web.

5. La page de modération devrait maintenant se charger (vide).

### Scénario B : Les Permissions Utilisateurs sont Cassées ("Access Denied")

- Symptômes : Les utilisateurs ne peuvent pas soumettre de fichiers bien qu'ils soient connectés. Les logs montrent `PermissionError: Access denied`.

- Diagnostic : Cela arrive généralement si le code source concernant les Rôles/Permissions (RBAC) a été mis à jour, mais que le fichier de base de données `users.json` contient encore d'anciennes structures de données utilisateur manquant les nouveaux champs de permission.

- Correction :

1. Sauvegarder `bibliotheque_data/users.json` (optionnel, pour référence).

2. Supprimer le fichier `bibliotheque_data/users.json`.

3. Redémarrer le serveur web.

- Note : Cela déclenche la recréation automatique du compte Admin par défaut.

4. Demander à tous les utilisateurs de réinscrire leurs comptes via la page `/signup`.
