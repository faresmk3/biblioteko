import os
import json
from typing import Optional
from core.auth import Utilisateur

class FileSystemUserRepository:
    def __init__(self, base_path: str):
        self.base_path = base_path
        # On stocke tous les utilisateurs dans un seul fichier JSON pour simplifier
        self.users_file = os.path.join(base_path, "users.json")
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Crée le fichier users.json s'il n'existe pas"""
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)

    def _load_db(self):
        """Charge le contenu du JSON"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_db(self, data):
        """Sauvegarde le dictionnaire dans le JSON"""
        with open(self.users_file, 'w') as f:
            json.dump(data, f, indent=4)

    def sauvegarder(self, utilisateur: Utilisateur):
        """Enregistre ou met à jour un utilisateur"""
        db = self._load_db()
        # On utilise l'ID comme clé
        db[utilisateur.id] = utilisateur.to_dict()
        self._save_db(db)

    def trouver_par_email(self, email: str) -> Optional[Utilisateur]:
        """Cherche un utilisateur par son email"""
        db = self._load_db()
        for user_data in db.values():
            if user_data.get('email') == email:
                return Utilisateur.from_dict(user_data)
        return None

    def trouver_par_id(self, user_id: str) -> Optional[Utilisateur]:
        """
        [CETTE MÉTHODE MANQUAIT]
        Récupère un utilisateur par son ID unique.
        Utilisé pour reconnecter l'utilisateur depuis sa session.
        """
        db = self._load_db()
        user_data = db.get(user_id)
        
        if user_data:
            return Utilisateur.from_dict(user_data)
        return None