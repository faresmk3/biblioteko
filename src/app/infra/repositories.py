# src/app/infra/repositories.py (VERSION CORRIGÉE)

import os
import git
import json
from typing import List, Optional, Dict
from datetime import datetime
from src.app.domain.modeles import Oeuvre, Utilisateur
from src.app.domain.modeles import (
    DemandeBibliothecaire, StatutDemande
)

class FileSystemGitRepository:
    """
    ARCHITECTURE CORRIGÉE :
    - metadata.json : Base de données avec toutes les métadonnées
    - fichiers.md : Contenu complet des livres (texte OCR)
    """
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.metadata_file = os.path.join(root_dir, "data", "metadata.json")
        
        # Initialiser le dépôt Git
        try:
            self.repo = git.Repo(self.root_dir)
        except git.exc.InvalidGitRepositoryError:
            print(f"[Infra] Init Git dans {self.root_dir}")
            self.repo = git.Repo.init(self.root_dir)
        
        # Créer la structure de dossiers
        self._ensure_dir("a_moderer")
        self._ensure_dir("fond_commun")
        self._ensure_dir("sequestre")
        self._ensure_dir("archives")
        
        # Initialiser metadata.json s'il n'existe pas
        if not os.path.exists(self.metadata_file):
            self._init_metadata_file()

    def _ensure_dir(self, dossier: str):
        """Crée un dossier s'il n'existe pas"""
        os.makedirs(os.path.join(self.root_dir, "data", dossier), exist_ok=True)

    def _init_metadata_file(self):
        """Initialise le fichier metadata.json"""
        initial_data = {
            "oeuvres": [],
            "version": "1.0",
            "derniere_maj": datetime.now().isoformat()
        }
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        print(f"[Metadata] Fichier créé : {self.metadata_file}")

    def _load_metadata(self) -> Dict:
        """Charge les métadonnées depuis le JSON"""
        if not os.path.exists(self.metadata_file):
            return {"oeuvres": []}
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_metadata(self, metadata: Dict):
        """Sauvegarde les métadonnées dans le JSON"""
        metadata["derniere_maj"] = datetime.now().isoformat()
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        # Commit Git
        self.repo.index.add([self.metadata_file])
        self.repo.index.commit(f"MAJ metadata : {len(metadata['oeuvres'])} œuvres")

    def _get_file_path(self, dossier: str, filename: str) -> str:
        """Retourne le chemin complet d'un fichier"""
        return os.path.join(self.root_dir, "data", dossier, filename)

    # ============================================
    # MÉTHODE PRINCIPALE : Sauvegarder une œuvre
    # ============================================

    def sauvegarder(self, oeuvre: Oeuvre, contenu_markdown: str = None):
        """
        Sauvegarde une œuvre :
        1. Métadonnées dans metadata.json
        2. Contenu Markdown dans le fichier .md
        
        Args:
            oeuvre: L'objet Oeuvre avec les métadonnées
            contenu_markdown: Le contenu complet du livre en Markdown
        """
        # 1. Déterminer le dossier selon l'état
        if oeuvre.etat.nom in ["SOUMISE", "EN_TRAITEMENT"]:
            dossier = "a_moderer"
        elif oeuvre.etat.nom == "VALIDEE":
            dossier = "fond_commun"
        elif oeuvre.etat.nom == "REFUSEE":
            dossier = "archives"
        else:
            dossier = "sequestre"

        # 2. Nom du fichier Markdown
        safe_filename = f"{oeuvre.titre.replace(' ', '_')}.md"
        file_path = self._get_file_path(dossier, safe_filename)

        # 3. Écrire le contenu Markdown complet
        if contenu_markdown:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(contenu_markdown)
            print(f"[Fichier] Sauvegardé : {file_path}")
        else:
            # Si pas de contenu fourni, créer un fichier vide
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {oeuvre.titre}\n\nContenu à ajouter...")

        # 4. Mettre à jour metadata.json
        metadata = self._load_metadata()
        
        # Créer l'entrée métadonnées
        oeuvre_meta = {
            "id": safe_filename,
            "titre": oeuvre.titre,
            "auteur": oeuvre.auteur,
            "fichier_nom": safe_filename,
            "dossier": dossier,
            "soumis_par": oeuvre.soumis_par_email,
            "date_soumission": oeuvre.date_soumission,
            "etat": oeuvre.etat.nom,
            "metadonnees": oeuvre.metadonnees
        }

        # Chercher si l'œuvre existe déjà (mise à jour)
        existing_index = None
        for i, o in enumerate(metadata["oeuvres"]):
            if o["id"] == safe_filename:
                existing_index = i
                break

        if existing_index is not None:
            metadata["oeuvres"][existing_index] = oeuvre_meta
        else:
            metadata["oeuvres"].append(oeuvre_meta)

        # 5. Sauvegarder metadata.json
        self._save_metadata(metadata)

        # 6. Git commit du fichier .md
        self.repo.index.add([file_path])
        self.repo.index.commit(f"Ajout/MAJ : {oeuvre.titre} ({oeuvre.etat.nom})")

        print(f"[Git] Commit : {oeuvre.titre}")

    # ============================================
    # RÉCUPÉRATION D'ŒUVRES
    # ============================================

    def lister_oeuvres_en_attente(self) -> List[Oeuvre]:
        """Liste les œuvres à modérer depuis metadata.json"""
        metadata = self._load_metadata()
        oeuvres = []

        for meta in metadata["oeuvres"]:
            if meta["dossier"] == "a_moderer":
                # Créer un stub utilisateur
                user_stub = Utilisateur(
                    nom="Inconnu",
                    prenom="",
                    email=meta.get("soumis_par", "inconnu"),
                    mdp=""
                )

                # Créer l'objet Oeuvre
                oeuvre = Oeuvre(
                    titre=meta["titre"],
                    auteur=meta["auteur"],
                    fichier_nom=meta["fichier_nom"],
                    soumis_par=user_stub
                )
                
                # Restaurer l'état
                self._restore_etat(oeuvre, meta["etat"])
                
                oeuvres.append(oeuvre)

        return oeuvres

    def get_oeuvre_by_id(self, id_oeuvre: str) -> Optional[Oeuvre]:
        """Récupère une œuvre par son ID depuis metadata.json"""
        metadata = self._load_metadata()

        for meta in metadata["oeuvres"]:
            if meta["id"] == id_oeuvre:
                # Créer l'objet Oeuvre
                user_stub = Utilisateur(
                    nom="Inconnu",
                    prenom="",
                    email=meta.get("soumis_par", "inconnu"),
                    mdp=""
                )

                oeuvre = Oeuvre(
                    titre=meta["titre"],
                    auteur=meta["auteur"],
                    fichier_nom=meta["fichier_nom"],
                    soumis_par=user_stub
                )

                # Restaurer l'état
                self._restore_etat(oeuvre, meta["etat"])

                return oeuvre

        return None

    def lire_contenu_oeuvre(self, id_oeuvre: str) -> str:
        """
        Lit le contenu Markdown complet d'une œuvre
        
        Returns:
            str: Le contenu Markdown du fichier
        """
        metadata = self._load_metadata()

        for meta in metadata["oeuvres"]:
            if meta["id"] == id_oeuvre:
                file_path = self._get_file_path(meta["dossier"], meta["fichier_nom"])
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    raise FileNotFoundError(f"Fichier introuvable : {file_path}")

        raise ValueError(f"Œuvre '{id_oeuvre}' non trouvée dans les métadonnées")

    # ============================================
    # GESTION DES ÉTATS
    # ============================================

    def _restore_etat(self, oeuvre: Oeuvre, etat_str: str):
        """Restaure l'état d'une œuvre depuis une string"""
        from src.app.domain.modeles import (
            EtatSoumise, EtatEnTraitement, EtatValidee, EtatRefusee
        )

        if etat_str == "EN_TRAITEMENT":
            oeuvre._etat_actuel = EtatEnTraitement()
        elif etat_str == "VALIDEE":
            oeuvre._etat_actuel = EtatValidee()
        elif etat_str == "REFUSEE":
            oeuvre._etat_actuel = EtatRefusee()
        # SOUMISE est l'état par défaut

    # ============================================
    # DÉPLACEMENT D'ŒUVRES
    # ============================================

    def deplacer_vers_catalogue(self, oeuvre: Oeuvre, destination: str):
        """Déplace une œuvre vers un autre catalogue"""
        metadata = self._load_metadata()

        # 1. Trouver l'œuvre dans les métadonnées
        for meta in metadata["oeuvres"]:
            if meta["id"] == oeuvre.fichier_nom:
                old_dossier = meta["dossier"]
                old_path = self._get_file_path(old_dossier, meta["fichier_nom"])
                new_path = self._get_file_path(destination, meta["fichier_nom"])

                # 2. Déplacer le fichier physique
                if os.path.exists(old_path):
                    # Lire le contenu
                    with open(old_path, 'r', encoding='utf-8') as f:
                        contenu = f.read()
                    
                    # Écrire dans le nouveau dossier
                    with open(new_path, 'w', encoding='utf-8') as f:
                        f.write(contenu)
                    
                    # Supprimer l'ancien
                    os.remove(old_path)

                    # 3. Git
                    self.repo.index.remove([old_path])
                    self.repo.index.add([new_path])

                # 4. Mettre à jour les métadonnées
                meta["dossier"] = destination
                meta["etat"] = oeuvre.etat.nom

                self._save_metadata(metadata)
                self.repo.index.commit(f"Déplacement : {oeuvre.titre} -> {destination}")

                print(f"[Déplacement] {oeuvre.titre} : {old_dossier} -> {destination}")
                return

        raise ValueError(f"Œuvre '{oeuvre.fichier_nom}' non trouvée")

    def archiver_rejet(self, oeuvre: Oeuvre, motif: str):
        """Archive une œuvre rejetée"""
        oeuvre.set_metadonnee("motif_rejet", motif)
        self.deplacer_vers_catalogue(oeuvre, "archives")

    # ============================================
    # EMPRUNTS
    # ============================================

    def sauvegarder_emprunt(self, emprunt):
        """Sauvegarde un emprunt"""
        emprunt_dir = os.path.join(self.root_dir, "data", "emprunts")
        os.makedirs(emprunt_dir, exist_ok=True)

        emprunt_file = os.path.join(emprunt_dir, f"{emprunt.id}.json")

        emprunt_data = {
            "id": emprunt.id,
            "oeuvre_id": emprunt.oeuvre_id,
            "oeuvre_titre": emprunt.oeuvre_titre,
            "utilisateur_email": emprunt.utilisateur_email,
            "date_debut": emprunt.date_debut.isoformat(),
            "date_fin": emprunt.date_fin.isoformat(),
            "est_actif": emprunt.est_actif
        }

        with open(emprunt_file, 'w', encoding='utf-8') as f:
            json.dump(emprunt_data, f, indent=2)

        self.repo.index.add([emprunt_file])
        self.repo.index.commit(f"Emprunt: {emprunt.oeuvre_titre}")

    def supprimer_emprunt(self, id_emprunt: str):
        """Supprime un emprunt"""
        emprunt_file = os.path.join(self.root_dir, "data", "emprunts", f"{id_emprunt}.json")

        if os.path.exists(emprunt_file):
            os.remove(emprunt_file)
            try:
                self.repo.index.remove([emprunt_file])
                self.repo.index.commit(f"Retour: {id_emprunt}")
            except:
                pass

    def lister_toutes_oeuvres(self) -> List[Oeuvre]:
        """Liste toutes les œuvres"""
        metadata = self._load_metadata()
        oeuvres = []

        for meta in metadata["oeuvres"]:
            user_stub = Utilisateur("Inc", "", meta.get("soumis_par", "?"), "")
            oeuvre = Oeuvre(
                meta["titre"],
                meta["auteur"],
                meta["fichier_nom"],
                user_stub
            )
            self._restore_etat(oeuvre, meta["etat"])
            oeuvres.append(oeuvre)

        return oeuvres


