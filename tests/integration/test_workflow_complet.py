# ============================================
# tests/integration/test_workflow_complet_fixed.py
# Tests d'intégration CORRIGÉS
# ============================================
"""
Tests d'intégration du workflow complet - VERSION CORRIGÉE
"""
import pytest
import os
import tempfile
import shutil
from src.app.domain.modeles import Utilisateur, PermissionsSysteme, Oeuvre
from src.app.domain.services import ServiceOeuvre, ServiceEmprunt
from src.app.infra.repositories import FileSystemGitRepository
from src.app.infra.crypto import ServiceChiffrement


class TestWorkflowComplet:
    """Tests d'intégration end-to-end - CORRIGÉS"""
    
    @pytest.fixture
    def setup(self):
        """
        Setup du test : Création des services
        CORRECTION : Crée la structure de dossiers complète
        """
        # Dossier temporaire pour Git
        temp_dir = tempfile.mkdtemp()
        
        # CORRECTION 1 : Créer la structure de dossiers nécessaire
        os.makedirs(os.path.join(temp_dir, "data", "a_moderer"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "data", "fond_commun"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "data", "sequestre"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "data", "archives"), exist_ok=True)
        
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
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_scenario_soumission_moderation_validation(self, setup):
        """
        SCÉNARIO 1 : Soumission -> Modération -> Validation
        CORRIGÉ : Gestion correcte des IDs et des paths
        """
        service = setup['service_oeuvre']
        repo = setup['repo']
        
        # 1. Création des acteurs
        membre = Utilisateur("Martin", "Alice", "alice@test.fr", "pass123")
        role_membre = PermissionsSysteme.creer_role_membre()
        membre.ajouter_role(role_membre)
        
        biblio = Utilisateur("Dupont", "Jean", "biblio@test.fr", "admin123")
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        # 2. Le membre soumet une œuvre
        oeuvre = Oeuvre("Les Misérables", "Victor Hugo", "miserables.pdf", membre)
        service.soumettre_oeuvre(oeuvre)
        
        assert oeuvre.etat.nom == "SOUMISE"
        print(f"✓ Oeuvre soumise avec état : {oeuvre.etat.nom}")
        
        # 3. Le bibliothécaire liste les œuvres à modérer
        a_moderer = service.lister_oeuvres_a_moderer(biblio)
        assert len(a_moderer) >= 1, "Aucune œuvre à modérer trouvée"
        print(f"✓ {len(a_moderer)} œuvre(s) à modérer")
        
        # CORRECTION 2 : L'ID est le nom du fichier Markdown généré
        id_oeuvre = f"{oeuvre.titre.replace(' ', '_')}.md"
        print(f"✓ ID de l'oeuvre : {id_oeuvre}")
        
        # 4. Traitement de l'œuvre
        service.traiter_oeuvre(biblio, id_oeuvre)
        
        # CORRECTION 3 : Récupération avec le bon ID
        oeuvre_traitee = repo.get_oeuvre_by_id(id_oeuvre)
        assert oeuvre_traitee is not None, "Oeuvre non trouvée après traitement"
        assert oeuvre_traitee.etat.nom == "EN_TRAITEMENT"
        print(f"✓ Oeuvre traitée : {oeuvre_traitee.etat.nom}")
        
        # 5. Validation
        service.valider_oeuvre(biblio, id_oeuvre, "fond_commun")
        
        # CORRECTION 4 : Chercher dans le bon dossier après déplacement
        oeuvre_validee = repo.get_oeuvre_by_id(id_oeuvre)
        assert oeuvre_validee is not None, "Oeuvre non trouvée après validation"
        assert oeuvre_validee.etat.nom == "VALIDEE"
        print(f"✓ Oeuvre validée : {oeuvre_validee.etat.nom}")
        
        # Vérification que le fichier existe bien dans fond_commun
        path_fond_commun = os.path.join(setup['temp_dir'], "data", "fond_commun", id_oeuvre)
        assert os.path.exists(path_fond_commun), f"Fichier non trouvé : {path_fond_commun}"
        print(f"✓ Fichier trouvé dans fond_commun")
    
    def test_scenario_emprunt_retour(self, setup):
        """
        SCÉNARIO 2 : Emprunter -> Consulter -> Retourner
        CORRIGÉ : Création complète du workflow avant emprunt
        """
        service_oeuvre = setup['service_oeuvre']
        service_emprunt = setup['service_emprunt']
        repo = setup['repo']
        
        # 1. Préparation : Créer une œuvre validée
        membre = Utilisateur("Test", "User", "user@test.fr", "pass")
        role_membre = PermissionsSysteme.creer_role_membre()
        membre.ajouter_role(role_membre)
        
        biblio = Utilisateur("Admin", "Jean", "admin@test.fr", "pass")
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        # CORRECTION 5 : Créer et valider une œuvre complète
        oeuvre = Oeuvre("Livre Test", "Auteur", "test.pdf", membre)
        service_oeuvre.soumettre_oeuvre(oeuvre)
        
        id_oeuvre = f"{oeuvre.titre.replace(' ', '_')}.md"
        
        # Workflow complet de validation
        service_oeuvre.traiter_oeuvre(biblio, id_oeuvre)
        service_oeuvre.valider_oeuvre(biblio, id_oeuvre, "fond_commun")
        print(f"✓ Oeuvre validée pour emprunt : {id_oeuvre}")
        
        # CORRECTION 6 : Mock du contenu du fichier pour l'emprunt
        # Le service d'emprunt essaie de lire le contenu du fichier
        # Pour ce test, on mock cette méthode
        def mock_lire_contenu(id_oeuvre):
            return b"Contenu du fichier PDF..."
        
        # Patch temporaire de la méthode
        original_method = repo.lire_contenu_oeuvre if hasattr(repo, 'lire_contenu_oeuvre') else None
        repo.lire_contenu_oeuvre = mock_lire_contenu
        
        try:
            # 2. Le membre emprunte l'œuvre
            emprunt = service_emprunt.emprunter_oeuvre(membre, id_oeuvre, duree_jours=7)
            
            assert emprunt.est_actif == True
            assert emprunt.jours_restants() == 7
            print(f"✓ Emprunt créé : {emprunt.id}")
            
            # 3. Consultation de mes emprunts
            mes_emprunts = service_emprunt.lister_mes_emprunts(membre)
            assert len(mes_emprunts) == 1
            assert mes_emprunts[0].oeuvre_titre == "Livre Test"
            print(f"✓ {len(mes_emprunts)} emprunt(s) actif(s)")
            
            # 4. Retour de l'œuvre
            service_emprunt.retourner_oeuvre(membre, emprunt.id)
            
            mes_emprunts_apres = service_emprunt.lister_mes_emprunts(membre)
            # CORRECTION 7 : Filtrer les emprunts inactifs
            emprunts_actifs = [e for e in mes_emprunts_apres if e.est_actif]
            assert len(emprunts_actifs) == 0
            print(f"✓ Oeuvre retournée, {len(emprunts_actifs)} emprunt(s) actif(s)")
            
        finally:
            # Restaurer la méthode originale
            if original_method:
                repo.lire_contenu_oeuvre = original_method
    
    def test_scenario_rejet_oeuvre(self, setup):
        """
        SCÉNARIO 3 : Soumission -> Traitement -> Rejet
        NOUVEAU TEST pour couvrir le cas du rejet
        """
        service = setup['service_oeuvre']
        repo = setup['repo']
        
        # Acteurs
        membre = Utilisateur("Membre", "Test", "membre@test.fr", "pass")
        biblio = Utilisateur("Biblio", "Admin", "biblio@test.fr", "pass")
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        # Soumission
        oeuvre = Oeuvre("Oeuvre Problématique", "Auteur", "probleme.pdf", membre)
        service.soumettre_oeuvre(oeuvre)
        
        id_oeuvre = f"{oeuvre.titre.replace(' ', '_')}.md"
        
        # Traitement
        service.traiter_oeuvre(biblio, id_oeuvre)
        
        # Rejet avec motif
        motif = "Contenu non conforme aux règles"
        service.rejeter_oeuvre(biblio, id_oeuvre, motif)
        
        # Vérification
        oeuvre_rejetee = repo.get_oeuvre_by_id(id_oeuvre)
        assert oeuvre_rejetee.etat.nom == "REFUSEE"
        print(f"✓ Oeuvre rejetée : {oeuvre_rejetee.etat.nom}")


