# test_rbac.py
from infrastructure.users_repo import UserRepositoryInMemory

def test_access_control():
    print("=== DÉMARRAGE DU TEST RBAC ===")
    
    # 1. Initialisation du repo (charge Bob, Alice, Charlie)
    repo = UserRepositoryInMemory()
    
    # 2. Récupération des utilisateurs
    bob = repo.trouver_par_email("bob@mail.com")
    alice = repo.trouver_par_email("alice@mail.com")
    charlie = repo.trouver_par_email("charlie@hack.com")

    # 3. Définition de l'action critique
    action_critique = "peut_moderer_oeuvre"

    print(f"\n--- Test de l'action : '{action_critique}' ---")

    # TEST BOB (Membre)
    if bob.a_la_permission(action_critique):
        print(f" ERREUR : {bob.nom} ne devrait PAS pouvoir modérer !")
    else:
        print(f" SUCCÈS : {bob.nom} a été bloqué correctement.")

    # TEST ALICE (Bibliothécaire)
    if alice.a_la_permission(action_critique):
        print(f" SUCCÈS : {alice.nom} a l'autorisation requise.")
    else:
        print(f" ERREUR : {alice.nom} devrait pouvoir modérer !")

    # TEST CHARLIE (Sans rôle)
    if charlie.a_la_permission("peut_proposer_oeuvre"): # Même proposer lui est interdit
        print(f" ERREUR : {charlie.nom} ne devrait rien pouvoir faire.")
    else:
        print(f" SUCCÈS : {charlie.nom} n'a aucun droit.")

    print("\n=== FIN DU TEST RBAC ===")

if __name__ == "__main__":
    test_access_control()