# test_domain_manuel.py
from src.app.domain.modeles import Utilisateur, Role, Permission, Oeuvre

# 1. Setup RBAC
perm_moderer = Permission("peut_moderer_oeuvre")
role_biblio = Role("Bibliothécaire")
role_biblio.ajouter_permission(perm_moderer)

biblio = Utilisateur("Dupont", "Jean", "biblio@culture.org", "secret")
biblio.ajouter_role(role_biblio)

membre = Utilisateur("Martin", "Alice", "alice@gmail.com", "pass")

# 2. Scénario de Soumission
print("\n--- 1. Soumission ---")
oeuvre = Oeuvre("Les Misérables", "Victor Hugo", "mis.pdf", membre)
print(oeuvre)  # Doit afficher état SOUMISE

# 3. Scénario de Traitement
print("\n--- 2. Prise en charge ---")
if biblio.a_la_permission("peut_moderer_oeuvre"):
    oeuvre.traiter()  # Doit passer EN_TRAITEMENT
    print(oeuvre)
else:
    print("Accès refusé")

# 4. Scénario de Validation
print("\n--- 3. Validation ---")
oeuvre.set_infos("Genre", "Roman Historique")
oeuvre.accepter() # Doit passer VALIDEE
print(oeuvre)
print("Métadonnées:", oeuvre.metadonnees)

# 5. Test d'erreur (Transition interdite)
print("\n--- 4. Test Erreur ---")
try:
    oeuvre.refuser() # Impossible depuis VALIDEE
except Exception as e:
    print(f"Erreur attrapée : {e}")