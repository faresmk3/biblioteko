# ============================================
# FICHIER 9: tests/unit/test_modeles.py (NOUVEAU)
# ============================================
"""
Tests unitaires pour les modèles du domaine
"""
import pytest
from datetime import datetime, timedelta
from src.app.domain.modeles import (
    Utilisateur, Role, Permission, Oeuvre, Emprunt,
    CategorieOeuvre, StatutDroit, PermissionsSysteme,
    EtatSoumise, EtatEnTraitement, EtatValidee
)

class TestUtilisateur:
    """Tests du modèle Utilisateur"""
    
    def test_creation_utilisateur(self):
        """Test : Création d'un utilisateur"""
        user = Utilisateur("Dupont", "Jean", "jean@test.fr", "motdepasse123")
        
        assert user.nom == "Dupont"
        assert user.prenom == "Jean"
        assert user.email == "jean@test.fr"
        assert user.verifier_mdp("motdepasse123") == True
        assert user.verifier_mdp("mauvais") == False
    
    def test_hashing_mdp(self):
        """Test : Le mot de passe est bien hashé avec bcrypt"""
        user = Utilisateur("Test", "User", "test@test.fr", "secret")
        
        # Le hash ne doit PAS être le mot de passe en clair
        assert user.mdp_hash != b"secret"
        assert len(user.mdp_hash) == 60  # Longueur d'un hash bcrypt
    
    def test_cle_chiffrement_generee(self):
        """Test : Chaque utilisateur a une clé de chiffrement unique"""
        user1 = Utilisateur("A", "A", "a@test.fr", "pass")
        user2 = Utilisateur("B", "B", "b@test.fr", "pass")
        
        assert user1.cle_chiffrement != user2.cle_chiffrement
        assert len(user1.cle_chiffrement) == 44  # Longueur clé Fernet base64
    
    def test_permissions_rbac(self):
        """Test : Système de permissions RBAC"""
        perm_moderer = Permission("peut_moderer_oeuvre")
        role_biblio = Role("Bibliothécaire")
        role_biblio.ajouter_permission(perm_moderer)
        
        user = Utilisateur("Admin", "Jean", "biblio@test.fr", "pass")
        user.ajouter_role(role_biblio)
        
        assert user.a_la_permission("peut_moderer_oeuvre") == True
        assert user.a_la_permission("autre_permission") == False
    
    def test_factory_roles(self):
        """Test : Factory pour créer les rôles standards"""
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        role_membre = PermissionsSysteme.creer_role_membre()
        
        assert role_biblio.nom_role == "Bibliothécaire"
        assert len(role_biblio.permissions) >= 3
        
        assert role_membre.nom_role == "Membre"
        assert any(p.nom_permission == "peut_emprunter_oeuvre" for p in role_membre.permissions)


