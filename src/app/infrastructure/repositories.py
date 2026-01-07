# src/app/infrastructure/repositories.py
import os
import json
import shutil
from typing import List
from core.ports import OeuvreRepository
from core.entities import Oeuvre
from core.states import EtatSoumise, EtatEnTraitement, EtatValidee, EtatRefusee

class FileSystemOeuvreRepository(OeuvreRepository):
    def __init__(self, base_path: str = "data_repo"):
        self.base_path = base_path
        # Initialisation des dossiers obligatoires
        self.folders = ["a_moderer", "fond_commun", "sequestre", "emprunts", "archives"]
        self._init_folders()

    def _init_folders(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        for folder in self.folders:
            path = os.path.join(self.base_path, folder)
            os.makedirs(path, exist_ok=True)

    def _get_path(self, dossier: str, id_oeuvre: str, extension: str = "json") -> str:
        """Helper pour avoir le chemin du json OU du pdf"""
        return os.path.join(self.base_path, dossier, f"{id_oeuvre}.{extension}")

    def sauvegarder(self, oeuvre, dossier_cible, fichier_binaire=None):
        path_dossier = os.path.join(self.base_path, dossier_cible)
        if not os.path.exists(path_dossier):
            os.makedirs(path_dossier)

        # DEBUG: Let's see what's inside before we fail
        data_to_save = oeuvre.to_dict()
        
        # 1. Save JSON Metadata
        json_path = os.path.join(path_dossier, f"{oeuvre.id}.json")
        try:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=4, ensure_ascii=False)
        except TypeError as e:
            print(f"DEBUG - Dictionary content: {data_to_save}")
            raise TypeError(f"Serialization failed: {e}")

        # 2. Save Binary PDF (Separately)
        if fichier_binaire:
            pdf_path = os.path.join(path_dossier, f"{oeuvre.id}.pdf")
            with open(pdf_path, 'wb') as f:
                # Binary data is written directly to disk, not JSON
                data = fichier_binaire.read() if hasattr(fichier_binaire, 'read') else fichier_binaire
                f.write(data)

    def charger(self, id_oeuvre: str, dossier_source: str) -> Oeuvre:
        filepath = self._get_path(dossier_source, id_oeuvre, "json")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Oeuvre {id_oeuvre} introuvable dans {dossier_source}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        oeuvre = Oeuvre.from_dict(data)
        
        # Reconstruction dynamique de l'État (Magie du Pattern State)
        etat_nom = data.get("etat_classe", "EtatSoumise")
        if etat_nom == "EtatEnTraitement":
            oeuvre.set_etat(EtatEnTraitement())
        elif etat_nom == "EtatValidee":
            oeuvre.set_etat(EtatValidee())
        elif etat_nom == "EtatRefusee":
            oeuvre.set_etat(EtatRefusee())
        else:
            oeuvre.set_etat(EtatSoumise())
            
        return oeuvre

    def deplacer(self, oeuvre: Oeuvre, dossier_source: str, dossier_dest: str) -> None:
        # 1. Déplacement du JSON
        src_json = self._get_path(dossier_source, oeuvre.id, "json")
        dest_json = self._get_path(dossier_dest, oeuvre.id, "json")
        
        # 2. Déplacement du PDF
        src_pdf = self._get_path(dossier_source, oeuvre.id, "pdf")
        dest_pdf = self._get_path(dossier_dest, oeuvre.id, "pdf")
        
        if not os.path.exists(src_json):
            raise FileNotFoundError(f"Source introuvable {src_json}")

        # On met à jour le JSON avant de déplacer (pour l'état validé)
        self.sauvegarder(oeuvre, dossier_source)
        
        # Déplacement physique
        shutil.move(src_json, dest_json)
        
        # On déplace le PDF s'il existe
        if os.path.exists(src_pdf):
            shutil.move(src_pdf, dest_pdf)
            print(f"[DISK] PDF déplacé de {dossier_source} vers {dossier_dest}")
        else:
            print(f"[WARN] Pas de PDF trouvé pour {oeuvre.id}")

    def lister_ids(self, dossier: str) -> List[str]:
        path = os.path.join(self.base_path, dossier)
        if not os.path.exists(path):
            return []
        # On retourne juste les IDs (nom du fichier sans .json)
        return [f.replace(".json", "") for f in os.listdir(path) if f.endswith(".json")]