# ============================================
# FICHIER 2: src/app/domain/services.py (VERSION COMPLÈTE)
# ============================================
"""
Services métier enrichis avec toutes les fonctionnalités
"""
import os
from typing import List, Optional, Dict
from datetime import datetime

from src.app.domain.modeles import (
    Oeuvre, Utilisateur, Emprunt, 
    CategorieOeuvre, StatutDroit
)

class ServiceOeuvre:
    """Service principal de gestion des œuvres"""
    
    def __init__(self, depot_git):
        self.depot = depot_git
        from src.app.infra.pdf_to_md import PDFToMarkdownConverter
        self.pdf_converter = PDFToMarkdownConverter(dpi=300, lang="fra")

    def lister_oeuvres_a_moderer(self, demandeur: Utilisateur) -> List[Oeuvre]:
        if not demandeur.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé : Vous n'êtes pas modérateur.")
        return self.depot.lister_oeuvres_en_attente()

    def recuperer_oeuvre(self, id_oeuvre: str) -> Optional[Oeuvre]:
        return self.depot.get_oeuvre_by_id(id_oeuvre)

    def traiter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str) -> Oeuvre:
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        if not oeuvre:
            raise ValueError("Œuvre introuvable.")
        oeuvre.traiter()
        self.depot.sauvegarder(oeuvre)
        return oeuvre

    def valider_oeuvre(self, biblio: Utilisateur, id_oeuvre: str, destination: str):
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        oeuvre.accepter()
        self.depot.deplacer_vers_catalogue(oeuvre, destination)
        return f"L'œuvre '{oeuvre.titre}' a été validée."

    def rejeter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str, motif: str):
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        oeuvre.refuser()
        self.depot.archiver_rejet(oeuvre, motif)
        return f"L'œuvre a été rejetée."

    def soumettre_oeuvre(self, oeuvre: Oeuvre):
        self.depot.sauvegarder(oeuvre)
        return oeuvre
    
    # 🆕 CLASSIFICATION
    def classifier_oeuvre(
        self, 
        biblio: Utilisateur, 
        id_oeuvre: str, 
        categories: List[CategorieOeuvre]
    ):
        """Ajoute des catégories à une œuvre"""
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Seuls les modérateurs peuvent classifier.")
        
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        for cat in categories:
            oeuvre.ajouter_categorie(cat)
        
        self.depot.sauvegarder(oeuvre)
        return oeuvre
    
    def rechercher_par_categorie(self, categorie: CategorieOeuvre) -> List[Oeuvre]:
        """Trouve toutes les œuvres d'une catégorie"""
        toutes = self.depot.lister_toutes_oeuvres()
        return [o for o in toutes if o.est_dans_categorie(categorie)]


