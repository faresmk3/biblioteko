# ============================================
# FICHIER 11: tests/validation/test_scenarios_metier.py (NOUVEAU)
# ============================================
"""
Tests de validation des scénarios métier du cahier des charges
"""
import pytest
from src.app.domain.modeles import (
    Utilisateur, Oeuvre, CategorieOeuvre, 
    StatutDroit, PermissionsSysteme
)

class TestScenariosMetier:
    """
    Validation des scénarios métier définis dans le cahier des charges
    """
    
    def test_scenario_devenir_membre(self):
        """
        SCÉNARIO : Devenir membre de la bibliothèque
        CRITÈRE : Un utilisateur peut s'inscrire avec email/mdp
        """
        membre = Utilisateur("Nouveau", "Membre", "nouveau@test.fr", "motdepasse")
        role = PermissionsSysteme.creer_role_membre()
        membre.ajouter_role(role)
        
        # Validations
        assert membre.email == "nouveau@test.fr"
        assert membre.verifier_mdp("motdepasse") == True
        assert membre.a_la_permission("peut_emprunter_oeuvre") == True
    
    def test_scenario_proposer_oeuvre(self):
        """
        SCÉNARIO : Un membre propose une œuvre pour partage
        CRITÈRE : L'œuvre est créée avec statut SOUMISE
        """
        membre = Utilisateur("Martin", "Alice", "alice@test.fr", "pass")
        oeuvre = Oeuvre("Mon Livre", "Moi", "livre.pdf", membre)
        
        assert oeuvre.etat.nom == "SOUMISE"
        assert oeuvre.soumis_par_email == "alice@test.fr"
    
    def test_scenario_moderer_oeuvre(self):
        """
        SCÉNARIO : Un bibliothécaire modère une œuvre
        CRITÈRES : 
        - Seul un biblio peut modérer
        - États SOUMISE -> EN_TRAITEMENT -> VALIDEE
        """
        membre = Utilisateur("Membre", "Test", "membre@test.fr", "pass")
        biblio = Utilisateur("Biblio", "Admin", "biblio@test.fr", "pass")
        
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        oeuvre = Oeuvre("Livre", "Auteur", "livre.pdf", membre)
        
        # Le membre ne peut PAS modérer
        assert membre.a_la_permission("peut_moderer_oeuvre") == False
        
        # Le biblio peut modérer
        assert biblio.a_la_permission("peut_moderer_oeuvre") == True
        
        # Workflow de modération
        oeuvre.traiter()
        assert oeuvre.etat.nom == "EN_TRAITEMENT"
        
        oeuvre.accepter()
        assert oeuvre.etat.nom == "VALIDEE"
    
    def test_scenario_emprunter_oeuvre_sous_droits(self):
        """
        SCÉNARIO : Emprunter une œuvre sous droits pour 14 jours
        CRITÈRE : L'emprunt est limité à 2 semaines
        """
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Livre Récent", "Auteur", "recent.pdf", membre)
        oeuvre.statut_droit = StatutDroit.SOUS_DROITS
        
        from src.app.domain.modeles import Emprunt
        emprunt = Emprunt(oeuvre, membre, duree_jours=14)
        
        assert emprunt.jours_restants() == 14
        assert emprunt.est_actif == True
    
    def test_scenario_acceder_fond_commun(self):
        """
        SCÉNARIO : Consulter le fond commun (domaine public)
        CRITÈRE : Accès gratuit, pas d'emprunt limité
        """
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre_libre = Oeuvre("Oeuvre Ancienne", "Auteur 1800", "ancien.pdf", membre)
        
        oeuvre_libre.statut_droit = StatutDroit.DOMAINE_PUBLIC
        
        assert oeuvre_libre.est_libre_de_droits() == True
    
    def test_scenario_classifier_oeuvre(self):
        """
        SCÉNARIO : Classifier une œuvre (Livres, Musique, Vidéos)
        CRITÈRE : Une œuvre peut avoir plusieurs catégories
        """
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("BD Éducative", "Auteur", "bd.pdf", membre)
        
        oeuvre.ajouter_categorie(CategorieOeuvre.LIVRE_BD)
        oeuvre.ajouter_categorie(CategorieOeuvre.LIVRE_EDUCATION)
        
        assert len(oeuvre.categories) == 2
        assert oeuvre.est_dans_categorie(CategorieOeuvre.LIVRE_BD)
        assert oeuvre.est_dans_categorie(CategorieOeuvre.LIVRE_EDUCATION)

