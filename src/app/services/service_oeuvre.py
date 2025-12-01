# services/service_oeuvre.py
from core.entities import Oeuvre
from infrastructure.repositories import OeuvreRepository # À créer
from core.auth import Utilisateur # À créer

class ServiceOeuvre:
    def __init__(self, repo: OeuvreRepository):
        self.repo = repo # Injection de dépendance

    def soumettre_oeuvre(self, membre: Utilisateur, fichier_path: str, titre: str) -> Oeuvre:
        # Création de l'objet
        nouvelle_oeuvre = Oeuvre(id="uuid_genere", titre=titre, auteur_nom=membre.nom)
        
        # Sauvegarde physique (État initial : Soumise -> dossier "a_moderer")
        self.repo.sauvegarder(nouvelle_oeuvre, dossier="a_moderer")
        
        return nouvelle_oeuvre

    def traiter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str) -> Oeuvre:
        # 1. RBAC Check
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")

        # 2. Chargement
        oeuvre = self.repo.charger(id_oeuvre)

        # 3. Logique Métier (Transition d'état)
        oeuvre.traiter() # Passe à EtatEnTraitement

        # 4. Mise à jour (Optionnel: peut-être déplacer dans un dossier temporaire)
        self.repo.sauvegarder(oeuvre) 
        
        return oeuvre

    def valider_oeuvre(self, biblio: Utilisateur, id_oeuvre: str):
        # 1. RBAC Check
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")

        # 2. Chargement
        oeuvre = self.repo.charger(id_oeuvre)

        # 3. Logique Métier
        oeuvre.accepter() # Passe à EtatValidee

        # 4. Persistance & Infrastructure
        # Le repository s'occupe de déplacer le fichier Git de "a_moderer" vers "fond_commun"
        self.repo.deplacer(oeuvre, dossier_source="a_moderer", dossier_dest="fond_commun")
        
        print(f"Succès : Oeuvre {id_oeuvre} publiée.")