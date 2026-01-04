# ============================================
# FICHIER 7: src/app/views/auth.py (NOUVEAU)
# ============================================
"""
Vues pour l'authentification JWT
"""
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPUnauthorized
from src.app.domain.modeles import Utilisateur, PermissionsSysteme
from src.app.auth.jwt_handler import JWTHandler

@view_config(route_name='auth_register', renderer='json', request_method='POST')
def auth_register(request):
    """
    Inscription d'un nouvel utilisateur
    POST /api/auth/register
    Body: {"email": "...", "nom": "...", "prenom": "...", "password": "..."}
    """
    data = request.json_body
    
    email = data.get('email')
    nom = data.get('nom')
    prenom = data.get('prenom')
    password = data.get('password')
    
    if not all([email, nom, prenom, password]):
        request.response.status = 400
        return {"error": "Tous les champs sont requis"}
    
    # Vérifier si l'utilisateur existe déjà
    depot_users = request.registry.depot_utilisateurs
    if depot_users.existe(email):
        request.response.status = 409
        return {"error": "Cet email est déjà utilisé"}
    
    # Créer l'utilisateur
    nouveau_user = Utilisateur(nom, prenom, email, password)
    
    # Attribuer le rôle Membre par défaut
    role_membre = PermissionsSysteme.creer_role_membre()
    nouveau_user.ajouter_role(role_membre)
    
    # Sauvegarder
    depot_users.sauvegarder(nouveau_user)
    
    # Générer le token
    token = JWTHandler.generer_token(nouveau_user)
    
    return {
        "success": True,
        "message": "Compte créé avec succès",
        "token": token,
        "user": {
            "email": nouveau_user.email,
            "nom": nouveau_user.nom,
            "prenom": nouveau_user.prenom
        }
    }


@view_config(route_name='auth_login', renderer='json', request_method='POST')
def auth_login(request):
    """
    Connexion d'un utilisateur
    POST /api/auth/login
    Body: {"email": "...", "password": "..."}
    """
    data = request.json_body
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        request.response.status = 400
        return {"error": "Email et mot de passe requis"}
    
    # Récupérer l'utilisateur
    depot_users = request.registry.depot_utilisateurs
    user = depot_users.get_by_email(email)
    
    if not user:
        raise HTTPUnauthorized("Email ou mot de passe incorrect")
    
    # Vérifier le mot de passe
    if not user.verifier_mdp(password):
        raise HTTPUnauthorized("Email ou mot de passe incorrect")
    
    # Générer le token
    token = JWTHandler.generer_token(user)
    
    return {
        "success": True,
        "token": token,
        "user": {
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "roles": [r.nom_role for r in user.roles]
        }
    }
