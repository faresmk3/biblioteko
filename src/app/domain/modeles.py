# ============================================
# FICHIER 1: src/app/domain/modeles.py (VERSION COMPLÈTE)
# ============================================
"""
Modèles métier enrichis avec toutes les fonctionnalités manquantes
"""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from enum import Enum
import bcrypt
import secrets

# ============================================================
# 1. ENUMS (Classification, Statuts)
# ============================================================

class CategorieOeuvre(Enum):
    """Classification des œuvres selon le cahier des charges"""
    # Livres
    LIVRE_BD = "BD"
    LIVRE_ROMAN = "Roman"
    LIVRE_JEUNESSE = "Jeunesse"
    LIVRE_TECHNIQUE = "Technique"
    LIVRE_EDUCATION = "Education"
    LIVRE_CULTURE = "Culture"
    LIVRE_SANTE = "Santé"
    
    # Musique
    MUSIQUE_CLASSIQUE = "Classique"
    MUSIQUE_JAZZ = "Jazz"
    MUSIQUE_POP = "Pop"
    MUSIQUE_METAL = "Metal"
    
    # Vidéos
    VIDEO_SF = "SF"
    VIDEO_HISTOIRE = "Histoire"
    VIDEO_SERIE = "Série"
    VIDEO_DOCUMENTAIRE = "Documentaire"
    
    # Articles
    ARTICLE = "Article"

class StatutDroit(Enum):
    """Statut juridique de l'œuvre"""
    DOMAINE_PUBLIC = "libre"
    SOUS_DROITS = "protege"
    SEQUESTRE = "attente_liberation"

# ============================================================
# 2. GESTION DES UTILISATEURS & DROITS (RBAC) - AMÉLIORÉ
# ============================================================

class Permission:
    def __init__(self, nom_permission: str):
        self.nom_permission = nom_permission

    def __repr__(self):
        return f"<Permission {self.nom_permission}>"

    def __eq__(self, other):
        if isinstance(other, str):
            return self.nom_permission == other
        return self.nom_permission == other.nom_permission

class Role:
    def __init__(self, nom_role: str):
        self.nom_role = nom_role
        self.permissions: List[Permission] = []

    def ajouter_permission(self, permission: Permission):
        self.permissions.append(permission)

class Utilisateur:
    """
    SÉCURISÉ : Hashing bcrypt + Clé de chiffrement personnelle
    """
    def __init__(self, nom: str, prenom: str, email: str, mdp: str):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.courriel = email  # Alias
        
        # 🔐 SÉCURITÉ : Hashing du mot de passe
        self.mdp_hash = bcrypt.hashpw(mdp.encode('utf-8'), bcrypt.gensalt())
        
        # 🔑 Clé de chiffrement unique pour les emprunts
        self.cle_chiffrement = self._generer_cle_chiffrement()
        
        self.roles: List[Role] = []
        self.espace_disque_mb: int = 1000  # Espace dispo en MB
        self.date_inscription = datetime.now()

    def _generer_cle_chiffrement(self) -> bytes:
        """Génère une clé Fernet pour chiffrer les emprunts"""
        from cryptography.fernet import Fernet
        return Fernet.generate_key()

    def verifier_mdp(self, mdp: str) -> bool:
        """Vérifie le mot de passe en toute sécurité"""
        return bcrypt.checkpw(mdp.encode('utf-8'), self.mdp_hash)

    def ajouter_role(self, role: Role):
        self.roles.append(role)

    def a_la_permission(self, nom_perm: str) -> bool:
        for role in self.roles:
            for perm in role.permissions:
                if perm.nom_permission == nom_perm:
                    return True
        return False

    def a_espace_disque_disponible(self, taille_mb: int = 10) -> bool:
        """Vérifie si l'utilisateur a assez d'espace disque"""
        return self.espace_disque_mb >= taille_mb

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"


# ============================================================
# 3. PATTERN STATE (États de l'Oeuvre) - INCHANGÉ
# ============================================================

class EtatOeuvre(ABC):
    @property
    @abstractmethod
    def nom(self) -> str:
        pass

    def traiter(self, oeuvre) -> None:
        raise PermissionError(f"Action 'traiter' impossible depuis l'état {self.nom}")

    def accepter(self, oeuvre) -> None:
        raise PermissionError(f"Action 'accepter' impossible depuis l'état {self.nom}")

    def refuser(self, oeuvre) -> None:
        raise PermissionError(f"Action 'refuser' impossible depuis l'état {self.nom}")

    def __repr__(self):
        return self.nom

