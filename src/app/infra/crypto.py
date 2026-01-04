# ============================================
# FICHIER 3: src/app/infra/crypto.py (NOUVEAU)
# ============================================
"""
Infrastructure : Service de chiffrement pour les emprunts
"""
from cryptography.fernet import Fernet
from typing import Optional

class ServiceChiffrement:
    """
    Chiffre/déchiffre les œuvres empruntées avec la clé de l'utilisateur
    Utilise Fernet (AES 128-bit)
    """
    
    @staticmethod
    def chiffrer(contenu: bytes, cle: bytes) -> bytes:
        """Chiffre le contenu avec la clé Fernet de l'utilisateur"""
        try:
            f = Fernet(cle)
            return f.encrypt(contenu)
        except Exception as e:
            raise RuntimeError(f"Erreur de chiffrement : {e}")
    
    @staticmethod
    def dechiffrer(contenu_chiffre: bytes, cle: bytes) -> bytes:
        """Déchiffre le contenu avec la clé Fernet de l'utilisateur"""
        try:
            f = Fernet(cle)
            return f.decrypt(contenu_chiffre)
        except Exception as e:
            raise RuntimeError(f"Erreur de déchiffrement : {e}")
    
    @staticmethod
    def generer_cle() -> bytes:
        """Génère une nouvelle clé Fernet"""
        return Fernet.generate_key()