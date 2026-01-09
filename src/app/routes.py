# ============================================
# FICHIER COMPLET: src/app/routes.py
# ============================================
"""
Toutes les routes API du système
"""

def includeme(config):
    # ====================================
    # ROUTES PRINCIPALES
    # ====================================
    
    # Accueil
    config.add_route('home', '/')
    
    # ====================================
    # AUTHENTIFICATION
    # ====================================
    config.add_route('auth_login', '/api/auth/login')
    config.add_route('auth_register', '/api/auth/register')
    config.add_route('auth_refresh', '/api/auth/refresh')
    
    # ====================================
    # ŒUVRES - Gestion et Modération
    # ====================================
    config.add_route('api_oeuvres', '/api/oeuvres')
    config.add_route('api_depot', '/api/oeuvres/depot')
    config.add_route('api_depot_pdf', '/api/oeuvres/depot-pdf')
    config.add_route('api_convertir_pdf', '/api/oeuvres/convertir-pdf')
    config.add_route('api_deposer_md', '/api/oeuvres/deposer-md')
    
    # Actions de modération
    config.add_route('api_traiter', '/api/oeuvres/{id}/traiter')
    config.add_route('api_valider', '/api/oeuvres/{id}/valider')
    config.add_route('api_rejeter', '/api/oeuvres/{id}/rejeter')
    config.add_route('api_reconvertir', '/api/oeuvres/{id}/reconvertir')
    
    # ====================================
    # CLASSIFICATION
    # ====================================
    config.add_route('api_classifier', '/api/oeuvres/{id}/classifier')
    config.add_route('api_rechercher_categorie', '/api/oeuvres/categorie/{cat}')
    # Route bonus pour lister les catégories disponibles
    config.add_route('api_categories_disponibles', '/api/categories')
    
    # ====================================
    # MULTI-IA (OCR)
    # ====================================
    config.add_route('api_ocr_multi_ia', '/api/oeuvres/{id}/ocr-multi-ia')
    config.add_route('api_comparer_ia', '/api/oeuvres/{id}/comparer-ia')
    # Route bonus pour obtenir le résultat d'une IA spécifique
    config.add_route('api_resultat_ia', '/api/oeuvres/{id}/resultat-ia/{ia}')
    
    # ====================================
    # EMPRUNTS
    # ====================================
    config.add_route('api_emprunter', '/api/emprunts/emprunter')
    config.add_route('api_mes_emprunts', '/api/emprunts/mes-emprunts')
    config.add_route('api_retourner', '/api/emprunts/{id}/retourner')
    config.add_route('api_renouveler', '/api/emprunts/{id}/renouveler')
    
    # ====================================
    # CATALOGUE
    # ====================================
    config.add_route('api_fond_commun', '/api/catalogue/fond-commun')
    config.add_route('api_sequestre', '/api/catalogue/sequestre')
    # Routes bonus pour statistiques et détails
    config.add_route('api_catalogues_stats', '/api/catalogue/stats')
    config.add_route('api_oeuvre_detail', '/api/catalogue/oeuvre/{id}')
    
    # ====================================
    # UTILITAIRES
    # ====================================
    # Route bonus pour health check
    config.add_route('api_health', '/api/health')