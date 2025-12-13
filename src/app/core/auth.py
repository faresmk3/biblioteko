from dataclasses import dataclass, field
from typing import List, Set

@dataclass(frozen=True) # frozen=True rend l'objet immuable (Value Object)
class Permission:
    nom: str
    description: str = ""

@dataclass
class Role:
    nom: str
    permissions: Set[Permission] = field(default_factory=set)

    def ajouter_permission(self, permission: Permission):
        self.permissions.add(permission)

@dataclass
class Utilisateur:
    id: str
    nom: str
    email: str
    # On stocke le mot de passe (en clair pour ce MVP, à hasher en prod)
    mot_de_passe: str
    roles: List[Role] = field(default_factory=list)

    def ajouter_role(self, role: Role):
        # On évite les doublons de rôles
        if not any(r.nom == role.nom for r in self.roles):
            self.roles.append(role)

    def a_la_permission(self, nom_permission_requise: str) -> bool:
        """
        C'est le cœur du RBAC.
        On parcourt tous les rôles de l'utilisateur.
        Si l'un des rôles contient la permission demandée, c'est gagné.
        """
        for role in self.roles:
            for permission in role.permissions:
                if permission.nom == nom_permission_requise:
                    return True
        return False
    # --- SERIALIZATION POUR SAUVEGARDE JSON ---
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "mot_de_passe": self.mot_de_passe,
            # On ne sauvegarde que le nom des rôles
            "roles": [r.nom for r in self.roles]
        }

    @staticmethod
    def from_dict(data: dict) -> 'Utilisateur':
        u = Utilisateur(
            id=data["id"],
            nom=data["nom"],
            email=data["email"],
            mot_de_passe=data.get("mot_de_passe", "")
        )
        # La réhydratation des rôles se fera via le Repository ou le Service
        # car RoleFactory est dans un autre module (éviter import circulaire)
        return u
    def __repr__(self):
        roles_str = ", ".join([r.nom for r in self.roles])
        return f"<Utilisateur {self.nom} (Rôles: {roles_str})>"