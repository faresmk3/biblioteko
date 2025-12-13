# test_storage.py
from infrastructure.repositories import FileSystemOeuvreRepository
from core.entities import Oeuvre
from core.states import EtatEnTraitement

def test_infrastructure():
    print("=== TEST INFRASTRUCTURE (FICHIERS) ===")
    
    # 1. Initialisation
    repo = FileSystemOeuvreRepository(base_path="test_data_repo")
    
    # 2. Création d'une œuvre dummy
    oeuvre = Oeuvre(id="livre_123", titre="Les Misérables", auteur_nom="Victor Hugo")
    print(f"1. Création objet : {oeuvre}")

    # 3. Sauvegarde dans 'a_moderer'
    repo.sauvegarder(oeuvre, "a_moderer")
    
    # 4. Simulation : Un bibliothécaire la charge
    oeuvre_chargee = repo.charger("livre_123", "a_moderer")
    print(f"2. Chargement depuis disque : {oeuvre_chargee.titre} - État: {oeuvre_chargee._etat}")

    # 5. Changement d'état (Simulation Pattern State)
    oeuvre_chargee.set_etat(EtatEnTraitement())
    
    # 6. Déplacement vers 'fond_commun' (Validation)
    print("3. Déplacement physique du fichier...")
    repo.deplacer(oeuvre_chargee, "a_moderer", "fond_commun")
    
    # 7. Vérification
    ids_attente = repo.lister_ids("a_moderer")
    ids_valides = repo.lister_ids("fond_commun")
    
    print(f"   -> Contenu 'a_moderer' : {ids_attente}")   # Devrait être vide
    print(f"   -> Contenu 'fond_commun' : {ids_valides}") # Devrait contenir livre_123

    print("=== FIN DU TEST ===")

if __name__ == "__main__":
    test_infrastructure()