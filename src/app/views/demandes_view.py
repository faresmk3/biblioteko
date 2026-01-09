# ============================================
# NOUVEAU FICHIER: src/app/views/demandes_views.py
# ============================================
"""
Vues API pour la gestion des demandes de promotion
"""
from pyramid.view import view_config
from src.app.auth.decorators import require_auth, require_permission


# ============================================
# ENDPOINTS POUR LES MEMBRES
# ============================================

@view_config(route_name='demande_soumettre', renderer='json', request_method='POST')
@require_auth
def soumettre_demande(request):
    """
    Un membre soumet une demande pour devenir bibliothécaire
    
    POST /api/demandes/soumettre
    Headers: Authorization: Bearer TOKEN
    Body: {"motivation": "Je souhaite contribuer..."}
    
    Returns:
        {
            "success": true,
            "message": "Demande soumise avec succès",
            "demande": {
                "id": "demande_abc123",
                "statut": "en_attente",
                "date_demande": "2025-01-09T10:30:00"
            }
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    depot_users = request.registry.depot_utilisateurs
    
    try:
        data = request.json_body
    except:
        request.response.status = 400
        return {"error": "Body JSON requis"}
    
    motivation = data.get('motivation', '')
    
    if not motivation or len(motivation) < 10:
        request.response.status = 400
        return {"error": "Motivation requise (minimum 10 caractères)"}
    
    # Récupérer l'utilisateur connecté
    user = depot_users.get_by_email(request.user_email)
    
    try:
        demande = service_demandes.soumettre_demande(user, motivation)
        
        return {
            "success": True,
            "message": "Demande soumise avec succès. Un bibliothécaire la traitera prochainement.",
            "demande": demande.to_dict()
        }
    
    except ValueError as e:
        request.response.status = 400
        return {"error": str(e)}
    
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur serveur : {str(e)}"}


@view_config(route_name='demande_mes_demandes', renderer='json', request_method='GET')
@require_auth
def mes_demandes(request):
    """
    Consulter mes demandes de promotion
    
    GET /api/demandes/mes-demandes
    Headers: Authorization: Bearer TOKEN
    
    Returns:
        {
            "demandes": [
                {
                    "id": "...",
                    "motivation": "...",
                    "statut": "en_attente",
                    "date_demande": "...",
                    "delai_jours": 2
                }
            ]
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    depot_users = request.registry.depot_utilisateurs
    
    user = depot_users.get_by_email(request.user_email)
    
    try:
        demandes = service_demandes.consulter_mes_demandes(user)
        
        return {
            "success": True,
            "demandes": [d.to_dict() for d in demandes]
        }
    
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


@view_config(route_name='demande_annuler', renderer='json', request_method='POST')
@require_auth
def annuler_demande(request):
    """
    Annuler ma propre demande
    
    POST /api/demandes/{id}/annuler
    Headers: Authorization: Bearer TOKEN
    
    Returns:
        {
            "success": true,
            "message": "Demande annulée"
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    depot_users = request.registry.depot_utilisateurs
    
    id_demande = request.matchdict['id']
    user = depot_users.get_by_email(request.user_email)
    
    try:
        demande = service_demandes.annuler_ma_demande(user, id_demande)
        
        return {
            "success": True,
            "message": "Demande annulée avec succès",
            "demande": demande.to_dict()
        }
    
    except ValueError as e:
        request.response.status = 400
        return {"error": str(e)}
    
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


# ============================================
# ENDPOINTS POUR LES BIBLIOTHÉCAIRES
# ============================================

@view_config(route_name='demande_lister_attente', renderer='json', request_method='GET')
@require_permission('peut_traiter_demandes_bibliothecaire')
def lister_demandes_en_attente(request):
    """
    Liste toutes les demandes en attente de traitement
    
    GET /api/demandes/en-attente
    Headers: Authorization: Bearer BIBLIO_TOKEN
    
    Returns:
        {
            "demandes": [
                {
                    "id": "demande_abc",
                    "email_demandeur": "alice@test.fr",
                    "nom_demandeur": "Alice Martin",
                    "motivation": "Je souhaite...",
                    "date_demande": "2025-01-07T10:00:00",
                    "delai_jours": 2
                }
            ],
            "stats": {
                "total_en_attente": 3,
                "total_approuvees": 10,
                "total_refusees": 2
            }
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    
    # request.user est injecté par le décorateur require_permission
    try:
        demandes = service_demandes.lister_demandes_en_attente(request.user)
        stats = service_demandes.obtenir_statistiques(request.user)
        
        return {
            "success": True,
            "demandes": [d.to_dict() for d in demandes],
            "stats": stats
        }
    
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


@view_config(route_name='demande_approuver', renderer='json', request_method='POST')
@require_permission('peut_traiter_demandes_bibliothecaire')
def approuver_demande(request):
    """
    Approuver une demande (promeut automatiquement le membre)
    
    POST /api/demandes/{id}/approuver
    Headers: Authorization: Bearer BIBLIO_TOKEN
    
    Returns:
        {
            "success": true,
            "message": "alice@test.fr est maintenant bibliothécaire",
            "membre_promu": {
                "email": "alice@test.fr",
                "roles": ["Membre", "Bibliothécaire"]
            }
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    
    id_demande = request.matchdict['id']
    
    try:
        # Approuver et promouvoir
        membre_promu = service_demandes.approuver_demande(request.user, id_demande)
        
        return {
            "success": True,
            "message": f"{membre_promu.email} est maintenant bibliothécaire !",
            "membre_promu": {
                "email": membre_promu.email,
                "nom": membre_promu.nom,
                "prenom": membre_promu.prenom,
                "roles": [r.nom_role for r in membre_promu.roles]
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
        return {"error": f"Erreur serveur : {str(e)}"}


@view_config(route_name='demande_refuser', renderer='json', request_method='POST')
@require_permission('peut_traiter_demandes_bibliothecaire')
def refuser_demande(request):
    """
    Refuser une demande avec un motif
    
    POST /api/demandes/{id}/refuser
    Headers: Authorization: Bearer BIBLIO_TOKEN
    Body: {"motif": "Pas assez d'expérience"}
    
    Returns:
        {
            "success": true,
            "message": "Demande refusée"
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    
    try:
        data = request.json_body
    except:
        request.response.status = 400
        return {"error": "Body JSON requis"}
    
    id_demande = request.matchdict['id']
    motif = data.get('motif', 'Non spécifié')
    
    if len(motif) < 5:
        request.response.status = 400
        return {"error": "Motif requis (minimum 5 caractères)"}
    
    try:
        demande = service_demandes.refuser_demande(request.user, id_demande, motif)
        
        return {
            "success": True,
            "message": f"Demande de {demande.email_demandeur} refusée",
            "demande": demande.to_dict()
        }
    
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    
    except ValueError as e:
        request.response.status = 400
        return {"error": str(e)}
    
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


@view_config(route_name='demande_historique', renderer='json', request_method='GET')
@require_permission('peut_traiter_demandes_bibliothecaire')
def historique_demandes(request):
    """
    Historique complet des demandes (pour audit)
    
    GET /api/demandes/historique?limit=50
    Headers: Authorization: Bearer BIBLIO_TOKEN
    
    Returns:
        {
            "demandes": [...],
            "total": 50
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    
    # Récupérer le paramètre limit
    limit = int(request.params.get('limit', 50))
    
    try:
        demandes = service_demandes.lister_historique_complet(request.user, limit=limit)
        
        return {
            "success": True,
            "demandes": [d.to_dict() for d in demandes],
            "total": len(demandes)
        }
    
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


@view_config(route_name='demande_statistiques', renderer='json', request_method='GET')
@require_permission('peut_traiter_demandes_bibliothecaire')
def statistiques_demandes(request):
    """
    Statistiques complètes sur les demandes
    
    GET /api/demandes/statistiques
    Headers: Authorization: Bearer BIBLIO_TOKEN
    
    Returns:
        {
            "total": 20,
            "en_attente": 3,
            "approuvees": 15,
            "refusees": 2,
            "delai_moyen_jours": 2.5
        }
    """
    service_demandes = request.registry.service_demandes_promotion
    
    try:
        stats = service_demandes.obtenir_statistiques(request.user)
        
        return {
            "success": True,
            "stats": stats
        }
    
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}