# ============================================
# REPOSITORY UTILISATEURS (JSON)
# ============================================

# ============================================
# CORRECTIF URGENT : RepoUtilisateurs
# src/app/infra/repositories.py (LIGNE ~380)
# ============================================
"""
REMPLACER LA CLASSE RepoUtilisateurs COMPLÈTE
"""

import json
from typing import Optional, List, Dict
from datetime import datetime

class RepoUtilisateurs:
    """
    Repository pour les utilisateurs
    
    STRUCTURE SUPPORTÉE (email comme clé) :
    {
      "admin@biblioteko.fr": {
        "nom": "Admin",
        "prenom": "Jean",
        "email": "admin@biblioteko.fr",
        "roles": ["Membre"],
        ...
      }
    }
    """
    
    def __init__(self, users_file: str):
        self.users_file = users_file
        
        # Créer le dossier parent si nécessaire
        users_dir = os.path.dirname(users_file)
        if users_dir and not os.path.exists(users_dir):
            os.makedirs(users_dir, exist_ok=True)
        
        # Initialiser si fichier inexistant
        if not os.path.exists(users_file):
            self._init_users_file()
    
    def _init_users_file(self):
        """Initialise le fichier users.json vide"""
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2)
        print(f"[RepoUsers] Fichier initialisé : {self.users_file}")
    
    def _load_users(self) -> Dict:
        """
        Charge les utilisateurs depuis le JSON
        ADAPTÉ : Structure avec email comme clé
        """
        try:
            if not os.path.exists(self.users_file):
                self._init_users_file()
                return {}
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier que c'est un dictionnaire
            if not isinstance(data, dict):
                print(f"[RepoUsers] WARNING : Structure invalide, réinitialisation")
                return {}
            
            return data
        
        except json.JSONDecodeError as e:
            print(f"[RepoUsers] ERREUR JSON : {e}")
            return {}
        except Exception as e:
            print(f"[RepoUsers] ERREUR : {e}")
            return {}
    
    def _save_users(self, data: Dict):
        """Sauvegarde les utilisateurs"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[RepoUsers] ERREUR sauvegarde : {e}")
    
    def sauvegarder(self, utilisateur):
        """Sauvegarde un utilisateur"""
        from src.app.domain.modeles import Utilisateur
        
        data = self._load_users()
        
        user_dict = {
            "nom": utilisateur.nom,
            "prenom": utilisateur.prenom,
            "email": utilisateur.email,
            "courriel": utilisateur.email,
            "mot_de_passe": utilisateur.mdp_hash.decode('utf-8'),
            "roles": [r.nom_role for r in utilisateur.roles],
            
        }
        
        # Email comme clé
        data[utilisateur.email] = user_dict
        self._save_users(data)
        print(f"[RepoUsers] Utilisateur sauvegardé : {utilisateur.email}")
    
    def get_by_email(self, email: str):
        """
        Récupère un utilisateur par email
        ADAPTÉ : Email comme clé directe
        """
        try:
            data = self._load_users()
            
            # ✅ CORRECTIF : Email comme clé directe
            if email in data:
                u = data[email]
                
                # Créer l'objet Utilisateur
                from src.app.domain.modeles import Utilisateur, PermissionsSysteme, Role
                
                user = Utilisateur(
                    u.get("nom", "Inconnu"),
                    u.get("prenom", ""),
                    u.get("email"),
                    ""  # Mot de passe vide (pas stocké en clair)
                )

                if "mot_de_passe" in u:
                    user.mdp_hash = u["mot_de_passe"].encode('utf-8')
                
                # Restaurer les rôles
                for role_name in u.get("roles", []):
                    if role_name == "Bibliothécaire":
                        role = PermissionsSysteme.creer_role_bibliothecaire()
                    elif role_name == "Membre":
                        role = PermissionsSysteme.creer_role_membre()
                    else:
                        role = Role(role_name)
                    
                    user.ajouter_role(role)
                
                return user
            
            # Utilisateur non trouvé
            print(f"[RepoUsers] ⚠️  Utilisateur non trouvé : {email}")
            return None
        
        except Exception as e:
            print(f"[RepoUsers] ❌ ERREUR dans get_by_email : {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def user_exists(self, email: str) -> bool:
        """Vérifie si un utilisateur existe"""
        data = self._load_users()
        return email in data
    
    def count_users(self) -> int:
        """Compte le nombre d'utilisateurs"""
        data = self._load_users()
        return len(data)
    
    def get_all_emails(self) -> List[str]:
        """Retourne tous les emails"""
        data = self._load_users()
        return list(data.keys())
    
    def list_all(self) -> List[Dict]:
        """Liste tous les utilisateurs"""
        data = self._load_users()
        return list(data.values())
    



