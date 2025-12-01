from datetime import date
from typing import Optional, List
from core.states import EtatOeuvre, EtatSoumise
import json

class Oeuvre:
    def __init__(self, id: str, titre: str, auteur_nom: str):
        self.id = id
        self.titre = titre
        self.auteur_nom = auteur_nom
        self.date_publication = date.today()
        # État initial défini par le constructeur
        self._etat: EtatOeuvre = EtatSoumise()
        self.metadata: dict = {}
    def to_dict(self) -> dict:
        """Convertit l'objet en dictionnaire pour le JSON"""
        return {
            "id": self.id,
            "titre": self.titre,
            "auteur_nom": self.auteur_nom,
            "date_publication": str(self.date_publication),
            "etat_classe": self._etat.__class__.__name__, # On sauvegarde le nom de l'état
            "metadata": self.metadata
        }
    def set_etat(self, nouvel_etat: EtatOeuvre):
        self._etat = nouvel_etat

    # Délégation (Pattern State)
    def traiter(self):
        self._etat.traiter(self)

    def accepter(self):
        self._etat.accepter(self)

    def refuser(self):
        self._etat.refuser(self)
    
    def set_infos(self, metadata: dict):
        self.metadata.update(metadata)
        
    def __repr__(self):
        return f"<Oeuvre {self.titre} [{self._etat.__class__.__name__}]>"