class TestOeuvre:
    """Tests du modèle Oeuvre"""
    
    def test_creation_oeuvre(self):
        """Test : Création d'une œuvre"""
        membre = Utilisateur("Martin", "Alice", "alice@test.fr", "pass")
        oeuvre = Oeuvre("Les Misérables", "Victor Hugo", "miserables.pdf", membre)
        
        assert oeuvre.titre == "Les Misérables"
        assert oeuvre.auteur == "Victor Hugo"
        assert oeuvre.etat.nom == "SOUMISE"
    
    def test_state_pattern_transitions(self):
        """Test : Transitions d'état avec le pattern State"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Titre", "Auteur", "file.pdf", membre)
        
        # État initial
        assert oeuvre.etat.nom == "SOUMISE"
        
        # SOUMISE -> EN_TRAITEMENT
        oeuvre.traiter()
        assert oeuvre.etat.nom == "EN_TRAITEMENT"
        
        # EN_TRAITEMENT -> VALIDEE
        oeuvre.accepter()
        assert oeuvre.etat.nom == "VALIDEE"
    
    def test_state_pattern_erreurs(self):
        """Test : Transitions interdites lèvent des erreurs"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Titre", "Auteur", "file.pdf", membre)
        
        # Impossible d'accepter depuis SOUMISE
        with pytest.raises(PermissionError):
            oeuvre.accepter()
        
        # Transition valide
        oeuvre.traiter()
        
        # Impossible de traiter depuis EN_TRAITEMENT
        with pytest.raises(PermissionError):
            oeuvre.traiter()
    
    def test_classification_multi_categories(self):
        """Test : Une œuvre peut avoir plusieurs catégories"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("BD Technique", "Auteur", "bd.pdf", membre)
        
        oeuvre.ajouter_categorie(CategorieOeuvre.LIVRE_BD)
        oeuvre.ajouter_categorie(CategorieOeuvre.LIVRE_TECHNIQUE)
        
        assert len(oeuvre.categories) == 2
        assert oeuvre.est_dans_categorie(CategorieOeuvre.LIVRE_BD)
        assert oeuvre.est_dans_categorie(CategorieOeuvre.LIVRE_TECHNIQUE)
        assert not oeuvre.est_dans_categorie(CategorieOeuvre.MUSIQUE_JAZZ)
    
    def test_statut_juridique(self):
        """Test : Gestion du statut juridique"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Oeuvre Ancienne", "Auteur du 19e", "old.pdf", membre)
        
        # Par défaut : sous droits
        assert oeuvre.statut_droit == StatutDroit.SOUS_DROITS
        
        # Simulation passage domaine public
        oeuvre.date_liberation = datetime.now() - timedelta(days=1)
        oeuvre.calculer_statut_droit()
        
        assert oeuvre.est_libre_de_droits() == True
        assert oeuvre.statut_droit == StatutDroit.DOMAINE_PUBLIC
    
    def test_resultats_multi_ia(self):
        """Test : Stockage des résultats multi-IA"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Livre Scanné", "Auteur", "scan.pdf", membre)
        
        oeuvre.enregistrer_resultat_ocr("tesseract", "Texte Tesseract...")
        oeuvre.enregistrer_resultat_ocr("gemini", "Texte Gemini...")
        oeuvre.enregistrer_resultat_ocr("pixtral", "Texte Pixtral...")
        
        assert len(oeuvre.resultats_ocr) == 3
        assert "tesseract" in oeuvre.resultats_ocr
        
        scores = oeuvre.comparer_qualite_ocr()
        assert "tesseract" in scores
        assert "nb_mots" in scores["tesseract"]


class TestEmprunt:
    """Tests du modèle Emprunt"""
    
    def test_creation_emprunt(self):
        """Test : Création d'un emprunt"""
        membre = Utilisateur("Martin", "Alice", "alice@test.fr", "pass")
        oeuvre = Oeuvre("Livre", "Auteur", "livre.pdf", membre)
        
        emprunt = Emprunt(oeuvre, membre, duree_jours=14)
        
        assert emprunt.oeuvre_titre == "Livre"
        assert emprunt.utilisateur_email == "alice@test.fr"
        assert emprunt.jours_restants() == 14
        assert emprunt.est_actif == True
    
    def test_expiration_emprunt(self):
        """Test : Détection de l'expiration"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Livre", "Auteur", "livre.pdf", membre)
        
        emprunt = Emprunt(oeuvre, membre, duree_jours=14)
        
        # Simulation expiration
        emprunt.date_fin = datetime.now() - timedelta(days=1)
        
        assert emprunt.est_expire() == True
        assert emprunt.jours_restants() == 0
    
    def test_retour_emprunt(self):
        """Test : Retour d'une œuvre"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Livre", "Auteur", "livre.pdf", membre)
        emprunt = Emprunt(oeuvre, membre)
        
        emprunt.retourner()
        
        assert emprunt.est_actif == False
        assert emprunt.date_retour is not None
        assert emprunt.jours_restants() == 0
    
    def test_renouvellement(self):
        """Test : Prolongation d'un emprunt"""
        membre = Utilisateur("Test", "User", "test@test.fr", "pass")
        oeuvre = Oeuvre("Livre", "Auteur", "livre.pdf", membre)
        emprunt = Emprunt(oeuvre, membre, duree_jours=7)
        
        date_fin_initiale = emprunt.date_fin
        
        emprunt.renouveler(jours=7)
        
        assert emprunt.date_fin > date_fin_initiale
        assert emprunt.jours_restants() == 14  # 7 + 7