class RepoDemandesPromotion:
    """
    Stocke les demandes de promotion dans des fichiers JSON sous Git
    
    Structure :
    data/demandes_promotion/
    ├── demande_abc123.json
    ├── demande_def456.json
    └── ...
    """
    
    def __init__(self, root_dir: str, git_repo):
        """
        Args:
            root_dir: Racine du projet
            git_repo: Instance git.Repo pour les commits
        """
        self.root_dir = root_dir
        self.repo = git_repo
        self.demandes_dir = os.path.join(root_dir, "data", "demandes_promotion")
        
        # Créer le dossier s'il n'existe pas
        os.makedirs(self.demandes_dir, exist_ok=True)
        
        print(f"[RepoDemandesPromotion] Initialisé dans {self.demandes_dir}")
    
    # ========================================
    # SAUVEGARDE & LECTURE
    # ========================================
    
    def sauvegarder(self, demande: DemandeBibliothecaire):
        """
        Sauvegarde une demande en JSON et commit Git
        
        Args:
            demande: La demande à sauvegarder
        """
        file_path = os.path.join(self.demandes_dir, f"{demande.id}.json")
        
        # Sérialisation en JSON
        data = {
            "id": demande.id,
            "email_demandeur": demande.email_demandeur,
            "nom_demandeur": demande.nom_demandeur,
            "motivation": demande.motivation,
            "date_demande": demande.date_demande.isoformat(),
            "date_reponse": demande.date_reponse.isoformat() if demande.date_reponse else None,
            "statut": demande.statut.value,
            "traite_par_email": demande.traite_par_email,
            "motif_refus": demande.motif_refus
        }
        
        # Écriture du fichier
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Commit Git
        self.repo.index.add([file_path])
        
        if demande.statut == StatutDemande.EN_ATTENTE:
            message = f"Demande: {demande.email_demandeur} soumet"
        elif demande.statut == StatutDemande.APPROUVEE:
            message = f"Demande: {demande.email_demandeur} APPROUVÉE par {demande.traite_par_email}"
        elif demande.statut == StatutDemande.REFUSEE:
            message = f"Demande: {demande.email_demandeur} REFUSÉE par {demande.traite_par_email}"
        else:
            message = f"Demande: {demande.email_demandeur} annulée"
        
        self.repo.index.commit(message)
        
        print(f"[RepoDemandesPromotion] Sauvegardé : {demande.id}")
    
    def _charger_demande_depuis_fichier(self, file_path: str) -> Optional[DemandeBibliothecaire]:
        """
        Charge une demande depuis un fichier JSON
        
        Args:
            file_path: Chemin complet du fichier
        
        Returns:
            DemandeBibliothecaire ou None si erreur
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Créer un utilisateur stub pour initialiser la demande
            user_stub = Utilisateur("", "", data["email_demandeur"], "")
            
            demande = DemandeBibliothecaire(user_stub, data["motivation"])
            
            # Restaurer les propriétés
            demande.id = data["id"]
            demande.nom_demandeur = data["nom_demandeur"]
            demande.date_demande = datetime.fromisoformat(data["date_demande"])
            
            if data["date_reponse"]:
                demande.date_reponse = datetime.fromisoformat(data["date_reponse"])
            
            demande.statut = StatutDemande(data["statut"])
            demande.traite_par_email = data.get("traite_par_email")
            demande.motif_refus = data.get("motif_refus")
            
            return demande
        
        except Exception as e:
            print(f"[RepoDemandesPromotion] Erreur chargement {file_path}: {e}")
            return None
    
    # ========================================
    # RÉCUPÉRATION
    # ========================================
    
    def get_demande_by_id(self, id_demande: str) -> Optional[DemandeBibliothecaire]:
        """
        Récupère une demande par son ID
        
        Args:
            id_demande: ID de la demande
        
        Returns:
            DemandeBibliothecaire ou None
        """
        file_path = os.path.join(self.demandes_dir, f"{id_demande}.json")
        
        if not os.path.exists(file_path):
            return None
        
        return self._charger_demande_depuis_fichier(file_path)
    
    def get_demandes_by_email(
        self, 
        email: str, 
        statut: Optional[StatutDemande] = None
    ) -> List[DemandeBibliothecaire]:
        """
        Récupère toutes les demandes d'un utilisateur
        
        Args:
            email: Email de l'utilisateur
            statut: Filtrer par statut (optionnel)
        
        Returns:
            List[DemandeBibliothecaire]: Demandes de l'utilisateur
        """
        demandes = []
        
        for filename in os.listdir(self.demandes_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.demandes_dir, filename)
            demande = self._charger_demande_depuis_fichier(file_path)
            
            if demande and demande.email_demandeur == email:
                # Filtre par statut si spécifié
                if statut is None or demande.statut == statut:
                    demandes.append(demande)
        
        # Trier par date (plus récentes en premier)
        demandes.sort(key=lambda d: d.date_demande, reverse=True)
        
        return demandes
    
    def get_demandes_by_statut(
        self, 
        statut: StatutDemande
    ) -> List[DemandeBibliothecaire]:
        """
        Récupère toutes les demandes d'un certain statut
        
        Args:
            statut: Statut recherché
        
        Returns:
            List[DemandeBibliothecaire]: Demandes correspondantes
        """
        demandes = []
        
        for filename in os.listdir(self.demandes_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.demandes_dir, filename)
            demande = self._charger_demande_depuis_fichier(file_path)
            
            if demande and demande.statut == statut:
                demandes.append(demande)
        
        # Trier par date (plus anciennes en premier pour les demandes en attente)
        if statut == StatutDemande.EN_ATTENTE:
            demandes.sort(key=lambda d: d.date_demande)
        else:
            demandes.sort(key=lambda d: d.date_demande, reverse=True)
        
        return demandes
    
    def get_all_demandes(self, limit: Optional[int] = None) -> List[DemandeBibliothecaire]:
        """
        Récupère toutes les demandes
        
        Args:
            limit: Nombre max de résultats (optionnel)
        
        Returns:
            List[DemandeBibliothecaire]: Toutes les demandes
        """
        demandes = []
        
        for filename in os.listdir(self.demandes_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.demandes_dir, filename)
            demande = self._charger_demande_depuis_fichier(file_path)
            
            if demande:
                demandes.append(demande)
        
        # Trier par date (plus récentes en premier)
        demandes.sort(key=lambda d: d.date_demande, reverse=True)
        
        # Limiter si demandé
        if limit:
            demandes = demandes[:limit]
        
        return demandes
    
    def count_demandes_by_statut(self) -> dict:
        """
        Compte les demandes par statut
        
        Returns:
            dict: {"en_attente": 3, "approuvees": 5, ...}
        """
        counts = {
            "en_attente": 0,
            "approuvees": 0,
            "refusees": 0,
            "annulees": 0
        }
        
        for filename in os.listdir(self.demandes_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.demandes_dir, filename)
            demande = self._charger_demande_depuis_fichier(file_path)
            
            if demande:
                if demande.statut == StatutDemande.EN_ATTENTE:
                    counts["en_attente"] += 1
                elif demande.statut == StatutDemande.APPROUVEE:
                    counts["approuvees"] += 1
                elif demande.statut == StatutDemande.REFUSEE:
                    counts["refusees"] += 1
                elif demande.statut == StatutDemande.ANNULEE:
                    counts["annulees"] += 1
        
        return counts
    
    # ========================================
    # NETTOYAGE (optionnel)
    # ========================================
    
    def archiver_demandes_anciennes(self, jours: int = 365):
        """
        Archive les demandes traitées de plus de X jours
        
        Args:
            jours: Nombre de jours avant archivage
        """
        import shutil
        
        archive_dir = os.path.join(self.root_dir, "data", "archives_demandes")
        os.makedirs(archive_dir, exist_ok=True)
        
        seuil = datetime.now().timestamp() - (jours * 24 * 60 * 60)
        archived_count = 0
        
        for filename in os.listdir(self.demandes_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(self.demandes_dir, filename)
            demande = self._charger_demande_depuis_fichier(file_path)
            
            if demande and demande.date_reponse:
                if demande.date_reponse.timestamp() < seuil:
                    # Archiver
                    archive_path = os.path.join(archive_dir, filename)
                    shutil.move(file_path, archive_path)
                    archived_count += 1
        
        if archived_count > 0:
            self.repo.index.commit(f"Archive: {archived_count} demandes anciennes")
            print(f"[RepoDemandesPromotion] {archived_count} demandes archivées")


