from typing import Dict, Optional
from core.auth import Utilisateur, RoleFactory

class UserRepositoryInMemory:
    def __init__(self):
        self._users_db: Dict[str, Utilisateur] = {}
        self._init_demo_data()

    def _init_demo_data(self):
        # Créons un Membre standard (Bob)
        bob = Utilisateur(id="u1", nom="Bob le Bricoleur", email="bob@mail.com")
        bob.ajouter_role(RoleFactory.get_role_membre())
        self.sauvegarder(bob)

        # Créons une Bibliothécaire (Alice)
        alice = Utilisateur(id="u2", nom="Alice la Bibliothécaire", email="alice@mail.com")
        alice.ajouter_role(RoleFactory.get_role_bibliothecaire())
        self.sauvegarder(alice)

        # Créons un Invité sans rôle (Charlie)
        charlie = Utilisateur(id="u3", nom="Charlie l'Intrus", email="charlie@hack.com")
        self.sauvegarder(charlie)

    def sauvegarder(self, user: Utilisateur):
        self._users_db[user.email] = user

    def trouver_par_email(self, email: str) -> Optional[Utilisateur]:
        return self._users_db.get(email)