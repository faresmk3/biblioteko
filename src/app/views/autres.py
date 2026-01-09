# ============================================
# FICHIER NOUVEAU: src/app/views/autres.py
# ============================================
"""
Vues diverses : home, dépôt MD, rejet
"""
from pyramid.view import view_config
from src.app.auth.decorators import require_auth, require_permission
from src.app.domain.modeles import Utilisateur, Oeuvre


@view_config(route_name='home', renderer='json', request_method='GET')
def home(request):
    """
    GET /
    
    Page d'accueil de l'API - Documentation
    """
    return {
        "nom": "Biblioteko Backend API",
        "version": "1.0.0",
        "description": "API pour la gestion de bibliothèque culturelle collaborative",
        "documentation": {
            "authentification": {
                "register": "POST /api/auth/register",
                "login": "POST /api/auth/login",
                "refresh": "POST /api/auth/refresh"
            },
            "oeuvres": {
                "lister": "GET /api/oeuvres",
                "depot_simple": "POST /api/oeuvres/depot",
                "depot_pdf": "POST /api/oeuvres/depot-pdf",
                "convertir_pdf": "POST /api/oeuvres/convertir-pdf",
                "deposer_md": "POST /api/oeuvres/deposer-md",
                "traiter": "POST /api/oeuvres/{id}/traiter",
                "valider": "POST /api/oeuvres/{id}/valider",
                "rejeter": "POST /api/oeuvres/{id}/rejeter",
                "reconvertir": "POST /api/oeuvres/{id}/reconvertir",
                "classifier": "POST /api/oeuvres/{id}/classifier",
                "rechercher_categorie": "GET /api/oeuvres/categorie/{cat}"
            },
            "emprunts": {
                "emprunter": "POST /api/emprunts/emprunter",
                "mes_emprunts": "GET /api/emprunts/mes-emprunts",
                "retourner": "POST /api/emprunts/{id}/retourner",
                "renouveler": "POST /api/emprunts/{id}/renouveler"
            },
            "multi_ia": {
                "ocr_multi_ia": "POST /api/oeuvres/{id}/ocr-multi-ia",
                "comparer_ia": "GET /api/oeuvres/{id}/comparer-ia"
            },
            "catalogue": {
                "fond_commun": "GET /api/catalogue/fond-commun",
                "sequestre": "GET /api/catalogue/sequestre"
            }
        },
        "statut": "OK",
        "timestamp": "2026-01-05"
    }


# @view_config(route_name='api_deposer_md', renderer='json', request_method='POST')
# @require_auth
# def deposer_md(request):
#     """
#     POST /api/oeuvres/deposer-md
    
#     Headers:
#         Authorization: Bearer TOKEN
    
#     Body: multipart/form-data
#     - md: Fichier Markdown
#     - titre: Titre de l'œuvre
#     - auteur: Auteur de l'œuvre
    
#     Permet de déposer directement un fichier Markdown
#     (utile pour les œuvres déjà converties)
#     """
#     service = request.registry.service_oeuvre
#     depot_users = request.registry.depot_utilisateurs
    
#     # Récupération des données
#     titre = request.POST.get('titre')
#     auteur = request.POST.get('auteur', 'Auteur inconnu')
#     md_file = request.POST.get('md')
    
#     if not titre:
#         request.response.status = 400
#         return {"error": "Titre requis"}
    
#     if not md_file or not hasattr(md_file, 'filename'):
#         request.response.status = 400
#         return {"error": "Fichier Markdown requis"}
    
#     # Récupérer l'utilisateur authentifié
#     user = depot_users.get_by_email(request.user_email)
    
#     try:
#         # Lire le contenu du fichier MD
#         md_file.file.seek(0)
#         contenu_md = md_file.file.read().decode('utf-8')
        
#         # Créer l'œuvre
#         oeuvre = Oeuvre(titre, auteur, md_file.filename, user)
        
#         # Ajouter le contenu MD dans les métadonnées
#         oeuvre.set_metadonnee("contenu_md", contenu_md)
        
#         # Sauvegarder
#         service.soumettre_oeuvre(oeuvre)
        
#         return {
#             "success": True,
#             "message": f"Fichier Markdown '{titre}' déposé avec succès",
#             "oeuvre": {
#                 "id": oeuvre.fichier_nom,
#                 "titre": oeuvre.titre,
#                 "auteur": oeuvre.auteur,
#                 "etat": oeuvre.etat.nom
#             }
#         }
    
#     except Exception as e:
#         request.response.status = 500
#         return {"error": f"Erreur lors du dépôt : {str(e)}"}


@view_config(route_name='api_rejeter', renderer='json', request_method='POST')
@require_permission('peut_moderer_oeuvre')
def api_rejeter(request):
    """
    POST /api/oeuvres/{id}/rejeter
    
    Headers:
        Authorization: Bearer TOKEN (avec permission modérer)
    
    Body JSON:
    {
        "motif": "Raison du rejet"
    }
    """
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    
    try:
        data = request.json_body
        motif = data.get('motif', 'Non spécifié')
    except:
        motif = 'Non spécifié'
    
    try:
        msg = service.rejeter_oeuvre(request.user, id_oeuvre, motif)
        
        return {
            "success": True,
            "message": msg,
            "motif": motif
        }
    
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    except ValueError as e:
        request.response.status = 404
        return {"error": str(e)}
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors du rejet : {str(e)}"}


@view_config(route_name='api_health', renderer='json', request_method='GET')
def health_check(request):
    """
    GET /api/health
    
    Health check pour monitoring
    (Route bonus non définie dans routes.py mais utile)
    """
    import os
    
    # Vérifier que les dossiers nécessaires existent
    repo = request.registry.repo_oeuvres
    dossiers = ["a_moderer", "fond_commun", "sequestre", "archives", "emprunts"]
    
    checks = {}
    for dossier in dossiers:
        path = os.path.join(repo.root_dir, "data", dossier)
        checks[dossier] = os.path.exists(path)
    
    # Vérifier que les services sont disponibles
    services = {
        "service_oeuvre": hasattr(request.registry, 'service_oeuvre'),
        "service_emprunt": hasattr(request.registry, 'service_emprunt'),
        "depot_utilisateurs": hasattr(request.registry, 'depot_utilisateurs'),
        "repo_oeuvres": hasattr(request.registry, 'repo_oeuvres')
    }
    
    all_ok = all(checks.values()) and all(services.values())
    
    return {
        "status": "OK" if all_ok else "WARNING",
        "dossiers": checks,
        "services": services,
        "timestamp": "2026-01-05"
    }