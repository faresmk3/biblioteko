# src/app/interface/web/__init__.py
import os
from pyramid.config import Configurator
from pyramid.session import SignedCookieSessionFactory

# Imports du backend
from infrastructure.repositories import FileSystemOeuvreRepository
from infrastructure.users_repo import FileSystemUserRepository
from services.service_oeuvre import ServiceOeuvre
from services.service_auth import ServiceAuth

def main(global_config, **settings):
    settings['pyramid.debug_all'] = True
    settings['pyramid.reload_templates'] = True

    base_path = os.path.abspath("bibliotheque_data")
    if not os.path.exists(base_path):
        os.makedirs(base_path)

    # Initialisation Repos & Services
    repo_oeuvre = FileSystemOeuvreRepository(base_path=base_path)
    repo_user = FileSystemUserRepository(base_path=base_path)
    
    service_oeuvre = ServiceOeuvre(repo_oeuvre)
    service_auth = ServiceAuth(repo_user)
    
    # CRÉATION ADMIN PAR DÉFAUT
    service_auth.ensure_admin_exists()

    # Configuration Session (Clé secrète pour signer les cookies)
    my_session_factory = SignedCookieSessionFactory('ma_cle_secrete_super_securisee')

    with Configurator(settings=settings) as config:
        config.include('pyramid_chameleon')
        config.set_session_factory(my_session_factory)
        
        # Injection
        config.registry.service_oeuvre = service_oeuvre
        config.registry.service_auth = service_auth
        
        config.add_static_view(name='data', path=base_path)
        
        # Routes
        config.add_route('accueil', '/')
        config.add_route('login', '/login')
        config.add_route('logout', '/logout')
        config.add_route('signup', '/signup')
        config.add_route('depot', '/depot')
        config.add_route('moderation', '/moderation')
        config.add_route('valider', '/valider/{id}')
        config.add_route('rejeter', '/rejeter/{id}')
        
        config.scan('.views')

    return config.make_wsgi_app()