# src/cli/test_workflow_moderation.py
import os
from src.app.domain.modeles import Utilisateur, Role, Permission, Oeuvre
from src.app.domain.services import ServiceOeuvre
from src.app.infra.repositories import FileSystemGitRepository

# 1. SETUP INFRA
repo = FileSystemGitRepository(os.getcwd())

# 2. SETUP SERVICE
service = ServiceOeuvre(repo)

# 3. SETUP ACTEURS
perm_moderer = Permission("peut_moderer_oeuvre")
role_biblio = Role("Bibliothécaire")
role_biblio.ajouter_permission(perm_moderer)

# CORRECTION ICI : Ordre (Nom, Prénom, Email, MotDePasse)
biblio = Utilisateur("Admin", "Jean", "biblio@culture.org", "password123")
biblio.ajouter_role(role_biblio)

# CORRECTION ICI AUSSI
membre = Utilisateur("Membre", "Alice", "alice@gmail.com", "password123")

# --- SCÉNARIO ---

print("--- 1. Un membre soumet une œuvre ---")
# Attention: Oeuvre attend (Titre, Auteur, Fichier, SoumisPar)
oeuvre = Oeuvre("Les Misérables", "Victor Hugo", "les_mis.pdf", membre)
repo.sauvegarder(oeuvre) 

print("--- 2. Le bibliothécaire liste les œuvres ---")
a_moderer = service.lister_oeuvres_a_moderer(biblio)
for o in a_moderer:
    # Note: dans votre modèle c'est 'auteur_nom' et non 'auteur'
    auteur = getattr(o, 'auteur_nom', getattr(o, 'auteur', 'Inconnu'))
    print(f"Trouvé : {o.titre} (Auteur: {auteur})")

if a_moderer:
    # On récupère le nom du fichier généré (titre avec underscores + .md)
    target_id = f"{a_moderer[0].titre.replace(' ', '_')}.md"
    
    print(f"\n--- 3. Traitement de {target_id} ---")
    service.traiter_oeuvre(biblio, target_id)
    
    print("\n--- 4. Validation ---")
    service.valider_oeuvre(biblio, target_id, "fond_commun")

print("\n✅ Test Workflow terminé. Vérifiez le dossier 'data/fond_commun' !")