class EtatSoumise(EtatOeuvre):
    nom = "SOUMISE"
    def traiter(self, oeuvre):
        oeuvre.changer_etat(EtatEnTraitement())

class EtatEnTraitement(EtatOeuvre):
    nom = "EN_TRAITEMENT"
    def accepter(self, oeuvre):
        oeuvre.changer_etat(EtatValidee())
    def refuser(self, oeuvre):
        oeuvre.changer_etat(EtatRefusee())

class EtatValidee(EtatOeuvre):
    nom = "VALIDEE"

class EtatRefusee(EtatOeuvre):
    nom = "REFUSEE"


# ============================================================
# 4. DOMAINE MÉTIER : L'ŒUVRE (ENRICHIE)
# ============================================================

class Oeuvre:
    """
    NOUVELLES FONCTIONNALITÉS :
    - Classification multi-catégories
    - Gestion domaine public / sous droits
    - Métadonnées IA (Gemini, Pixtral)
    """
    def __init__(self, titre: str, auteur: str, fichier_nom: str, soumis_par: Utilisateur):
        self.id = f"{titre.replace(' ', '_')}.md"
        self.titre = titre
        self.auteur = auteur
        self.fichier_nom = fichier_nom
        
        self.soumis_par_email = soumis_par.email if hasattr(soumis_par, 'email') else str(soumis_par)
        self.date_soumission = datetime.now().isoformat()
        
        # État interne (privé)
        self._etat_actuel: EtatOeuvre = EtatSoumise()
        
        # 🆕 CLASSIFICATION
        self.categories: List[CategorieOeuvre] = []
        
        # 🆕 STATUT JURIDIQUE
        self.statut_droit: StatutDroit = StatutDroit.SOUS_DROITS
        self.date_liberation: Optional[datetime] = None  # Date de passage domaine public
        
        # 🆕 RECONNAISSANCE IA
        self.resultats_ocr: Dict[str, str] = {}  # {"tesseract": "...", "gemini": "...", "pixtral": "..."}
        
        self.metadonnees: Dict = {}

    @property
    def etat(self):
        return self._etat_actuel

    def changer_etat(self, nouvel_etat: EtatOeuvre):
        print(f"[State] Oeuvre '{self.titre}' : {self._etat_actuel.nom} -> {nouvel_etat.nom}")
        self._etat_actuel = nouvel_etat

    def set_metadonnee(self, cle: str, valeur: str):
        self.metadonnees[cle] = valeur

    # --- Méthodes Classification ---
    
    def ajouter_categorie(self, categorie: CategorieOeuvre):
        """Ajoute une catégorie (œuvre peut avoir plusieurs catégories)"""
        if categorie not in self.categories:
            self.categories.append(categorie)
    
    def est_dans_categorie(self, categorie: CategorieOeuvre) -> bool:
        return categorie in self.categories
    
    # --- Méthodes Juridiques ---
    
    def calculer_statut_droit(self):
        """
        Détermine si l'œuvre est dans le domaine public
        Règle : 70 ans après la mort de l'auteur (simplifié ici)
        """
        if self.date_liberation and datetime.now() > self.date_liberation:
            self.statut_droit = StatutDroit.DOMAINE_PUBLIC
            return True
        return False
    
    def est_libre_de_droits(self) -> bool:
        return self.statut_droit == StatutDroit.DOMAINE_PUBLIC
    
    def placer_en_sequestre(self, date_liberation: datetime):
        """Place l'œuvre en attente de libération automatique"""
        self.statut_droit = StatutDroit.SEQUESTRE
        self.date_liberation = date_liberation
    
    # --- Méthodes IA ---
    
    def enregistrer_resultat_ocr(self, source_ia: str, texte: str):
        """Enregistre le résultat d'une reconnaissance IA"""
        self.resultats_ocr[source_ia] = texte
    
    def comparer_qualite_ocr(self) -> Dict[str, float]:
        """
        Compare la qualité des différentes OCR
        Retourne un score basique (nombre de mots / longueur)
        """
        scores = {}
        for source, texte in self.resultats_ocr.items():
            nb_mots = len(texte.split())
            longueur = len(texte)
            scores[source] = {
                "nb_mots": nb_mots,
                "longueur": longueur,
                "score": nb_mots / max(longueur, 1) * 1000  # Score simplifié
            }
        return scores

    # --- Méthodes Métier (State) ---
    
    def traiter(self):
        self._etat_actuel.traiter(self)

    def accepter(self):
        self._etat_actuel.accepter(self)

    def valider(self):
        self.accepter()

    def refuser(self):
        self._etat_actuel.refuser(self)

    def __repr__(self):
        cats = ", ".join([c.value for c in self.categories])
        return f"<Oeuvre '{self.titre}' [{self._etat_actuel.nom}] ({cats})>"


