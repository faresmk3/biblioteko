class RoleFactory:
    @staticmethod
    def get_role_membre() -> Role:
        # Un membre peut seulement proposer et emprunter
        p_proposer = Permission("peut_proposer_oeuvre", "Droit de soumettre un PDF")
        p_emprunter = Permission("peut_emprunter", "Droit de louer une œuvre")
        
        role = Role(nom="Membre")
        role.ajouter_permission(p_proposer)
        role.ajouter_permission(p_emprunter)
        return role

    @staticmethod
    def get_role_bibliothecaire() -> Role:
        # Un bibliothécaire a tout ce qu'un membre a, PLUS la modération
        role = Role(nom="Bibliothecaire")
        
        # On récupère les droits de base (optionnel, selon votre règle métier)
        role_membre = RoleFactory.get_role_membre()
        for p in role_membre.permissions:
            role.ajouter_permission(p)
            
        # On ajoute les droits spécifiques
        role.ajouter_permission(Permission("peut_moderer_oeuvre", "Valider ou rejeter"))
        role.ajouter_permission(Permission("peut_enrichir_metadata", "Modifier titre/auteur"))
        
        return role