# src/app/services/service_oeuvre.py
import uuid
import io
from datetime import datetime
from typing import List

from core.entities import Oeuvre
from core.auth import Utilisateur
from core.ports import OeuvreRepository
from infrastructure.ai_adapters import GeminiAdapter

class ServiceOeuvre:
    def __init__(self, repo: OeuvreRepository):
        self.repo = repo
        try:
            self.ocr_provider = GeminiAdapter()
            print("✅ AI Adapter (Gemini) loaded.")
        except Exception as e:
            print(f"⚠️ Warning: AI Adapter failed to load ({e}). OCR will be disabled.")
            self.ocr_provider = None

    def soumettre_oeuvre(self, membre: Utilisateur, titre_form: str, auteur_form: str, categories: List[str], fichier_stream=None) -> Oeuvre:
        if not membre.a_la_permission("peut_proposer_oeuvre"):
            raise PermissionError("Access denied.")

        # 1. Create a clean entity with primitive types only
        nouvelle_oeuvre = Oeuvre(
            id=str(uuid.uuid4())[:8], 
            titre=str(titre_form), 
            auteur_nom=str(auteur_form),
            categories=list(categories)
        )
        
        # Binary data is kept strictly separate from the object
        file_bytes = None
        if fichier_stream is not None:
            file_bytes = fichier_stream.read()

        if file_bytes and self.ocr_provider:
            try:
                # Use a memory stream for the AI analysis
                analyse = self.ocr_provider.analyser_oeuvre(io.BytesIO(file_bytes))
                
                # Assign ONLY text/primitive data to the entity
                nouvelle_oeuvre.contenu_markdown = str(analyse.get("contenu_markdown", ""))
                nouvelle_oeuvre.titre = str(analyse.get("titre", nouvelle_oeuvre.titre))
                nouvelle_oeuvre.auteur_nom = str(analyse.get("auteur", nouvelle_oeuvre.auteur_nom))
                nouvelle_oeuvre.date_publication = str(analyse.get("date_publication", "2024"))
                nouvelle_oeuvre.est_domaine_public = bool(analyse.get("est_domaine_public", False))
                
                # Ensure metadata dictionary is clean
                nouvelle_oeuvre.set_infos({
                    "ai_analysis": True,
                    "ai_reason": str(analyse.get("raison", "Analyse effectuée"))
                })
            except Exception as e:
                print(f"❌ AI Error: {e}")

        # Pass the raw bytes in a fresh BytesIO to the repository
        binary_to_save = io.BytesIO(file_bytes) if file_bytes else None
        
        self.repo.sauvegarder(
            nouvelle_oeuvre, 
            dossier_cible="a_moderer", 
            fichier_binaire=binary_to_save
        )
        return nouvelle_oeuvre
    def lister_a_moderer(self, demandeur: Utilisateur) -> List[Oeuvre]:
        if not demandeur.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Access denied.")
            
        ids = self.repo.lister_ids("a_moderer")
        oeuvres = []
        for id_o in ids:
            try:
                # We try to load the work
                oeuvre = self.repo.charger(id_o, "a_moderer")
                oeuvres.append(oeuvre)
            except Exception as e:
                # If a file is corrupt, we print the error but DO NOT stop the application
                print(f"⚠️ Corrupt file found ({id_o}): {e}. Skipping.")
                continue 
        return oeuvres

    def lister_publiques(self) -> List[Oeuvre]:
        ids = self.repo.lister_ids("fond_commun")
        return [self.repo.charger(id_o, "fond_commun") for id_o in ids]

    def lister_sequestre(self) -> List[Oeuvre]:
        ids = self.repo.lister_ids("sequestre")
        return [self.repo.charger(id_o, "sequestre") for id_o in ids]

    def valider_oeuvre(self, bibliothecaire: Utilisateur, id_oeuvre: str, est_domaine_public: bool,
                       nouveau_titre: str = None, nouveau_auteur: str = None, nouvelles_categories: List[str] = None):
        
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Access denied.")

        oeuvre = self.repo.charger(id_oeuvre, dossier_source="a_moderer")
        
        # Enrichment
        if nouveau_titre: oeuvre.titre = nouveau_titre
        if nouveau_auteur: oeuvre.auteur_nom = nouveau_auteur
        if nouvelles_categories is not None: oeuvre.categories = nouvelles_categories
        
        # Rights & State
        oeuvre.est_domaine_public = est_domaine_public
        try:
            oeuvre.traiter()
            oeuvre.accepter()
        except Exception: pass

        dossier_dest = "fond_commun" if est_domaine_public else "sequestre"
        self.repo.deplacer(oeuvre, dossier_source="a_moderer", dossier_dest=dossier_dest)
        print(f"✅ Validated: {oeuvre.titre} -> {dossier_dest}")

    def rejeter_oeuvre(self, bibliothecaire: Utilisateur, id_oeuvre: str):
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Access denied.")
        oeuvre = self.repo.charger(id_oeuvre, dossier_source="a_moderer")
        try:
            oeuvre.traiter()
            oeuvre.refuser()
        except Exception: pass
        self.repo.deplacer(oeuvre, dossier_source="a_moderer", dossier_dest="archives")

    # --- THIS WAS MISSING ---
    def verifier_expiration_droits(self):
        """
        Scans 'sequestre' and moves works > 70 years old to 'fond_commun'.
        """
        print("--- 🕒 Running Automatic Rights Check ---")
        
        ids = self.repo.lister_ids("sequestre")
        current_year = datetime.now().year
        moved_count = 0
        
        for id_o in ids:
            try:
                oeuvre = self.repo.charger(id_o, "sequestre")
                
                # Extract year safely (Handling YYYY-MM-DD)
                pub_year_str = oeuvre.date_publication[:4]
                if pub_year_str.isdigit():
                    pub_year = int(pub_year_str)
                    
                    # 70-year rule
                    if (current_year - pub_year) > 70:
                        print(f"🔓 Rights expired for '{oeuvre.titre}' ({pub_year}). Moving to Public Domain.")
                        
                        oeuvre.est_domaine_public = True
                        self.repo.sauvegarder(oeuvre, "sequestre") # Save metadata update first
                        self.repo.deplacer(oeuvre, "sequestre", "fond_commun")
                        moved_count += 1
            except Exception as e:
                print(f"Error checking rights for {id_o}: {e}")
                
        print(f"--- Check Complete. {moved_count} works moved. ---")