# ============================================
# FICHIER COMPLET: src/app/views/emprunts.py
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
    POST /api/emprunts/emprunter
    
    Headers:
        Authorization: Bearer TOKEN
    
    Body JSON:
    {
        "id_oeuvre": "Livre_Test.md",
        "duree_jours": 14
    }
    """
    service_emprunt = request.registry.service_emprunt
    depot_users = request.registry.depot_utilisateurs
    
    try:
        data = request.json_body
    except:
        request.response.status = 400
        return {"error": "Body JSON requis"}
    
    id_oeuvre = data.get('id_oeuvre')
    duree = data.get('duree_jours', 14)
    
    if not id_oeuvre:
        request.response.status = 400
        return {"error": "id_oeuvre requis"}
    
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
                "date_debut": emprunt.date_debut.isoformat(),
                "date_fin": emprunt.date_fin.isoformat(),
                "jours_restants": emprunt.jours_restants()
            }
        }
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    except ValueError as e:
        request.response.status = 400
        return {"error": str(e)}
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur interne : {str(e)}"}


@view_config(route_name='api_mes_emprunts', renderer='json', request_method='GET')
@require_auth
def api_mes_emprunts(request):
    """
    GET /api/emprunts/mes-emprunts
    
    Headers:
        Authorization: Bearer TOKEN
    
    Returns:
    {
        "emprunts": [...]
    }
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
                "oeuvre_id": e.oeuvre_id,
                "date_debut": e.date_debut.isoformat(),
                "date_fin": e.date_fin.isoformat(),
                "jours_restants": e.jours_restants(),
                "est_expire": e.est_expire(),
                "est_actif": e.est_actif
            }
            for e in emprunts
        ]
    }


@view_config(route_name='api_retourner', renderer='json', request_method='POST')
@require_auth
def api_retourner(request):
    """
    POST /api/emprunts/{id}/retourner
    
    Headers:
        Authorization: Bearer TOKEN
    """
    service_emprunt = request.registry.service_emprunt
    depot_users = request.registry.depot_utilisateurs
    
    id_emprunt = request.matchdict['id']
    user = depot_users.get_by_email(request.user_email)
    
    try:
        msg = service_emprunt.retourner_oeuvre(user, id_emprunt)
        return {"success": True, "message": msg}
    except ValueError as e:
        request.response.status = 404
        return {"error": str(e)}
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


@view_config(route_name='api_renouveler', renderer='json', request_method='POST')
@require_auth
def api_renouveler(request):
    """
    POST /api/emprunts/{id}/renouveler
    
    Headers:
        Authorization: Bearer TOKEN
    
    Body JSON (optionnel):
    {
        "jours": 14
    }
    """
    service_emprunt = request.registry.service_emprunt
    depot_users = request.registry.depot_utilisateurs
    
    id_emprunt = request.matchdict['id']
    
    # Récupérer le nombre de jours (14 par défaut)
    try:
        data = request.json_body
        jours = data.get('jours', 14)
    except:
        jours = 14
    
    user = depot_users.get_by_email(request.user_email)
    
    try:
        # Récupérer l'emprunt
        emprunt = service_emprunt._trouver_emprunt(user.email, id_emprunt)
        
        if not emprunt:
            request.response.status = 404
            return {"error": "Emprunt introuvable"}
        
        if not emprunt.est_actif:
            request.response.status = 400
            return {"error": "Cet emprunt n'est plus actif"}
        
        # Renouveler
        emprunt.renouveler(jours)
        
        # Sauvegarder la modification
        service_emprunt.depot.sauvegarder_emprunt(emprunt)
        
        return {
            "success": True,
            "message": f"Emprunt prolongé de {jours} jours",
            "emprunt": {
                "id": emprunt.id,
                "nouvelle_date_fin": emprunt.date_fin.isoformat(),
                "jours_restants": emprunt.jours_restants()
            }
        }
    
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors du renouvellement : {str(e)}"}