# src/app/__init__.py
import os
from pyramid.config import Configurator
from pyramid.response import Response  # <--- N'oubliez pas cet import !
from src.app.infra.repositories import FileSystemGitRepository
from src.app.domain.services import ServiceOeuvre

def main(global_config, **settings):
    """ Fonction principale qui construit l'application WSGI. """
    with Configurator(settings=settings) as config:
        
        # 1. Configuration des routes et des vues
        config.include('.routes')
        config.scan('.views')

        # 2. Injection de Dépendances
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        print(f"[Pyramid] Démarrage avec stockage dans : {root_dir}")

        repo = FileSystemGitRepository(root_dir)
        service = ServiceOeuvre(repo)
        config.registry.service_oeuvre = service

        # 3. Gestion du CORS (Correction ici)
        config.add_tween('src.app.cors_tween_factory')

    return config.make_wsgi_app()

def cors_tween_factory(handler, registry):
    def cors_tween(request):
        # Si c'est une requête de pré-vérification (OPTIONS), on répond direct !
        if request.method == 'OPTIONS':
            response = Response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST,GET,DELETE,PUT,OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
            return response

        # Sinon, on laisse passer la requête vers votre vue (api_depot, etc.)
        response = handler(request)
        
        # Et on ajoute les headers CORS à la réponse
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST,GET,DELETE,PUT,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
        
        return response
    return cors_tween