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
    roles: List[Role] = field(default_factory=list)

    def ajouter_role(self, role: Role):
        if role not in self.roles:
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

    def __repr__(self):
        roles_str = ", ".join([r.nom for r in self.roles])
        return f"<Utilisateur {self.nom} (Rôles: {roles_str})>"