# ============================================================
# 5. NOUVEAU : GESTION DES EMPRUNTS
# ============================================================

class Emprunt:
    """
    Représente l'emprunt d'une œuvre par un utilisateur
    FONCTIONNALITÉS :
    - Durée 14 jours (configurable)
    - Chiffrement avec clé utilisateur
    - Détection expiration
    """
    def __init__(self, oeuvre: Oeuvre, utilisateur: Utilisateur, duree_jours: int = 14):
        self.id = f"emprunt_{secrets.token_hex(8)}"
        self.oeuvre_id = oeuvre.fichier_nom
        self.oeuvre_titre = oeuvre.titre
        self.utilisateur_email = utilisateur.email
        
        # Dates
        self.date_debut = datetime.now()
        self.date_fin = self.date_debut + timedelta(days=duree_jours)
        self.date_retour: Optional[datetime] = None
        
        # Chiffrement
        self.cle_chiffrement = utilisateur.cle_chiffrement
        self.fichier_chiffre: Optional[bytes] = None
        
        # État
        self.est_actif = True
    
    def est_expire(self) -> bool:
        """Vérifie si l'emprunt a dépassé la date limite"""
        return datetime.now() > self.date_fin and self.est_actif
    
    def jours_restants(self) -> int:
        """Calcule le nombre de jours restants (arrondi métier)"""
        if not self.est_actif:
            return 0

        maintenant = datetime.now()
        delta = self.date_fin - maintenant

        # Si encore valide aujourd'hui, on compte le jour en cours
        jours = delta.days
        if delta.seconds > 0:
            jours += 1

        return max(0, jours)
    
    def retourner(self):
        """Marque l'emprunt comme retourné"""
        self.date_retour = datetime.now()
        self.est_actif = False
        print(f"[Emprunt] Retour de '{self.oeuvre_titre}' par {self.utilisateur_email}")
    
    def renouveler(self, jours: int = 14):
        """Prolonge l'emprunt"""
        if self.est_actif:
            self.date_fin = self.date_fin + timedelta(days=jours)
            print(f"[Emprunt] Prolongation de {jours} jours pour '{self.oeuvre_titre}'")
    
    def __repr__(self):
        statut = "ACTIF" if self.est_actif else "TERMINÉ"
        return f"<Emprunt '{self.oeuvre_titre}' [{statut}] - {self.jours_restants()}j restants>"


# ============================================================
# 6. NOUVEAU : PERMISSIONS SYSTÈME COMPLET
# ============================================================

class PermissionsSysteme:
    """Définition de toutes les permissions du système"""
    
    # Permissions Modération
    PEUT_MODERER = Permission("peut_moderer_oeuvre")
    PEUT_VALIDER = Permission("peut_valider_oeuvre")
    PEUT_REJETER = Permission("peut_rejeter_oeuvre")
    
    # Permissions Emprunts
    PEUT_EMPRUNTER = Permission("peut_emprunter_oeuvre")
    PEUT_RENOUVELER = Permission("peut_renouveler_emprunt")
    
    # Permissions Admin
    PEUT_GERER_UTILISATEURS = Permission("peut_gerer_utilisateurs")
    PEUT_GERER_DIFFUSION = Permission("peut_gerer_diffusion")
    

    # Nouvelle permission pour gérer les demandes
    PEUT_TRAITER_DEMANDES = Permission("peut_traiter_demandes_bibliothecaire")


    @classmethod
    def creer_role_bibliothecaire(cls) -> Role:
        """Factory pour créer un rôle bibliothécaire complet"""
        role = Role("Bibliothécaire")
        role.ajouter_permission(cls.PEUT_MODERER)
        role.ajouter_permission(cls.PEUT_VALIDER)
        role.ajouter_permission(cls.PEUT_REJETER)
        role.ajouter_permission(cls.PEUT_GERER_DIFFUSION)
        role.ajouter_permission(cls.PEUT_TRAITER_DEMANDES)
        return role
    
    @classmethod
    def creer_role_membre(cls) -> Role:
        """Factory pour créer un rôle membre standard"""
        role = Role("Membre")
        role.ajouter_permission(cls.PEUT_EMPRUNTER)
        role.ajouter_permission(cls.PEUT_RENOUVELER)
        return role



