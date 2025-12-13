# src/app/services/service_oeuvre.py
from typing import List
from core.entities import Oeuvre
from core.auth import Utilisateur
from core.ports import OeuvreRepository
import uuid

class ServiceOeuvre:
    def __init__(self, repo: OeuvreRepository):
        self.repo = repo

    # CORRECTION ICI : Ajout du paramètre 'fichier_stream=None'
    def soumettre_oeuvre(self, membre: Utilisateur, titre: str, auteur: str, fichier_stream=None) -> Oeuvre:
        print(f"--- Service: Tentative de soumission par {membre.nom} ---")
        
        # 1. Vérification Sécurité (RBAC)
        if not membre.a_la_permission("peut_proposer_oeuvre"):
            raise PermissionError(f"L'utilisateur {membre.nom} n'a pas le droit de soumettre.")

        # 2. Création du Domaine
        # On génère un ID unique court (8 caractères)
        nouvelle_oeuvre = Oeuvre(id=str(uuid.uuid4())[:8], titre=titre, auteur_nom=auteur)
        
        # 3. Persistance (Infrastructure)
        # On passe le fichier binaire au repository
        self.repo.sauvegarder(nouvelle_oeuvre, dossier_cible="a_moderer", fichier_binaire=fichier_stream)
        
        print(f"✅ Œuvre '{titre}' soumise avec succès (ID: {nouvelle_oeuvre.id})")
        return nouvelle_oeuvre

    def lister_a_moderer(self, demandeur: Utilisateur) -> List[Oeuvre]:
        # 1. RBAC
        if not demandeur.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé aux œuvres à modérer.")
            
        # 2. Infra
        ids = self.repo.lister_ids("a_moderer")
        oeuvres = []
        for id_o in ids:
            try:
                oeuvres.append(self.repo.charger(id_o, "a_moderer"))
            except FileNotFoundError:
                continue
            
        return oeuvres

    def valider_oeuvre(self, bibliothecaire: Utilisateur, id_oeuvre: str):
        print(f"--- Service: Validation de l'œuvre {id_oeuvre} par {bibliothecaire.nom} ---")

        # 1. RBAC
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Seuls les bibliothécaires peuvent valider.")

        # 2. Chargement (Infra)
        oeuvre = self.repo.charger(id_oeuvre, dossier_source="a_moderer")

        # 3. Logique Métier (Domaine / State Pattern)
        try:
            oeuvre.traiter()   # State: Soumise -> EnTraitement
            oeuvre.accepter()  # State: EnTraitement -> Validee
        except Exception as e:
            print(f"❌ Erreur métier : {e}")
            raise e

        # 4. Persistance & Déplacement (Infra)
        self.repo.deplacer(oeuvre, dossier_source="a_moderer", dossier_dest="fond_commun")
        
        print(f"✅ Œuvre validée et publiée dans le Fond Commun !")
    def rejeter_oeuvre(self, bibliothecaire: Utilisateur, id_oeuvre: str):
        print(f"--- Service: Rejet de l'œuvre {id_oeuvre} par {bibliothecaire.nom} ---")

        # 1. RBAC
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Seuls les bibliothécaires peuvent rejeter.")

        # 2. Chargement
        oeuvre = self.repo.charger(id_oeuvre, dossier_source="a_moderer")

        # 3. Logique Métier (Pattern State)
        try:
            oeuvre.traiter()   # Soumise -> EnTraitement
            oeuvre.refuser()   # EnTraitement -> Refusee
        except Exception as e:
            print(f"❌ Erreur métier : {e}")
            raise e

        # 4. Persistance & Archivage
        # On déplace le fichier hors de la vue "à modérer" vers "archives"
        self.repo.deplacer(oeuvre, dossier_source="a_moderer", dossier_dest="archives")
        
        print(f"✅ Œuvre rejetée et archivée.")