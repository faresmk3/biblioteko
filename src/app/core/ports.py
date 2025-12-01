from abc import ABC, abstractmethod
from typing import List
from core.entities import Oeuvre

class OeuvreRepository(ABC):
    """
    Interface (Port) que l'infrastructure devra respecter.
    Le ServiceOeuvre ne connaîtra que ça.
    """
    
    @abstractmethod
    def sauvegarder(self, oeuvre: Oeuvre, dossier_cible: str) -> None:
        """Sauvegarde ou met à jour une œuvre dans un dossier spécifique"""
        pass

    @abstractmethod
    def charger(self, id_oeuvre: str, dossier_source: str) -> Oeuvre:
        """Récupère une œuvre depuis un dossier"""
        pass

    @abstractmethod
    def deplacer(self, oeuvre: Oeuvre, dossier_source: str, dossier_dest: str) -> None:
        """Déplace physiquement le fichier d'un dossier à un autre (ex: Validation)"""
        pass
    
    @abstractmethod
    def lister_ids(self, dossier: str) -> List[str]:
        """Liste les IDs présents dans un dossier"""
        pass