# ============================================
# FICHIER NOUVEAU: src/app/views/classification.py
# ============================================
"""
Vues pour la classification des œuvres par catégories
"""
from pyramid.view import view_config
from src.app.auth.decorators import require_permission
from src.app.domain.modeles import CategorieOeuvre


@view_config(route_name='api_classifier', renderer='json', request_method='POST')
@require_permission('peut_moderer_oeuvre')
def classifier_oeuvre(request):
    """
    POST /api/oeuvres/{id}/classifier
    
    Headers:
        Authorization: Bearer TOKEN (avec permission modérer)
    
    Body JSON:
    {
        "categories": ["LIVRE_BD", "LIVRE_JEUNESSE"]
    }
    
    Returns:
    {
        "success": true,
        "oeuvre": "Titre",
        "categories": ["BD", "Jeunesse"]
    }
    """
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    
    try:
        data = request.json_body
    except:
        request.response.status = 400
        return {"error": "Body JSON requis"}
    
    categories_str = data.get('categories', [])
    
    if not categories_str:
        request.response.status = 400
        return {"error": "Au moins une catégorie requise"}
    
    # Convertir les strings en enum CategorieOeuvre
    categories = []
    categories_invalides = []
    
    for cat_str in categories_str:
        try:
            # Essayer de convertir en enum
            categorie = CategorieOeuvre[cat_str]
            categories.append(categorie)
        except KeyError:
            categories_invalides.append(cat_str)
    
    if categories_invalides:
        return {
            "error": f"Catégories invalides : {', '.join(categories_invalides)}",
            "categories_valides": [c.name for c in CategorieOeuvre]
        }
    
    try:
        oeuvre = service.classifier_oeuvre(request.user, id_oeuvre, categories)
        
        return {
            "success": True,
            "message": "Œuvre classifiée avec succès",
            "oeuvre": {
                "id": oeuvre.fichier_nom,
                "titre": oeuvre.titre,
                "categories": [c.value for c in oeuvre.categories]
            }
        }
    
    except ValueError as e:
        request.response.status = 404
        return {"error": str(e)}
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur interne : {str(e)}"}


@view_config(route_name='api_rechercher_categorie', renderer='json', request_method='GET')
def rechercher_par_categorie(request):
    """
    GET /api/oeuvres/categorie/{cat}
    
    Exemple: GET /api/oeuvres/categorie/LIVRE_BD
    
    Returns:
    {
        "categorie": "BD",
        "oeuvres": [...]
    }
    """
    service = request.registry.service_oeuvre
    cat_str = request.matchdict['cat']
    
    try:
        # Convertir en enum
        categorie = CategorieOeuvre[cat_str]
    except KeyError:
        request.response.status = 400
        return {
            "error": f"Catégorie invalide : {cat_str}",
            "categories_disponibles": [c.name for c in CategorieOeuvre]
        }
    
    try:
        oeuvres = service.rechercher_par_categorie(categorie)
        
        return {
            "categorie": categorie.value,
            "categorie_code": categorie.name,
            "nombre": len(oeuvres),
            "oeuvres": [
                {
                    "id": o.fichier_nom,
                    "titre": o.titre,
                    "auteur": o.auteur,
                    "etat": o.etat.nom
                }
                for o in oeuvres
            ]
        }
    
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors de la recherche : {str(e)}"}


@view_config(route_name='api_categories_disponibles', renderer='json', request_method='GET')
def liste_categories(request):
    """
    GET /api/categories
    
    Liste toutes les catégories disponibles
    (Route bonus non définie dans routes.py mais utile)
    """
    categories = [
        {
            "code": cat.name,
            "nom": cat.value,
            "type": cat.name.split('_')[0]  # LIVRE, MUSIQUE, VIDEO, ARTICLE
        }
        for cat in CategorieOeuvre
    ]
    
    # Grouper par type
    par_type = {}
    for cat in categories:
        type_cat = cat['type']
        if type_cat not in par_type:
            par_type[type_cat] = []
        par_type[type_cat].append(cat)
    
    return {
        "categories": categories,
        "par_type": par_type
    }