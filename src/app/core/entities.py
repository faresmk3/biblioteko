from dataclasses import dataclass, field
from datetime import date
from core.states import EtatOeuvre, EtatSoumise
import json

@dataclass
class Oeuvre:
    id: str
    titre: str
    auteur_nom: str
    date_publication: str = field(default_factory=lambda: str(date.today()))
    contenu_markdown: str = ""        # Stores the AI output
    est_domaine_public: bool = False  # Rights management
    _etat: EtatOeuvre = field(default_factory=EtatSoumise)
    metadata: dict = field(default_factory=dict)

    def set_etat(self, nouvel_etat: EtatOeuvre):
        self._etat = nouvel_etat

    def traiter(self): self._etat.traiter(self)
    def accepter(self): self._etat.accepter(self)
    def refuser(self): self._etat.refuser(self)
    
    def set_infos(self, metadata: dict):
        self.metadata.update(metadata)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "titre": self.titre,
            "auteur_nom": self.auteur_nom,
            "date_publication": self.date_publication,
            "etat_classe": self._etat.__class__.__name__,
            "contenu_markdown": self.contenu_markdown,
            "est_domaine_public": self.est_domaine_public,
            "metadata": self.metadata
        }

    @staticmethod
    def from_dict(data: dict) -> 'Oeuvre':
        oeuvre = Oeuvre(
            id=data["id"], 
            titre=data["titre"], 
            auteur_nom=data["auteur_nom"]
        )
        oeuvre.date_publication = data.get("date_publication", str(date.today()))
        oeuvre.contenu_markdown = data.get("contenu_markdown", "")
        oeuvre.est_domaine_public = data.get("est_domaine_public", False)
        oeuvre.metadata = data.get("metadata", {})
        return oeuvre