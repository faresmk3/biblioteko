# ============================================
# FICHIER 6: src/app/routes.py (VERSION COMPLÈTE)
# ============================================
"""
Toutes les routes API du système
"""

def includeme(config):
    # --- Routes existantes ---
    config.add_route('home', '/')
    config.add_route('api_oeuvres', '/api/oeuvres')
    config.add_route('api_depot', '/api/oeuvres/depot')
    config.add_route('api_traiter', '/api/oeuvres/{id}/traiter')
    config.add_route('api_valider', '/api/oeuvres/{id}/valider')
    config.add_route('api_rejeter', '/api/oeuvres/{id}/rejeter')
    config.add_route('api_depot_pdf', '/api/oeuvres/depot-pdf')
    config.add_route('api_reconvertir', '/api/oeuvres/{id}/reconvertir')
    config.add_route('api_convertir_pdf', '/api/oeuvres/convertir-pdf')
    config.add_route('api_deposer_md', '/api/oeuvres/deposer-md')
    
    # 🆕 NOUVELLES ROUTES : Authentification
    config.add_route('auth_login', '/api/auth/login')
    config.add_route('auth_register', '/api/auth/register')
    config.add_route('auth_refresh', '/api/auth/refresh')
    
    # 🆕 NOUVELLES ROUTES : Emprunts
    config.add_route('api_emprunter', '/api/emprunts/emprunter')
    config.add_route('api_retourner', '/api/emprunts/{id}/retourner')
    config.add_route('api_mes_emprunts', '/api/emprunts/mes-emprunts')
    config.add_route('api_renouveler', '/api/emprunts/{id}/renouveler')
    
    # 🆕 NOUVELLES ROUTES : Classification
    config.add_route('api_classifier', '/api/oeuvres/{id}/classifier')
    config.add_route('api_rechercher_categorie', '/api/oeuvres/categorie/{cat}')
    
    # 🆕 NOUVELLES ROUTES : Multi-IA
    config.add_route('api_ocr_multi_ia', '/api/oeuvres/{id}/ocr-multi-ia')
    config.add_route('api_comparer_ia', '/api/oeuvres/{id}/comparer-ia')
    
    # 🆕 NOUVELLES ROUTES : Catalogue
    config.add_route('api_fond_commun', '/api/catalogue/fond-commun')
    config.add_route('api_sequestre', '/api/catalogue/sequestre')
