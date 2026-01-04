# ============================================
# FICHIER 8: src/app/views/emprunts.py (NOUVEAU)
# ============================================
"""
Vues pour la gestion des emprunts
"""
from pyramid.view import view_config
from src.app.auth.decorators import require_auth, require_permission

@view_config(route_name='api_emprunter', renderer='json', request_method='POST')
@require_auth
def api_emprunter(request):
    """
    Emprunter une œuvre
    POST /api/emprunts/emprunter
    Headers: Authorization: Bearer TOKEN
    Body: {"id_oeuvre": "...", "duree_jours": 14}
    """
    service_emprunt = request.registry.service_emprunt
    depot_users = request.registry.depot_utilisateurs
    
    data = request.json_body
    id_oeuvre = data.get('id_oeuvre')
    duree = data.get('duree_jours', 14)
    
    # Récupérer l'utilisateur authentifié
    user = depot_users.get_by_email(request.user_email)
    
    try:
        emprunt = service_emprunt.emprunter_oeuvre(user, id_oeuvre, duree)
        
        return {
            "success": True,
            "message": f"Œuvre empruntée pour {duree} jours",
            "emprunt": {
                "id": emprunt.id,
                "oeuvre": emprunt.oeuvre_titre,
                "date_fin": emprunt.date_fin.isoformat(),
                "jours_restants": emprunt.jours_restants()
            }
        }
    except Exception as e:
        request.response.status = 400
        return {"error": str(e)}


@view_config(route_name='api_mes_emprunts', renderer='json', request_method='GET')
@require_auth
def api_mes_emprunts(request):
    """
    Liste mes emprunts actifs
    GET /api/emprunts/mes-emprunts
    Headers: Authorization: Bearer TOKEN
    """
    service_emprunt = request.registry.service_emprunt
    depot_users = request.registry.depot_utilisateurs
    
    user = depot_users.get_by_email(request.user_email)
    emprunts = service_emprunt.lister_mes_emprunts(user)
    
    return {
        "emprunts": [
            {
                "id": e.id,
                "oeuvre": e.oeuvre_titre,
                "date_debut": e.date_debut.isoformat(),
                "date_fin": e.date_fin.isoformat(),
                "jours_restants": e.jours_restants(),
                "est_expire": e.est_expire()
            }
            for e in emprunts
        ]
    }


@view_config(route_name='api_retourner', renderer='json', request_method='POST')
@require_auth
def api_retourner(request):
    """
    Retourner une œuvre empruntée
    POST /api/emprunts/{id}/retourner
    Headers: Authorization: Bearer TOKEN
    """
    service_emprunt = request.registry.service_emprunt
    depot_users = request.registry.depot_utilisateurs
    
    id_emprunt = request.matchdict['id']
    user = depot_users.get_by_email(request.user_email)
    
    try:
        msg = service_emprunt.retourner_oeuvre(user, id_emprunt)
        return {"success": True, "message": msg}
    except Exception as e:
        request.response.status = 400
        return {"error": str(e)}
