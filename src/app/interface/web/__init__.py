# src/app/interface/web/__init__.py
import os
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

# Imports du backend
from infrastructure.repositories import FileSystemOeuvreRepository
from infrastructure.users_repo import FileSystemUserRepository
from services.service_oeuvre import ServiceOeuvre
from services.service_auth import ServiceAuth
from services.service_emprunt import ServiceEmprunt

def main(global_config, **settings):
    """ Cette fonction retourne une application WSGI Pyramid. """
    
    settings['pyramid.debug_all'] = True
    settings['pyramid.reload_templates'] = True

    base_path = os.path.abspath("bibliotheque_data")
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # 1. Initialisation de l'Infrastructure
    repo_oeuvre = FileSystemOeuvreRepository(base_path=base_path)
    repo_user = FileSystemUserRepository(base_path=base_path)
    
    # 2. Initialisation des Services
    service_oeuvre = ServiceOeuvre(repo_oeuvre)
    service_auth = ServiceAuth(repo_user)
    service_auth.ensure_admin_exists()
    
    service_emprunt = ServiceEmprunt(repo_oeuvre, base_path)

    # 3. Configuration Session
    my_session_factory = SignedCookieSessionFactory('ma_cle_secrete_super_securisee')

    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.set_session_factory(my_session_factory)
        
        # Injection des services dans le registre
        config.registry.service_oeuvre = service_oeuvre
        config.registry.service_auth = service_auth
        config.registry.service_emprunt = service_emprunt
        
        # Route statique pour les fichiers publics (PDFs)
        config.add_static_view(name='data', path=base_path)
        
        # --- DÉFINITION DES ROUTES (URL -> Nom de route) ---
        
        # Pages principales
        config.add_route('accueil', '/')
        config.add_route('login', '/login')
        config.add_route('logout', '/logout')
        config.add_route('signup', '/signup')
        
        # Actions Membres
        config.add_route('depot', '/depot')
        config.add_route('emprunter', '/emprunter/{id}')
        config.add_route('lire_emprunt', '/lire_emprunt/{id}') # Lecture déchiffrée
        
        # Actions Modération / Admin
        config.add_route('moderation', '/moderation')
        config.add_route('valider_form', '/valider_form')
        config.add_route('rejeter', '/rejeter/{id}')
        config.add_route('download_md', '/download_md/{id}')
        
        # Tâches Automatisées (Celle qui manquait !)
        config.add_route('admin_cron_droits', '/admin/check_rights')
        
        # Scan des vues pour associer le code aux routes
        config.scan('.views')

    return config.make_wsgi_app()