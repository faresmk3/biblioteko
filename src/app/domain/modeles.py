from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict

# ============================================================
# 1. GESTION DES UTILISATEURS & DROITS (RBAC)
# ============================================================

class Permission:
    def __init__(self, nom_permission: str):
        self.nom_permission = nom_permission

    def __repr__(self):
        return f"<Permission {self.nom_permission}>"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.nom_permission == other
        return self.nom_permission == other.nom_permission

class Role:
    def __init__(self, nom_role: str):
        self.nom_role = nom_role
        self.permissions: List[Permission] = []

    def ajouter_permission(self, permission: Permission):
        self.permissions.append(permission)

class Utilisateur:
    def __init__(self, nom: str, prenom: str, email: str, mdp: str):
        # Attention à l'ordre des arguments ici pour correspondre à votre test
        self.nom = nom
        self.prenom = prenom
        self.email = email # On utilise 'email' pour être cohérent avec le repo
        self.courriel = email # Alias si besoin
        self.mdp = mdp
        self.roles: List[Role] = []

    def ajouter_role(self, role: Role):
        self.roles.append(role)

    def a_la_permission(self, nom_perm: str) -> bool:
        for role in self.roles:
            for perm in role.permissions:
                if perm.nom_permission == nom_perm:
                    return True
        return False

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"


# ============================================================
# 2. PATTERN STATE (États de l'Oeuvre)
# ============================================================

class EtatOeuvre(ABC):
    @property
    @abstractmethod
    def nom(self) -> str:
        pass

    def traiter(self, oeuvre) -> None:
        raise PermissionError(f"Action 'traiter' impossible depuis l'état {self.nom}")

    def accepter(self, oeuvre) -> None:
        raise PermissionError(f"Action 'accepter' impossible depuis l'état {self.nom}")

    def refuser(self, oeuvre) -> None:
        raise PermissionError(f"Action 'refuser' impossible depuis l'état {self.nom}")

    def __repr__(self):
        return self.nom

class EtatSoumise(EtatOeuvre):
    nom = "SOUMISE"
    def traiter(self, oeuvre):
        oeuvre.changer_etat(EtatEnTraitement())

class EtatEnTraitement(EtatOeuvre):
    nom = "EN_TRAITEMENT"
    def accepter(self, oeuvre):
        oeuvre.changer_etat(EtatValidee())
    def refuser(self, oeuvre):
        oeuvre.changer_etat(EtatRefusee())

class EtatValidee(EtatOeuvre):
    nom = "VALIDEE"

class EtatRefusee(EtatOeuvre):
    nom = "REFUSEE"


# ============================================================
# 3. DOMAINE MÉTIER : L'ŒUVRE
# ============================================================

class Oeuvre:
    def __init__(self, titre: str, auteur: str, fichier_nom: str, soumis_par: Utilisateur):
        self.id = None
        self.titre = titre
        self.auteur = auteur          # Le repo attend 'auteur'
        self.fichier_nom = fichier_nom # Le repo attend 'fichier_nom' (ou mappé vers 'fichier')
        
        # Gestion de l'email de l'utilisateur
        self.soumis_par_email = soumis_par.email if hasattr(soumis_par, 'email') else str(soumis_par)
        
        self.date_soumission = datetime.now().isoformat()
        
        # État interne (privé)
        self._etat_actuel: EtatOeuvre = EtatSoumise()
        
        self.metadonnees: Dict = {}

    # --- La fameuse propriété qui manquait ---
    @property
    def etat(self):
        return self._etat_actuel

    def changer_etat(self, nouvel_etat: EtatOeuvre):
        print(f"[State] Oeuvre '{self.titre}' : {self._etat_actuel.nom} -> {nouvel_etat.nom}")
        self._etat_actuel = nouvel_etat

    def set_metadonnee(self, cle: str, valeur: str):
        self.metadonnees[cle] = valeur

    # --- Méthodes Métier ---
    def traiter(self):
        self._etat_actuel.traiter(self)

    def accepter(self):
        self._etat_actuel.accepter(self)

    def valider(self): # Alias pour accepter
        self.accepter()

    def refuser(self):
        self._etat_actuel.refuser(self)

    def __repr__(self):
        return f"<Oeuvre '{self.titre}' [{self._etat_actuel.nom}]>"