class StatutDemande(Enum):
    """États possibles d'une demande"""
    EN_ATTENTE = "en_attente"
    APPROUVEE = "approuvee"
    REFUSEE = "refusee"
    ANNULEE = "annulee"


class DemandeBibliothecaire:
    """
    Représente une demande de promotion en bibliothécaire
    
    Workflow :
    1. Membre fait une demande (EN_ATTENTE)
    2. Bibliothécaire approuve (APPROUVEE) ou refuse (REFUSEE)
    3. Système applique automatiquement la promotion si approuvée
    """
    
    def __init__(self, membre: 'Utilisateur', motivation: str = ""):
        self.id = f"demande_{secrets.token_hex(8)}"
        self.email_demandeur = membre.email
        self.nom_demandeur = f"{membre.prenom} {membre.nom}"
        self.motivation = motivation
        
        # Dates et statut
        self.date_demande = datetime.now()
        self.date_reponse: Optional[datetime] = None
        self.statut = StatutDemande.EN_ATTENTE
        
        # Qui a traité la demande
        self.traite_par_email: Optional[str] = None
        self.motif_refus: Optional[str] = None
    
    def approuver(self, bibliothecaire: 'Utilisateur'):
        """
        Approuve la demande
        
        Args:
            bibliothecaire: Le bibliothécaire qui approuve
        
        Raises:
            PermissionError: Si pas bibliothécaire
            ValueError: Si demande déjà traitée
        """
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Seuls les bibliothécaires peuvent approuver")
        
        if self.statut != StatutDemande.EN_ATTENTE:
            raise ValueError(f"Demande déjà traitée (statut: {self.statut.value})")
        
        self.statut = StatutDemande.APPROUVEE
        self.date_reponse = datetime.now()
        self.traite_par_email = bibliothecaire.email
        
        print(f"[Demande] ✅ Approuvée par {bibliothecaire.email}")
    
    def refuser(self, bibliothecaire: 'Utilisateur', motif: str):
        """
        Refuse la demande
        
        Args:
            bibliothecaire: Le bibliothécaire qui refuse
            motif: Raison du refus
        
        Raises:
            PermissionError: Si pas bibliothécaire
            ValueError: Si demande déjà traitée
        """
        if not bibliothecaire.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Seuls les bibliothécaires peuvent refuser")
        
        if self.statut != StatutDemande.EN_ATTENTE:
            raise ValueError(f"Demande déjà traitée (statut: {self.statut.value})")
        
        self.statut = StatutDemande.REFUSEE
        self.date_reponse = datetime.now()
        self.traite_par_email = bibliothecaire.email
        self.motif_refus = motif
        
        print(f"[Demande] ❌ Refusée par {bibliothecaire.email}: {motif}")
    
    def annuler(self, membre: 'Utilisateur'):
        """
        Le membre annule sa propre demande
        
        Args:
            membre: Le membre qui a fait la demande
        
        Raises:
            ValueError: Si ce n'est pas son propre demande ou si déjà traitée
        """
        if membre.email != self.email_demandeur:
            raise ValueError("Vous ne pouvez annuler que vos propres demandes")
        
        if self.statut != StatutDemande.EN_ATTENTE:
            raise ValueError("Demande déjà traitée, impossible d'annuler")
        
        self.statut = StatutDemande.ANNULEE
        self.date_reponse = datetime.now()
        
        print(f"[Demande] 🚫 Annulée par le demandeur")
    
    def est_en_attente(self) -> bool:
        """Vérifie si la demande est en attente"""
        return self.statut == StatutDemande.EN_ATTENTE
    
    def est_approuvee(self) -> bool:
        """Vérifie si la demande est approuvée"""
        return self.statut == StatutDemande.APPROUVEE
    
    def delai_traitement_jours(self) -> Optional[int]:
        """Calcule le délai de traitement en jours"""
        if not self.date_reponse:
            # Délai depuis la demande
            return (datetime.now() - self.date_demande).days
        else:
            # Délai réel de traitement
            return (self.date_reponse - self.date_demande).days
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire pour JSON"""
        return {
            "id": self.id,
            "email_demandeur": self.email_demandeur,
            "nom_demandeur": self.nom_demandeur,
            "motivation": self.motivation,
            "date_demande": self.date_demande.isoformat(),
            "date_reponse": self.date_reponse.isoformat() if self.date_reponse else None,
            "statut": self.statut.value,
            "traite_par": self.traite_par_email,
            "motif_refus": self.motif_refus,
            "delai_jours": self.delai_traitement_jours()
        }
    
    def __repr__(self):
        return f"<Demande {self.id} de {self.email_demandeur} [{self.statut.value}]>"

