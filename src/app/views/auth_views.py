# ============================================
# FICHIER NOUVEAU: src/app/views/auth_views.py
# ============================================
"""
Vues pour l'authentification (login, register, refresh)
"""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest, HTTPUnauthorized
from src.app.auth.jwt_handler import JWTHandler
from src.app.domain.modeles import Utilisateur, PermissionsSysteme


@view_config(route_name='auth_register', renderer='json', request_method='POST')
def register(request):
    """
    POST /api/auth/register
    
    Body JSON:
    {
        "email": "user@example.com",
        "password": "motdepasse",
        "nom": "Dupont",
        "prenom": "Jean"
    }
    
    Returns:
    {
        "success": true,
        "token": "JWT_TOKEN",
        "user": {...}
    }
    """
    try:
        data = request.json_body
    except:
        request.response.status = 400
        return {"error": "Body JSON requis"}
    
    email = data.get('email')
    password = data.get('password')
    nom = data.get('nom', '')
    prenom = data.get('prenom', '')
    
    # Validation
    if not email or not password:
        request.response.status = 400
        return {"error": "Email et mot de passe requis"}
    
    if len(password) < 6:
        request.response.status = 400
        return {"error": "Le mot de passe doit contenir au moins 6 caractères"}
    
    depot_users = request.registry.depot_utilisateurs
    
    # Vérifier si l'email existe déjà
    if depot_users.user_exists(email):
        request.response.status = 400
        return {"error": "Cet email est déjà utilisé"}
    
    # Créer l'utilisateur
    try:
        user = Utilisateur(nom, prenom, email, password)
        
        # Attribuer le rôle Membre par défaut
        role_membre = PermissionsSysteme.creer_role_membre()
        user.ajouter_role(role_membre)
        
        # Sauvegarder
        depot_users.sauvegarder(user)
        
        # Générer le token JWT
        token = JWTHandler.generer_token(user)
        
        return {
            "success": True,
            "message": "Inscription réussie",
            "token": token,
            "user": {
                "email": user.email,
                "nom": user.nom,
                "prenom": user.prenom,
                "roles": [r.nom_role for r in user.roles]
            }
        }
    
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors de l'inscription : {str(e)}"}


@view_config(route_name='auth_login', renderer='json', request_method='POST')
def login(request):
    """
    POST /api/auth/login
    
    Body JSON:
    {
        "email": "user@example.com",
        "password": "motdepasse"
    }
    
    Returns:
    {
        "success": true,
        "token": "JWT_TOKEN",
        "user": {...}
    }
    """
    try:
        data = request.json_body
    except:
        request.response.status = 400
        return {"error": "Body JSON requis"}
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        request.response.status = 400
        return {"error": "Email et mot de passe requis"}
    
    depot_users = request.registry.depot_utilisateurs
    
    # Récupérer l'utilisateur
    user = depot_users.get_by_email(email)
    
    if not user:
        request.response.status = 401
        return {"error": "Identifiants invalides"}
    
    # Vérifier le mot de passe
    if not user.verifier_mdp(password):
        request.response.status = 401
        return {"error": "Identifiants invalides"}
    
    # Générer le token JWT
    token = JWTHandler.generer_token(user)
    
    return {
        "success": True,
        "message": "Connexion réussie",
        "token": token,
        "user": {
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "roles": [r.nom_role for r in user.roles]
        }
    }


@view_config(route_name='auth_refresh', renderer='json', request_method='POST')
def refresh_token(request):
    """
    POST /api/auth/refresh
    
    Headers:
        Authorization: Bearer OLD_TOKEN
    
    Returns:
    {
        "success": true,
        "token": "NEW_JWT_TOKEN"
    }
    """
    # Récupérer le token depuis le header
    auth_header = request.headers.get('Authorization')
    token = JWTHandler.extraire_token_de_header(auth_header)
    
    if not token:
        request.response.status = 401
        return {"error": "Token manquant"}
    
    # Vérifier le token
    payload = JWTHandler.verifier_token(token)
    
    if not payload:
        request.response.status = 401
        return {"error": "Token invalide ou expiré"}
    
    # Récupérer l'utilisateur
    depot_users = request.registry.depot_utilisateurs
    user = depot_users.get_by_email(payload['email'])
    
    if not user:
        request.response.status = 401
        return {"error": "Utilisateur introuvable"}
    
    # Générer un nouveau token
    new_token = JWTHandler.generer_token(user)
    
    return {
        "success": True,
        "message": "Token rafraîchi",
        "token": new_token
    }