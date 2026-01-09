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

# src/app/domain/services.py - MÉTHODE CORRIGÉE

class ServiceOeuvre:
    """Service principal de gestion des œuvres"""
    
    def __init__(self, depot_git):
        self.depot = depot_git
        from src.app.infra.pdf_to_md import PDFToMarkdownConverter
        self.pdf_converter = PDFToMarkdownConverter(dpi=300, lang="fra")

    def soumettre_oeuvre(self, oeuvre: Oeuvre, contenu_markdown: str = None):
        """
        Soumet une œuvre avec son contenu Markdown
        
        Args:
            oeuvre: Objet Oeuvre avec les métadonnées
            contenu_markdown: Contenu complet du livre en Markdown (optionnel)
        """
        self.depot.sauvegarder(oeuvre, contenu_markdown=contenu_markdown)
        return oeuvre

    def soumettre_oeuvre_depuis_pdf(
        self, 
        pdf_path: str, 
        titre: str, 
        auteur: str, 
        soumis_par: Utilisateur
    ) -> Oeuvre:
        """
        Convertit un PDF en Markdown et soumet l'œuvre
        
        Args:
            pdf_path: Chemin vers le PDF
            titre: Titre de l'œuvre
            auteur: Auteur
            soumis_par: Utilisateur qui soumet
            
        Returns:
            Oeuvre: L'œuvre créée avec son contenu
        """
        # 1. Conversion PDF → Markdown
        md_output_path = pdf_path.replace('.pdf', '.md')
        self.pdf_converter.convert(pdf_path, md_output_path)
        
        # 2. Lire le contenu Markdown complet
        with open(md_output_path, 'r', encoding='utf-8') as f:
            contenu_markdown = f.read()
        
        # 3. Créer l'œuvre
        fichier_nom = f"{titre.replace(' ', '_')}.md"
        oeuvre = Oeuvre(
            titre=titre,
            auteur=auteur,
            fichier_nom=fichier_nom,
            soumis_par=soumis_par
        )
        
        # 4. Sauvegarder avec le contenu
        self.depot.sauvegarder(oeuvre, contenu_markdown=contenu_markdown)
        
        # 5. Nettoyer le fichier temporaire
        if os.path.exists(md_output_path):
            os.unlink(md_output_path)
        
        print(f"[Service] Œuvre '{titre}' créée depuis PDF")
        
        return oeuvre

    def lister_oeuvres_a_moderer(self, demandeur: Utilisateur) -> List[Oeuvre]:
        """Liste les œuvres à modérer depuis metadata.json"""
        if not demandeur.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé : Vous n'êtes pas modérateur.")
        return self.depot.lister_oeuvres_en_attente()

    def recuperer_oeuvre(self, id_oeuvre: str) -> Optional[Oeuvre]:
        """Récupère une œuvre par son ID"""
        return self.depot.get_oeuvre_by_id(id_oeuvre)
    
    def lire_contenu_oeuvre(self, id_oeuvre: str) -> str:
        """
        Lit le contenu Markdown complet d'une œuvre
        
        Returns:
            str: Le contenu Markdown du fichier
        """
        return self.depot.lire_contenu_oeuvre(id_oeuvre)

    def traiter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str) -> Oeuvre:
        """Passe une œuvre en traitement"""
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")
        
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        if not oeuvre:
            raise ValueError("Œuvre introuvable.")
        
        # Lire le contenu actuel
        contenu = self.depot.lire_contenu_oeuvre(id_oeuvre)
        
        # Changer l'état
        oeuvre.traiter()
        
        # Re-sauvegarder avec le contenu
        self.depot.sauvegarder(oeuvre, contenu_markdown=contenu)
        
        return oeuvre

    def valider_oeuvre(self, biblio: Utilisateur, id_oeuvre: str, destination: str):
        """Valide et déplace une œuvre vers un catalogue"""
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")
        
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        oeuvre.accepter()
        self.depot.deplacer_vers_catalogue(oeuvre, destination)
        
        return f"L'œuvre '{oeuvre.titre}' a été validée."

    def rejeter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str, motif: str):
        """Rejette une œuvre et l'archive"""
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")
        
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        oeuvre.refuser()
        self.depot.archiver_rejet(oeuvre, motif)
        
        return f"L'œuvre a été rejetée."


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
    






# ============================================
# SERVICE : Gestion des demandes de promotion
# src/app/domain/services.py (À AJOUTER)
# ============================================
"""
Service pour gérer les demandes de promotion membre → bibliothécaire
"""
from typing import List, Optional
from src.app.domain.modeles import (
    Utilisateur, DemandeBibliothecaire, StatutDemande, 
    PermissionsSysteme
)


