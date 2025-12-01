from abc import ABC, abstractmethod

class EtatOeuvre(ABC):
    """Interface du State Pattern"""
    
    @abstractmethod
    def traiter(self, oeuvre) -> None:
        pass

    @abstractmethod
    def accepter(self, oeuvre) -> None:
        pass

    @abstractmethod
    def refuser(self, oeuvre) -> None:
        pass


class EtatSoumise(EtatOeuvre):
    def traiter(self, oeuvre) -> None:
        print(f"Log: Transition de {oeuvre.titre} vers EN TRAITEMENT")
        # On change l'état de l'objet contexte
        oeuvre.set_etat(EtatEnTraitement())

    def accepter(self, oeuvre) -> None:
        raise PermissionError("Impossible d'accepter une œuvre qui n'est pas 'En Traitement'")

    def refuser(self, oeuvre) -> None:
        raise PermissionError("Impossible de refuser une œuvre qui n'est pas 'En Traitement'")

class EtatEnTraitement(EtatOeuvre):
    def traiter(self, oeuvre) -> None:
        print("L'œuvre est déjà en cours de traitement.")

    def accepter(self, oeuvre) -> None:
        print(f"Log: Validation de {oeuvre.titre}. Passage en VALIDÉE.")
        oeuvre.set_etat(EtatValidee())

    def refuser(self, oeuvre) -> None:
        print(f"Log: Rejet de {oeuvre.titre}. Passage en REFUSÉE.")
        oeuvre.set_etat(EtatRefusee())

class EtatValidee(EtatOeuvre):
    def traiter(self, oeuvre) -> None: pass # Ou erreur
    def accepter(self, oeuvre) -> None: pass
    def refuser(self, oeuvre) -> None: pass

class EtatRefusee(EtatOeuvre):
    def traiter(self, oeuvre) -> None: pass
    def accepter(self, oeuvre) -> None: pass
    def refuser(self, oeuvre) -> None: pass