# ============================================
# TESTS DE NON-RÉGRESSION
# ============================================

class TestNonRegression:
    """Tests pour vérifier que les corrections ne cassent pas le reste"""
    
    @pytest.fixture
    def setup(self):
        temp_dir = tempfile.mkdtemp()
        os.makedirs(os.path.join(temp_dir, "data", "a_moderer"), exist_ok=True)
        os.makedirs(os.path.join(temp_dir, "data", "fond_commun"), exist_ok=True)
        
        repo = FileSystemGitRepository(temp_dir)
        service = ServiceOeuvre(repo)
        
        yield {'repo': repo, 'service': service, 'temp_dir': temp_dir}
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_permissions_correctes(self, setup):
        """Vérifie que seuls les bibliothécaires peuvent modérer"""
        service = setup['service']
        
        # Membre sans permissions
        membre = Utilisateur("Membre", "Simple", "membre@test.fr", "pass")
        role_membre = PermissionsSysteme.creer_role_membre()
        membre.ajouter_role(role_membre)
        
        # Tentative de lister les œuvres à modérer
        with pytest.raises(PermissionError):
            service.lister_oeuvres_a_moderer(membre)
        
        print("✓ Les permissions sont bien vérifiées")
    
    def test_multiples_oeuvres(self, setup):
        """Teste la soumission de plusieurs œuvres"""
        service = setup['service']
        
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        
        # Soumettre 3 œuvres
        for i in range(3):
            oeuvre = Oeuvre(f"Livre {i+1}", f"Auteur {i+1}", f"livre{i+1}.pdf", membre)
            service.soumettre_oeuvre(oeuvre)
        
        # Vérifier qu'elles sont toutes présentes
        biblio = Utilisateur("Biblio", "Admin", "biblio@test.fr", "pass")
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        biblio.ajouter_role(role_biblio)
        
        oeuvres = service.lister_oeuvres_a_moderer(biblio)
        assert len(oeuvres) == 3
        print(f"✓ {len(oeuvres)} œuvres soumises et listées")


if __name__ == "__main__":
    # Pour exécuter les tests directement
    pytest.main([__file__, "-v", "--tb=short"])
