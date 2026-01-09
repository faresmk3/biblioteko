# ============================================
# FICHIER COMPLET: src/app/__init__.py
# ============================================
"""
Configuration principale de l'application Pyramid
Injection de dépendances et configuration CORS
"""
import os
from pyramid.config import Configurator
from pyramid.response import Response
from src.app.infra.repositories import FileSystemGitRepository, RepoUtilisateurs, RepoDemandesPromotion 
from src.app.infra.crypto import ServiceChiffrement
from src.app.domain.services import ServiceDemandesPromotion, ServiceOeuvre, ServiceEmprunt, ServiceReconnaissanceIA


def main(global_config, **settings):
    """
    Fonction principale qui construit l'application WSGI
    
    Cette fonction :
    1. Configure les routes et les vues
    2. Initialise tous les dépôts (repositories)
    3. Initialise tous les services métier
    4. Enregistre tout dans le registre Pyramid
    5. Configure CORS
    """
    with Configurator(settings=settings) as config:
        
        # ====================================
        # 1. CONFIGURATION DES ROUTES ET VUES
        # ====================================
        config.include('.routes')
        
        # Scanner tous les modules de vues
        config.scan('.views.api')
        config.scan('.views.auth_views')
        config.scan('.views.emprunts')
        config.scan('.views.classification')
        config.scan('.views.multi_ia')
        config.scan('.views.catalogue')
        config.scan('.views.autres')
        config.scan('.views.demandes_view')
        
        # ====================================
        # 2. INJECTION DE DÉPENDANCES
        # ====================================
        
        # Déterminer le répertoire racine
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        data_path = os.path.join(root_dir, 'data')
        
        # Créer le dossier data s'il n'existe pas
        if not os.path.exists(data_path):
            os.makedirs(data_path)
            print(f"[Init] Dossier data créé : {data_path}")
        
        # Créer la structure de dossiers nécessaire
        dossiers_requis = ['a_moderer', 'fond_commun', 'sequestre', 'archives', 'emprunts', 'demandes_promotion']
        for dossier in dossiers_requis:
            dossier_path = os.path.join(data_path, dossier)
            if not os.path.exists(dossier_path):
                os.makedirs(dossier_path)
                print(f"[Init] Dossier créé : {dossier}")
        
        print(f"[Pyramid] Démarrage avec stockage dans : {root_dir}")
        
        # ====================================
        # 3. INITIALISATION DES REPOSITORIES
        # ====================================
        
        # Repository pour les œuvres (Git + Filesystem)
        repo_oeuvres = FileSystemGitRepository(root_dir)
        
        # Repository pour les utilisateurs (JSON)
        users_json_path = os.path.join(data_path, 'users.json')
        repo_users = RepoUtilisateurs(users_json_path)
        
        # Service de chiffrement
        service_crypto = ServiceChiffrement()
        
        print("[Init] Repositories initialisés")
        
        # ====================================
        # 4. INITIALISATION DES SERVICES
        # ====================================

        # 🔍 Afficher les utilisateurs existants
        try:
            nb_users = repo_users.count_users()
            print(f"[Init] Utilisateurs existants : {nb_users}")
            
            if nb_users > 0:
                emails = repo_users.get_all_emails()
                print("[Init] Emails enregistrés :")
                for email in emails:
                    user = repo_users.get_by_email(email)
                    if user:
                        roles = [r.nom_role for r in user.roles]
                        print(f"  - {email} ({', '.join(roles)})")
            else:
                print("[Init] ℹ️  Aucun utilisateur trouvé")
                print("[Init] 💡 Créez un compte via /register")
        
        except Exception as e:
            print(f"[Init] ⚠️  Erreur lors de la vérification des utilisateurs : {e}")
        
        # Service de gestion des œuvres
        service_oeuvre = ServiceOeuvre(repo_oeuvres)
        
        # Service de gestion des emprunts
        service_emprunt = ServiceEmprunt(repo_oeuvres, service_crypto)
        
        # Service de reconnaissance multi-IA
        service_ia = ServiceReconnaissanceIA()
        
        print("[Init] Services métier initialisés")

        # 🆕 AJOUTER CES LIGNES
        # Repository des demandes de promotion
        repo_demandes = RepoDemandesPromotion(root_dir, repo_oeuvres.repo)

        # Service de gestion des demandes de promotion
        service_demandes_promotion = ServiceDemandesPromotion(
            repo_demandes,
            repo_users
)
        
        # ====================================
        # 5. ENREGISTREMENT DANS LE REGISTRE
        # ====================================
        
        # Repositories
        config.registry.repo_oeuvres = repo_oeuvres
        config.registry.depot_utilisateurs = repo_users
        
        # Services
        config.registry.service_oeuvre = service_oeuvre
        config.registry.service_emprunt = service_emprunt
        config.registry.service_ia = service_ia
        config.registry.service_demandes_promotion = service_demandes_promotion  
        
        # Service crypto (peut être utile ailleurs)
        config.registry.service_crypto = service_crypto
        
        print("[Init] Registre Pyramid configuré")
        
        # ====================================
        # 6. CONFIGURATION CORS
        # ====================================
        config.add_tween('src.app.cors_tween_factory')
        
        print("[Init] CORS configuré")
        print("[Init] Application prête ✓")
    
    return config.make_wsgi_app()


def cors_tween_factory(handler, registry):
    """
    Factory pour le middleware CORS
    
    Permet les requêtes cross-origin depuis n'importe quelle origine
    Nécessaire pour les applications frontend (React, Vue, etc.)
    """
    def cors_tween(request):
        # Requête de pré-vérification (OPTIONS)
        if request.method == 'OPTIONS':
            response = Response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST,GET,DELETE,PUT,PATCH,OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response
        
        # Requête normale - traiter puis ajouter les headers CORS
        response = handler(request)
        
        # Ajouter les headers CORS à toutes les réponses
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST,GET,DELETE,PUT,PATCH,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type'
        
        return response
    
    return cors_tween