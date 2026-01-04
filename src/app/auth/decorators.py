# ============================================
# FICHIER 5: src/app/auth/decorators.py (NOUVEAU)
# ============================================
"""
Décorateurs pour protéger les routes avec JWT
"""
from functools import wraps
from pyramid.httpexceptions import HTTPUnauthorized, HTTPForbidden
from src.app.auth.jwt_handler import JWTHandler

def require_auth(func):
    """Décorateur : Nécessite un token JWT valide"""
    @wraps(func)
    def wrapper(request):
        # 1. Extraction du token
        auth_header = request.headers.get('Authorization')
        token = JWTHandler.extraire_token_de_header(auth_header)
        
        if not token:
            raise HTTPUnauthorized("Token manquant")
        
        # 2. Vérification
        payload = JWTHandler.verifier_token(token)
        if not payload:
            raise HTTPUnauthorized("Token invalide ou expiré")
        
        # 3. Injection des données dans request
        request.user_email = payload['email']
        request.user_roles = payload['roles']
        
        return func(request)
    
    return wrapper

def require_permission(permission_name: str):
    """Décorateur : Nécessite une permission spécifique"""
    def decorator(func):
        @wraps(func)
        def wrapper(request):
            # Vérifie d'abord l'auth
            if not hasattr(request, 'user_email'):
                raise HTTPUnauthorized("Authentification requise")
            
            # Récupère l'utilisateur complet depuis le dépôt
            user = request.registry.depot_utilisateurs.get_by_email(request.user_email)
            
            if not user.a_la_permission(permission_name):
                raise HTTPForbidden(f"Permission '{permission_name}' requise")
            
            request.user = user
            return func(request)
        
        return wrapper
    return decorator