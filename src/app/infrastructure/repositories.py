import os
import json
import shutil
from typing import List
from core.ports import OeuvreRepository
from core.entities import Oeuvre
# Import des états pour la reconstruction
from core.states import EtatSoumise, EtatEnTraitement, EtatValidee, EtatRefusee


class FileSystemOeuvreRepository(OeuvreRepository):
  def __init__(self, base_path: str = "data_repo"):
    self.base_path = base_path
    # Initialisation des dossiers obligatoires du sujet
    self.folders = ["a_moderer", "fond_commun", "sequestre", "emprunts", "archives"]
    self._init_folders()