class ServiceDemandesPromotion:
    """
    Gère le workflow complet des demandes de promotion
    """
    
    def __init__(self, depot_demandes, depot_utilisateurs):
        """
        Args:
            depot_demandes: Repository pour sauvegarder les demandes
            depot_utilisateurs: Repository des utilisateurs
        """
        self.depot_demandes = depot_demandes
        self.depot_users = depot_utilisateurs
    
    # ========================================
    # WORKFLOW MEMBRE : Faire une demande
    # ========================================
    
    def soumettre_demande(
        self, 
        membre: Utilisateur, 
        motivation: str
    ) -> DemandeBibliothecaire:
        """
        Un membre soumet une demande pour devenir bibliothécaire
        
        Args:
            membre: Le membre qui fait la demande
            motivation: Pourquoi il veut devenir bibliothécaire
        
        Returns:
            DemandeBibliothecaire: La demande créée
        
        Raises:
            ValueError: Si déjà bibliothécaire ou demande en cours
        """
        # 1. Vérifier qu'il n'est pas déjà bibliothécaire
        if membre.a_la_permission("peut_moderer_oeuvre"):
            raise ValueError("Vous êtes déjà bibliothécaire")
        
        # 2. Vérifier qu'il n'a pas déjà une demande en attente
        demandes_actives = self.depot_demandes.get_demandes_by_email(
            membre.email, 
            statut=StatutDemande.EN_ATTENTE
        )
        
        if demandes_actives:
            raise ValueError("Vous avez déjà une demande en cours")
        
        # 3. Créer la demande
        demande = DemandeBibliothecaire(membre, motivation)
        
        # 4. Sauvegarder
        self.depot_demandes.sauvegarder(demande)
        
        print(f"[ServiceDemandes] 📝 Nouvelle demande de {membre.email}")
        return demande
    
    def annuler_ma_demande(
        self, 
        membre: Utilisateur, 
        id_demande: str
    ) -> DemandeBibliothecaire:
        """
        Un membre annule sa propre demande
        
        Args:
            membre: Le membre qui annule
            id_demande: ID de la demande à annuler
        
        Returns:
            DemandeBibliothecaire: La demande annulée
        """
        demande = self.depot_demandes.get_demande_by_id(id_demande)
        
        if not demande:
            raise ValueError("Demande introuvable")
        
        demande.annuler(membre)
        self.depot_demandes.sauvegarder(demande)
        
        return demande
    
    def consulter_mes_demandes(
        self, 
        membre: Utilisateur
    ) -> List[DemandeBibliothecaire]:
        """
        Un membre consulte l'historique de ses demandes
        
        Returns:
            List[DemandeBibliothecaire]: Toutes ses demandes
        """
        return self.depot_demandes.get_demandes_by_email(membre.email)
    
    # ========================================
    # WORKFLOW BIBLIOTHÉCAIRE : Traiter les demandes
    # ========================================
    
    def lister_demandes_en_attente(
        self, 
        bibliothecaire: Utilisateur
    ) -> List[DemandeBibliothecaire]:
        """
        Liste toutes les demandes en attente (pour modération)
        
        Args:
            bibliothecaire: Le bibliothécaire qui consulte
        
        Returns:
            List[DemandeBibliothecaire]: Demandes en attente
        
        Raises:
            PermissionError: Si pas bibliothécaire
        """
        if not bibliothecaire.a_la_permission("peut_traiter_demandes_bibliothecaire"):
            raise PermissionError("Seuls les bibliothécaires peuvent voir les demandes")
        
        return self.depot_demandes.get_demandes_by_statut(StatutDemande.EN_ATTENTE)
    
    def approuver_demande(
        self, 
        bibliothecaire: Utilisateur, 
        id_demande: str
    ) -> Utilisateur:
        """
        Approuve une demande et promeut automatiquement le membre
        
        Args:
            bibliothecaire: Le bibliothécaire qui approuve
            id_demande: ID de la demande
        
        Returns:
            Utilisateur: Le membre promu
        
        Raises:
            PermissionError: Si pas bibliothécaire
            ValueError: Si demande introuvable
        """
        # 1. Vérifier les permissions
        if not bibliothecaire.a_la_permission("peut_traiter_demandes_bibliothecaire"):
            raise PermissionError("Seuls les bibliothécaires peuvent approuver")
        
        # 2. Récupérer la demande
        demande = self.depot_demandes.get_demande_by_id(id_demande)
        if not demande:
            raise ValueError("Demande introuvable")
        
        # 3. Approuver la demande
        demande.approuver(bibliothecaire)
        self.depot_demandes.sauvegarder(demande)
        
        # 4. Promouvoir le membre automatiquement
        membre = self.depot_users.get_by_email(demande.email_demandeur)
        if not membre:
            raise ValueError(f"Membre {demande.email_demandeur} introuvable")
        
        # Ajouter le rôle bibliothécaire
        role_biblio = PermissionsSysteme.creer_role_bibliothecaire()
        membre.ajouter_role(role_biblio)
        self.depot_users.sauvegarder(membre)
        
        print(f"[ServiceDemandes] ✅ {demande.email_demandeur} promu par {bibliothecaire.email}")
        
        return membre
    
    def refuser_demande(
        self, 
        bibliothecaire: Utilisateur, 
        id_demande: str,
        motif: str
    ) -> DemandeBibliothecaire:
        """
        Refuse une demande avec un motif
        
        Args:
            bibliothecaire: Le bibliothécaire qui refuse
            id_demande: ID de la demande
            motif: Raison du refus
        
        Returns:
            DemandeBibliothecaire: La demande refusée
        """
        if not bibliothecaire.a_la_permission("peut_traiter_demandes_bibliothecaire"):
            raise PermissionError("Seuls les bibliothécaires peuvent refuser")
        
        demande = self.depot_demandes.get_demande_by_id(id_demande)
        if not demande:
            raise ValueError("Demande introuvable")
        
        demande.refuser(bibliothecaire, motif)
        self.depot_demandes.sauvegarder(demande)
        
        return demande
    
    # ========================================
    # STATISTIQUES & RAPPORTS
    # ========================================
    
    def obtenir_statistiques(
        self, 
        bibliothecaire: Utilisateur
    ) -> dict:
        """
        Obtient des statistiques sur les demandes
        
        Returns:
            dict: Statistiques complètes
        """
        if not bibliothecaire.a_la_permission("peut_traiter_demandes_bibliothecaire"):
            raise PermissionError("Accès refusé")
        
        toutes_demandes = self.depot_demandes.get_all_demandes()
        
        stats = {
            "total": len(toutes_demandes),
            "en_attente": sum(1 for d in toutes_demandes if d.statut == StatutDemande.EN_ATTENTE),
            "approuvees": sum(1 for d in toutes_demandes if d.statut == StatutDemande.APPROUVEE),
            "refusees": sum(1 for d in toutes_demandes if d.statut == StatutDemande.REFUSEE),
            "annulees": sum(1 for d in toutes_demandes if d.statut == StatutDemande.ANNULEE),
        }
        
        # Délai moyen de traitement
        demandes_traitees = [
            d for d in toutes_demandes 
            if d.statut in [StatutDemande.APPROUVEE, StatutDemande.REFUSEE]
        ]
        
        if demandes_traitees:
            delais = [d.delai_traitement_jours() for d in demandes_traitees]
            stats["delai_moyen_jours"] = sum(delais) / len(delais)
        else:
            stats["delai_moyen_jours"] = 0
        
        return stats
    
    def lister_historique_complet(
        self, 
        bibliothecaire: Utilisateur,
        limit: int = 50
    ) -> List[DemandeBibliothecaire]:
        """
        Liste l'historique complet des demandes (pour audit)
        
        Args:
            bibliothecaire: Le bibliothécaire qui consulte
            limit: Nombre max de résultats
        
        Returns:
            List[DemandeBibliothecaire]: Dernières demandes
        """
        if not bibliothecaire.a_la_permission("peut_traiter_demandes_bibliothecaire"):
            raise PermissionError("Accès refusé")
        
        return self.depot_demandes.get_all_demandes(limit=limit)


# ============================================
# EXEMPLE D'UTILISATION
# ============================================
"""
# Scénario complet

# 1. Un membre fait une demande
membre = depot_users.get_by_email("alice@test.fr")
demande = service.soumettre_demande(
    membre, 
    motivation="J'aimerais contribuer à la modération de la bibliothèque"
)

# 2. Un bibliothécaire consulte les demandes
biblio = depot_users.get_by_email("biblio@test.fr")
demandes = service.lister_demandes_en_attente(biblio)
# [<Demande ... de alice@test.fr [en_attente]>]

# 3. Le bibliothécaire approuve
membre_promu = service.approuver_demande(biblio, demande.id)
# alice@test.fr a maintenant le rôle "Bibliothécaire"

# 4. Statistiques
stats = service.obtenir_statistiques(biblio)
# {
#   "total": 10,
#   "en_attente": 3,
#   "approuvees": 5,
#   "refusees": 2,
#   "delai_moyen_jours": 2.5
# }
"""
