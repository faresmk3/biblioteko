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
    mot_de_passe_hache: str
    roles: List[Role] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

    def ajouter_role(self, role: Role):
        # On évite les doublons de rôles
        if not any(r.nom == role.nom for r in self.roles):
            self.roles.append(role)

    def a_la_permission(self, permission: str) -> bool:
        """ Vérifie si l'utilisateur a une permission spécifique. """
        return permission in self.permissions
    # --- SERIALIZATION POUR SAUVEGARDE JSON ---
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "mot_de_passe_hache": self.mot_de_passe_hache,
            # On sauvegarde la liste des noms des rôles
            "roles": [r.nom for r in self.roles], 
            "permissions": self.permissions
        }

    @classmethod
    def from_dict(cls, data: dict):
        # On reconstruit les objets Role à partir des chaînes
        roles_names = data.get("roles", [])
        roles_objects = [Role(nom=r_name) for r_name in roles_names]
        
        return cls(
            id=data.get("id"),
            nom=data.get("nom"),
            email=data.get("email"),
            mot_de_passe_hache=data.get("mot_de_passe_hache"),
            roles=roles_objects, # On passe bien la liste d'objets attendue par le dataclass
            permissions=data.get("permissions", [])
        )
    def __repr__(self):
        roles_str = ", ".join([r.nom for r in self.roles])
        return f"<Utilisateur {self.nom} (Rôles: {roles_str})>"