class ServiceEmprunt:
    """
    🆕 NOUVEAU SERVICE : Gestion des emprunts
    """
    def __init__(self, depot_git, service_chiffrement):
        self.depot = depot_git
        self.crypto = service_chiffrement
        self.emprunts_actifs: Dict[str, List[Emprunt]] = {}  # email -> [Emprunt]
    
    def emprunter_oeuvre(
        self, 
        utilisateur: Utilisateur, 
        id_oeuvre: str,
        duree_jours: int = 14
    ) -> Emprunt:
        """
        SCÉNARIO : Emprunter une œuvre
        1. Vérifier les droits
        2. Vérifier disponibilité
        3. Chiffrer l'œuvre
        4. Créer l'emprunt
        """
        # 1. Vérification permissions
        if not utilisateur.a_la_permission("peut_emprunter_oeuvre"):
            raise PermissionError("Vous ne pouvez pas emprunter d'œuvres.")
        
        # 2. Récupération œuvre
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        if not oeuvre:
            raise ValueError("Œuvre introuvable.")
        
        # 2b. Vérifier que l'œuvre n'est pas déjà empruntée
        if self._est_deja_emprunte(utilisateur.email, id_oeuvre):
            raise ValueError("Vous avez déjà emprunté cette œuvre.")
        
        # 3. Chiffrement du fichier
        contenu_fichier = self.depot.lire_contenu_oeuvre(id_oeuvre)
        contenu_chiffre = self.crypto.chiffrer(contenu_fichier, utilisateur.cle_chiffrement)
        
        # 4. Création de l'emprunt
        emprunt = Emprunt(oeuvre, utilisateur, duree_jours)
        emprunt.fichier_chiffre = contenu_chiffre
        
        # 5. Enregistrement
        if utilisateur.email not in self.emprunts_actifs:
            self.emprunts_actifs[utilisateur.email] = []
        self.emprunts_actifs[utilisateur.email].append(emprunt)
        
        # 6. Sauvegarde dans Git
        self.depot.sauvegarder_emprunt(emprunt)
        
        print(f"[Emprunt] {utilisateur.email} a emprunté '{oeuvre.titre}' pour {duree_jours}j")
        return emprunt
    
    def retourner_oeuvre(self, utilisateur: Utilisateur, id_emprunt: str):
        """SCÉNARIO : Retourner une œuvre"""
        emprunt = self._trouver_emprunt(utilisateur.email, id_emprunt)
        if not emprunt:
            raise ValueError("Emprunt introuvable.")
        
        emprunt.retourner()
        self.depot.supprimer_emprunt(id_emprunt)
        
        # Suppression du fichier chiffré
        self.emprunts_actifs[utilisateur.email].remove(emprunt)
        
        return f"Œuvre '{emprunt.oeuvre_titre}' retournée avec succès."
    
    def lister_mes_emprunts(self, utilisateur: Utilisateur) -> List[Emprunt]:
        """SCÉNARIO : Consulter mes emprunts"""
        return self.emprunts_actifs.get(utilisateur.email, [])
    
    def verifier_emprunts_expires(self) -> List[Emprunt]:
        """
        TÂCHE PÉRIODIQUE : Détecter les emprunts expirés
        À exécuter avec un cron
        """
        expires = []
        for email, emprunts in self.emprunts_actifs.items():
            for emp in emprunts:
                if emp.est_expire():
                    expires.append(emp)
        return expires
    
    def _est_deja_emprunte(self, email: str, id_oeuvre: str) -> bool:
        emprunts = self.emprunts_actifs.get(email, [])
        return any(e.oeuvre_id == id_oeuvre and e.est_actif for e in emprunts)
    
    def _trouver_emprunt(self, email: str, id_emprunt: str) -> Optional[Emprunt]:
        emprunts = self.emprunts_actifs.get(email, [])
        for emp in emprunts:
            if emp.id == id_emprunt:
                return emp
        return None
    


    def lister_mes_emprunts(self, utilisateur: Utilisateur) -> List[Emprunt]:
        """
        SCÉNARIO : Consulter mes emprunts ACTIFS uniquement
        
        Returns:
            List[Emprunt]: Liste des emprunts actifs de l'utilisateur
        """
        tous_emprunts = self.emprunts_actifs.get(utilisateur.email, [])
        
        # ✅ CORRECTION : Ne retourner que les emprunts actifs
        return [e for e in tous_emprunts if e.est_actif]
    
    def retourner_oeuvre(self, utilisateur: Utilisateur, id_emprunt: str):
        """SCÉNARIO : Retourner une œuvre"""
        emprunt = self._trouver_emprunt(utilisateur.email, id_emprunt)
        if not emprunt:
            raise ValueError("Emprunt introuvable.")
        
        emprunt.retourner()
        self.depot.supprimer_emprunt(id_emprunt)
        
        # ✅ CORRECTION : Ne pas supprimer de la liste, juste marquer comme inactif
        # La méthode lister_mes_emprunts filtrera les inactifs
        
        return f"Œuvre '{emprunt.oeuvre_titre}' retournée avec succès."
    

    def recuperer_oeuvre(self, id_oeuvre: str) -> Optional[Oeuvre]:
        """
        Alias pour get_oeuvre_by_id
        Permet de garder une API cohérente entre service et repository
        """
        return self.depot.get_oeuvre_by_id(id_oeuvre)


