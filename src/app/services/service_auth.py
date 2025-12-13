# src/app/services/service_auth.py
import uuid
from core.auth import Utilisateur
from core.roles_config import RoleFactory
from infrastructure.users_repo import FileSystemUserRepository

class ServiceAuth:
    def __init__(self, repo: FileSystemUserRepository):
        self.repo = repo

    def identifier_utilisateur(self, email: str, mot_de_passe: str) -> Utilisateur:
        """Retourne l'utilisateur si login OK, sinon None"""
        user = self.repo.trouver_par_email(email)
        if user and user.mot_de_passe == mot_de_passe:
            return user
        return None

    def inscrire_membre(self, nom: str, email: str, mot_de_passe: str) -> Utilisateur:
        if self.repo.trouver_par_email(email):
            raise ValueError("Cet email est déjà utilisé.")
            
        nouveau_membre = Utilisateur(
            id=str(uuid.uuid4())[:8],
            nom=nom,
            email=email,
            mot_de_passe=mot_de_passe
        )
        nouveau_membre.ajouter_role(RoleFactory.get_role_membre())
        self.repo.sauvegarder(nouveau_membre)
        return nouveau_membre

    def ensure_admin_exists(self):
        """Crée le compte root si inexistant (Requirement: main moderator by default)"""
        email_admin = "admin@biblio.com"
        if not self.repo.trouver_par_email(email_admin):
            print("⚠️ Création du compte ADMIN par défaut...")
            admin = Utilisateur(
                id="root",
                nom="Administrateur",
                email=email_admin,
                mot_de_passe="admin123" # Mot de passe par défaut
            )
            admin.ajouter_role(RoleFactory.get_role_bibliothecaire())
            self.repo.sauvegarder(admin)