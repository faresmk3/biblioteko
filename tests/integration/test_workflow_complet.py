# ============================================
# FICHIER 10: tests/integration/test_workflow_complet.py (NOUVEAU)
# ============================================
"""
Tests d'intégration du workflow complet
"""
import pytest
import os
import tempfile
from src.app.domain.modeles import Utilisateur, PermissionsSysteme
from src.app.domain.services import ServiceOeuvre, ServiceEmprunt
from src.app.infra.repositories import FileSystemGitRepository
from src.app.infra.crypto import ServiceChiffrement

class TestWorkflowComplet:
    """Tests d'intégration end-to-end"""
    
    @pytest.fixture
    def setup(self):
        """Setup du test : Création des services"""
        # Dossier temporaire pour Git
        temp_dir = tempfile.mkdtemp()
        
        repo = FileSystemGitRepository(temp_dir)
        service_oeuvre = ServiceOeuvre(repo)
        crypto = ServiceChiffrement()
        service_emprunt = ServiceEmprunt(repo, crypto)
        
        yield {
            'repo': repo,
            'service_oeuvre': service_oeuvre,
            'service_emprunt': service_emprunt,
            'temp_dir': temp_dir
        }
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_scenario_soumission_moderation_validation(self, setup):
        """
        SCÉNARIO 1 : Soumission -> Modération -> Validation
        """
        service = setup['service_oeuvre']
        
        # 1. Création des acteurs
        membre = Utilisateur("Martin", "Alice", "alice@test.fr", "pass123")
        role_membre = PermissionsSysteme.creer_role_membre()
        membre.ajouter_role(role_membre)
        
        biblio = Utilisateur("Dupont", "Jean", "biblio@test.fr", "admin123")
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        # 2. Le membre soumet une œuvre
        from src.app.domain.modeles import Oeuvre
        oeuvre = Oeuvre("Les Misérables", "Victor Hugo", "miserables.pdf", membre)
        service.soumettre_oeuvre(oeuvre)
        
        assert oeuvre.etat.nom == "SOUMISE"
        
        # 3. Le bibliothécaire liste les œuvres à modérer
        a_moderer = service.lister_oeuvres_a_moderer(biblio)
        assert len(a_moderer) >= 1
        
        # 4. Traitement de l'œuvre
        id_oeuvre = oeuvre.id
        service.traiter_oeuvre(biblio, id_oeuvre)
        
        oeuvre_traitee = service.recuperer_oeuvre(id_oeuvre)
        assert oeuvre_traitee.etat.nom == "EN_TRAITEMENT"
        
        # 5. Validation
        service.valider_oeuvre(biblio, id_oeuvre, "fond_commun")
        
        oeuvre_validee = service.recuperer_oeuvre(id_oeuvre)
        assert oeuvre_validee.etat.nom == "VALIDEE"
    
    def test_scenario_emprunt_retour(self, setup):
        """
        SCÉNARIO 2 : Emprunter -> Consulter -> Retourner
        """
        service_oeuvre = setup['service_oeuvre']
        service_emprunt = setup['service_emprunt']
        
        # 1. Préparation : Créer une œuvre validée
        membre = Utilisateur("Test", "User", "user@test.fr", "pass")
        role_membre = PermissionsSysteme.creer_role_membre()
        membre.ajouter_role(role_membre)
        
        biblio = Utilisateur("Admin", "Jean", "admin@test.fr", "pass")
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        from src.app.domain.modeles import Oeuvre
        oeuvre = Oeuvre("Livre Test", "Auteur", "test.pdf", membre)
        service_oeuvre.soumettre_oeuvre(oeuvre)
        
        id_oeuvre = f"{oeuvre.titre.replace(' ', '_')}.md"
        service_oeuvre.traiter_oeuvre(biblio, id_oeuvre)
        service_oeuvre.valider_oeuvre(biblio, id_oeuvre, "fond_commun")
        
        # 2. Le membre emprunte l'œuvre
        emprunt = service_emprunt.emprunter_oeuvre(membre, id_oeuvre, duree_jours=7)
        
        assert emprunt.est_actif == True
        assert emprunt.jours_restants() == 7
        
        # 3. Consultation de mes emprunts
        mes_emprunts = service_emprunt.lister_mes_emprunts(membre)
        assert len(mes_emprunts) == 1
        assert mes_emprunts[0].oeuvre_titre == "Livre Test"
        
        # 4. Retour de l'œuvre
        service_emprunt.retourner_oeuvre(membre, emprunt.id)
        
        mes_emprunts_apres = service_emprunt.lister_mes_emprunts(membre)
        assert len(mes_emprunts_apres) == 0
