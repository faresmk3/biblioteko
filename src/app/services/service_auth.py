# src/app/services/service_auth.py
import hashlib
import uuid
from core.auth import Utilisateur, Role # Import de Role nécessaire

class ServiceAuth:
    def __init__(self, repo):
        self.repo = repo

    def _hacher(self, mot_de_passe: str) -> str:
        return hashlib.sha256(mot_de_passe.encode()).hexdigest()

    def inscrire_membre(self, nom, email, mot_de_passe):
        if self.repo.trouver_par_email(email):
            raise ValueError("Cet email est déjà utilisé.")
        
        # Création de l'objet Role
        role_membre = Role(nom="membre")
        
        nouveau_membre = Utilisateur(
            id=str(uuid.uuid4())[:8],
            nom=nom,
            email=email,
            mot_de_passe_hache=self._hacher(mot_de_passe),
            roles=[role_membre], # On passe une liste contenant l'objet Role
            permissions=["peut_proposer_oeuvre"]
        )
        
        self.repo.sauvegarder(nouveau_membre)
        return nouveau_membre

    def identifier_utilisateur(self, email, mot_de_passe):
        user = self.repo.trouver_par_email(email)
        if user and user.mot_de_passe_hache == self._hacher(mot_de_passe):
            return user
        return None

    def ensure_admin_exists(self):
        if not self.repo.trouver_par_email("admin@biblio.com"):
            print("⚠️ Création du compte ADMIN par défaut...")
            
            # Création de l'objet Role Admin
            role_admin = Role(nom="admin")
            
            admin = Utilisateur(
                id="admin_id",
                nom="Administrateur",
                email="admin@biblio.com",
                mot_de_passe_hache=self._hacher("admin123"),
                roles=[role_admin], # Liste d'objets Role
                permissions=["peut_moderer_oeuvre", "peut_proposer_oeuvre"]
            )
            self.repo.sauvegarder(admin)