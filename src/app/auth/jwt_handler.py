# ============================================
# FICHIER 4: src/app/auth/jwt_handler.py (NOUVEAU)
# ============================================
"""
Authentification JWT pour remplacer get_fake_user()
"""
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional, Dict
from src.app.domain.modeles import Utilisateur

SECRET_KEY = os.getenv('JWT_SECRET', 'CHANGEZ_MOI_EN_PRODUCTION')
ALGORITHM = "HS256"

class JWTHandler:
    """Gestion des tokens JWT"""
    
    @staticmethod
    def generer_token(utilisateur: Utilisateur) -> str:
        """
        Génère un JWT contenant :
        - email
        - roles
        - expiration (24h)
        """
        payload = {
            'email': utilisateur.email,
            'nom': utilisateur.nom,
            'prenom': utilisateur.prenom,
            'roles': [r.nom_role for r in utilisateur.roles],
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return token
    
    @staticmethod
    def verifier_token(token: str) -> Optional[Dict]:
        """
        Vérifie et décode un JWT
        Retourne les données ou None si invalide
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            print("[JWT] Token expiré")
            return None
        except jwt.InvalidTokenError:
            print("[JWT] Token invalide")
            return None
    
    @staticmethod
    def extraire_token_de_header(authorization_header: str) -> Optional[str]:
        """
        Extrait le token depuis 'Authorization: Bearer TOKEN'
        """
        if not authorization_header:
            return None
        
        parts = authorization_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
