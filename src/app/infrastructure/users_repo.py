# src/app/infrastructure/users_repo.py
import os
import json
from typing import Optional
from core.auth import Utilisateur
from core.roles_config import RoleFactory # Nécessaire pour reconstruire les rôles

class FileSystemUserRepository:
    def __init__(self, base_path: str):
        self.file_path = os.path.join(base_path, "users.json")
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({}, f)

    def sauvegarder(self, user: Utilisateur):
        users_data = self._read_all_data()
        users_data[user.email] = user.to_dict()
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)

    def trouver_par_email(self, email: str) -> Optional[Utilisateur]:
        users_data = self._read_all_data()
        data = users_data.get(email)
        
        if not data:
            return None
            
        user = Utilisateur.from_dict(data)
        
        # Réhydratation des Rôles (Redonner les pouvoirs)
        role_names = data.get("roles", [])
        for role_name in role_names:
            if role_name == "Bibliothecaire":
                user.ajouter_role(RoleFactory.get_role_bibliothecaire())
            elif role_name == "Membre":
                user.ajouter_role(RoleFactory.get_role_membre())
                
        return user

    def _read_all_data(self) -> dict:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}