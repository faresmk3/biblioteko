# src/app/routes.py

def includeme(config):
    # Route de test (Hello World)
    config.add_route('home', '/')

    # --- API REST (JSON) pour React ---
    
    # 1. Lister les œuvres (GET)
    config.add_route('api_oeuvres', '/api/oeuvres')
    
    # 2. Soumettre une œuvre (POST)
    config.add_route('api_depot', '/api/oeuvres/depot')
    
    # 3. Actions de modération (POST)
    # {id} sera remplacé par le nom du fichier (ex: Les_Miserables.md)
    config.add_route('api_traiter', '/api/oeuvres/{id}/traiter')
    config.add_route('api_valider', '/api/oeuvres/{id}/valider')
    config.add_route('api_rejeter', '/api/oeuvres/{id}/rejeter')


    # NOUVELLES ROUTES PDF
    config.add_route('api_depot_pdf', '/api/oeuvres/depot-pdf')
    config.add_route('api_reconvertir', '/api/oeuvres/{id}/reconvertir')
    # NOUVELLES ROUTES SÉPARÉES
    config.add_route('api_convertir_pdf', '/api/oeuvres/convertir-pdf')  # Conversion seule
    config.add_route('api_deposer_md', '/api/oeuvres/deposer-md')        # Dépôt Markdown