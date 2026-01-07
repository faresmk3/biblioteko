from dataclasses import dataclass, field
from datetime import date
from typing import List
from core.states import EtatOeuvre, EtatSoumise

@dataclass
class Oeuvre:
    id: str
    titre: str
    auteur_nom: str
    categories: List[str] = field(default_factory=list) # NEW: Categories
    date_publication: str = field(default_factory=lambda: str(date.today()))
    contenu_markdown: str = ""
    est_domaine_public: bool = False
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
            "id": str(self.id),
            "titre": str(self.titre),
            "auteur_nom": str(self.auteur_nom),
            "categories": list(self.categories),
            "date_publication": str(self.date_publication),
            "etat_classe": str(self._etat.__class__.__name__),
            "contenu_markdown": str(self.contenu_markdown),
            "est_domaine_public": bool(self.est_domaine_public),
            "metadata": self.metadata  # Ensure metadata only contains strings/bools
        }
    @staticmethod
    def from_dict(data: dict) -> 'Oeuvre':
        oeuvre = Oeuvre(
            id=data["id"], 
            titre=data["titre"], 
            auteur_nom=data["auteur_nom"]
        )
        oeuvre.categories = data.get("categories", []) # NEW
        oeuvre.date_publication = data.get("date_publication", str(date.today()))
        oeuvre.contenu_markdown = data.get("contenu_markdown", "")
        oeuvre.est_domaine_public = data.get("est_domaine_public", False)
        oeuvre.metadata = data.get("metadata", {})
        return oeuvre