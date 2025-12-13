from typing import List
import uuid
import io

from core.entities import Oeuvre
from core.auth import Utilisateur
from core.ports import OeuvreRepository
from infrastructure.ai_adapters import GeminiAdapter  # Import real adapter

class ServiceOeuvre:
    def __init__(self, repo: OeuvreRepository):
        self.repo = repo
        # Initialize AI Adapter (will load API Key)
        try:
            self.ocr_provider = GeminiAdapter()
            print("✅ AI Adapter (Gemini) loaded.")
        except Exception as e:
            print(f"⚠️ Warning: AI Adapter failed to load ({e}). OCR will be disabled.")
            self.ocr_provider = None

    def soumettre_oeuvre(self, membre: Utilisateur, titre: str, auteur: str, fichier_stream=None) -> Oeuvre:
        if not membre.a_la_permission("peut_proposer_oeuvre"):
            raise PermissionError(f"User {membre.nom} cannot submit works.")

        nouvelle_oeuvre = Oeuvre(id=str(uuid.uuid4())[:8], titre=titre, auteur_nom=auteur)
        
        # --- AI PROCESS START ---
        if fichier_stream and self.ocr_provider:
            print(f"🤖 Sending '{titre}' to Gemini for OCR...")
            
            # Read bytes into memory to safely use stream twice (once for AI, once for Disk)
            if hasattr(fichier_stream, 'seek'): fichier_stream.seek(0)
            file_bytes = fichier_stream.read()
            
            # 1. OCR
            # Create a bytes stream for the AI
            try:
                ai_stream = io.BytesIO(file_bytes)
                md_text = self.ocr_provider.extraire_texte(ai_stream)
                nouvelle_oeuvre.contenu_markdown = md_text
                print("✅ OCR Complete.")
            except Exception as e:
                print(f"❌ OCR Failed: {e}")
                nouvelle_oeuvre.contenu_markdown = "OCR Failed or Unavailable."

            # 2. Reset stream for disk saving
            # Create a new bytes stream for the repository
            save_stream = io.BytesIO(file_bytes)
        else:
            save_stream = fichier_stream
        # --- AI PROCESS END ---

        self.repo.sauvegarder(nouvelle_oeuvre, dossier_cible="a_moderer", fichier_binaire=save_stream)
        return nouvelle_oeuvre

    def lister_a_moderer(self, demandeur: Utilisateur) -> List[Oeuvre]:
        if not demandeur.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Access denied.")
        ids = self.repo.lister_ids("a_moderer")
        oeuvres = []
        for id_o in ids:
            try:
                oeuvres.append(self.repo.charger(id_o, "a_moderer"))
            except FileNotFoundError: continue
        return oeuvres

    def valider_oeuvre(self, bibliothecaire: Utilisateur, id_oeuvre: str, est_domaine_public: bool,
                        nouveau_titre: str = None, nouveau_auteur: str = None):
        
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Access denied.")

        oeuvre = self.repo.charger(id_oeuvre, dossier_source="a_moderer")
        
        # 1. ENRICHMENT (Requirement: "enrichissement des métadonnées")
        if nouveau_titre: oeuvre.titre = nouveau_titre
        if nouveau_auteur: oeuvre.auteur_nom = nouveau_auteur
        
        # 2. Update Rights
        oeuvre.est_domaine_public = est_domaine_public
        
        # 3. State Transition
        try:
            oeuvre.traiter()
            oeuvre.accepter()
        except Exception: pass

        # 4. Move
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
    def lister_publiques(self) -> List[Oeuvre]:
        """Returns works in 'fond_commun' (Free Access)"""
        ids = self.repo.lister_ids("fond_commun")
        return [self.repo.charger(id_o, "fond_commun") for id_o in ids]

    def lister_sequestre(self) -> List[Oeuvre]:
        """Returns works in 'sequestre' (Available for Loan)"""
        ids = self.repo.lister_ids("sequestre")
        return [self.repo.charger(id_o, "sequestre") for id_o in ids]