class ServiceReconnaissanceIA:
    """
    🆕 NOUVEAU SERVICE : Reconnaissance multi-IA
    Intègre Gemini et Pixtral en plus de Tesseract
    """
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.pixtral_api_key = os.getenv('PIXTRAL_API_KEY')
        
        if not self.gemini_api_key:
            print("⚠️ GEMINI_API_KEY non définie dans .env")
        if not self.pixtral_api_key:
            print("⚠️ PIXTRAL_API_KEY non définie dans .env")
    
    def reconnaitre_avec_gemini(self, image_path: str) -> str:
        """
        Appelle l'API Gemini Vision pour extraire le texte
        Documentation : https://ai.google.dev/gemini-api/docs/vision
        """
        if not self.gemini_api_key:
            return "[Gemini non configuré]"
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Ouverture de l'image
            from PIL import Image
            img = Image.open(image_path)
            
            # Prompt OCR
            response = model.generate_content([
                "Extrais tout le texte de cette image. Retourne uniquement le texte, sans commentaire.",
                img
            ])
            
            return response.text
        
        except Exception as e:
            print(f"[Gemini] Erreur : {e}")
            return f"[Erreur Gemini : {e}]"
    
    def reconnaitre_avec_pixtral(self, image_path: str) -> str:
        """
        Appelle l'API Pixtral (Mistral AI) pour extraire le texte
        Documentation : https://docs.mistral.ai/capabilities/vision/
        """
        if not self.pixtral_api_key:
            return "[Pixtral non configuré]"
        
        try:
            from mistralai import Mistral
            import base64
            
            # Lecture de l'image en base64
            with open(image_path, "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            client = Mistral(api_key=self.pixtral_api_key)
            
            response = client.chat.complete(
                model="pixtral-12b-2409",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Extrais tout le texte de cette image."},
                            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_b64}"}
                        ]
                    }
                ]
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"[Pixtral] Erreur : {e}")
            return f"[Erreur Pixtral : {e}]"
    
    def reconnaitre_avec_tesseract(self, image_path: str, lang: str = "fra") -> str:
        """OCR classique avec Tesseract (déjà implémenté)"""
        import pytesseract
        from PIL import Image
        
        img = Image.open(image_path)
        return pytesseract.image_to_string(img, lang=lang)
    
    def comparer_trois_ia(self, image_path: str) -> Dict[str, str]:
        """
        FONCTIONNALITÉ CLEF : Compare les 3 IA
        Retourne un dictionnaire avec les 3 résultats
        """
        print(f"[Multi-IA] Analyse de {image_path}...")
        
        resultats = {
            "tesseract": self.reconnaitre_avec_tesseract(image_path),
            "gemini": self.reconnaitre_avec_gemini(image_path),
            "pixtral": self.reconnaitre_avec_pixtral(image_path)
        }
        
        # Calcul de scores basiques
        for ia, texte in resultats.items():
            nb_mots = len(texte.split())
            print(f"  - {ia.upper()}: {nb_mots} mots")
        
        return resultats
    
    def meilleur_resultat(self, resultats: Dict[str, str]) -> str:
        """
        Sélectionne le meilleur résultat (le plus long)
        Stratégie simple : plus de mots = meilleure qualité
        """
        scores = {ia: len(texte.split()) for ia, texte in resultats.items()}
        meilleur_ia = max(scores, key=scores.get)
        
        print(f"[Multi-IA] Meilleur résultat : {meilleur_ia.upper()} ({scores[meilleur_ia]} mots)")
        return resultats[meilleur_ia]