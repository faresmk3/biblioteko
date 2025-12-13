from core.auth import RoleFactory, Utilisateur
from infrastructure.repositories import FileSystemOeuvreRepository
from services.service_oeuvre import ServiceOeuvre
import shutil
import os

def nettoyer_environnement_test():
    """Supprime le dossier de test pour recommencer à zéro"""
    if os.path.exists("bibliotheque_data"):
        shutil.rmtree("bibliotheque_data")

def main():
    print("==================================================")
    print("   DEMARRAGE DE CULTURE DIFFUSION (BACKEND CLI)   ")
    print("==================================================")

    # 0. Initialisation (Bootstrap)
    nettoyer_environnement_test()
    repo = FileSystemOeuvreRepository(base_path="bibliotheque_data")
    service = ServiceOeuvre(repo)

    # --- Création des Acteurs ---
    # Bob (Membre)
    bob = Utilisateur(id="u1", nom="Bob", email="bob@test.com")
    bob.ajouter_role(RoleFactory.get_role_membre())

    # Alice (Bibliothécaire)
    alice = Utilisateur(id="u2", nom="Alice", email="alice@test.com")
    alice.ajouter_role(RoleFactory.get_role_bibliothecaire())

    # --- SCÉNARIO 1 : Bob soumet une œuvre ---
    print("\n--- ÉTAPE 1 : SOUMISSION ---")
    try:
        oeuvre_bob = service.soumettre_oeuvre(
            membre=bob, 
            titre="Les Fleurs du Mal", 
            auteur="Baudelaire"
        )
    except PermissionError as e:
        print(f"Erreur : {e}")

    # --- SCÉNARIO 2 : Bob essaie de modérer (Doit échouer) ---
    print("\n--- ÉTAPE 2 : TENTATIVE D'INTRUSION ---")
    try:
        service.lister_a_moderer(bob)
    except PermissionError as e:
        print(f" Sécurité RBAC active : {e}")

    # --- SCÉNARIO 3 : Alice modère ---
    print("\n--- ÉTAPE 3 : MODÉRATION ---")
    
    # Alice liste les œuvres
    liste = service.lister_a_moderer(alice)
    print(f"Alice voit {len(liste)} oeuvre(s) à modérer.")
    
    if liste:
        oeuvre_a_traiter = liste[0]
        print(f"Alice décide de valider : {oeuvre_a_traiter.titre}")
        
        # Alice valide
        service.valider_oeuvre(alice, oeuvre_a_traiter.id)

    # --- VÉRIFICATION FINALE ---
    print("\n--- ÉTAPE 4 : VÉRIFICATION DU DISQUE ---")
    ids_publies = repo.lister_ids("fond_commun")
    ids_attente = repo.lister_ids("a_moderer")
    
    print(f"Dossier 'a_moderer' contient : {ids_attente}")
    print(f"Dossier 'fond_commun' contient : {ids_publies}")

    if ids_publies:
        print("\n SUCCÈS TOTAL : L'architecture MVP fonctionne !")
    else:
        print("\n ÉCHEC : L'œuvre n'est pas arrivée à destination.")

if __name__ == "__main__":
    main()