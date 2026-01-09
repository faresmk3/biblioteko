# ============================================
# FICHIER COMPLET CORRIGÉ
# ============================================

"""
Remplacez TOUT le contenu de src/app/infra/repositories.py par ceci :
"""

# src/app/infra/repositories.py
import os
import git
from typing import List, Optional, Dict
from src.app.domain.modeles import Oeuvre, Utilisateur
import json
from datetime import datetime, timedelta


class FileSystemGitRepository:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        
        # Initialisation du dépôt Git
        try:
            self.repo = git.Repo(self.root_dir)
        except git.exc.InvalidGitRepositoryError:
            print(f"[Infra] Init Git dans {self.root_dir}")
            self.repo = git.Repo.init(self.root_dir)

    def _get_path(self, dossier: str, filename: str) -> str:
        return os.path.join(self.root_dir, "data", dossier, filename)

    def _ensure_dir(self, dossier: str):
        os.makedirs(os.path.join(self.root_dir, "data", dossier), exist_ok=True)

    # --- Gestion du format Markdown + Frontmatter ---

    def _serialize_to_markdown(self, oeuvre: Oeuvre) -> str:
        def safe(val): return str(val).replace('"', '\\"')

        md = f'titre: "{safe(oeuvre.titre)}"\n'
        md += f'auteur: "{safe(oeuvre.auteur)}"\n'
        md += f'fichier: "{safe(oeuvre.fichier_nom)}"\n'
        md += f'soumis_par: "{safe(oeuvre.soumis_par_email)}"\n'
        md += f'date: "{safe(oeuvre.date_soumission)}"\n'
        md += f'etat: "{safe(oeuvre.etat.nom)}"\n'
        
        for k, v in oeuvre.metadonnees.items():
            md += f'{k}: "{safe(v)}"\n'
        
        return md

    def _parse_from_markdown(self, content: str) -> Dict:
        data = {}
        lines = content.split('\n')
        if lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip().strip('"')
        else:
            # Pas de délimiteurs ---, on parse directement
            for line in lines:
                if ":" in line:
                    key, val = line.split(":", 1)
                    data[key.strip()] = val.strip().strip('"')
        return data

    # ========================================
    # MÉTHODES PRINCIPALES
    # ========================================

    def sauvegarder(self, oeuvre: Oeuvre):
        """Sauvegarde une œuvre selon son état"""
        if oeuvre.etat.nom in ["SOUMISE", "EN_TRAITEMENT"]:
            dossier = "a_moderer"
        elif oeuvre.etat.nom == "VALIDEE":
            dossier = "fond_commun"
        else:
            dossier = "archives"

        self._ensure_dir(dossier)
        safe_filename = f"{oeuvre.titre.replace(' ', '_')}.md"
        full_path = self._get_path(dossier, safe_filename)

        content = self._serialize_to_markdown(oeuvre)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.repo.index.add([full_path])
        self.repo.index.commit(f"Maj: {oeuvre.titre} -> {oeuvre.etat.nom}")
        print(f"[Git] Sauvegardé : {safe_filename}")

    def lister_oeuvres_en_attente(self) -> List[Oeuvre]:
        """Liste les œuvres à modérer"""
        oeuvres = []
        path = os.path.join(self.root_dir, "data", "a_moderer")
        
        if not os.path.exists(path):
            return []

        for filename in os.listdir(path):
            if filename.endswith(".md"):
                try:
                    with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                        data = self._parse_from_markdown(f.read())
                        
                        user_stub = Utilisateur(
                            nom="Inconnu", 
                            prenom="", 
                            email=data.get("soumis_par", "inconnu"), 
                            mdp=""
                        )
                        
                        o = Oeuvre(
                            titre=data.get("titre", "Sans titre"),
                            auteur=data.get("auteur", "Inconnu"),
                            fichier_nom=data.get("fichier", ""),
                            soumis_par=user_stub
                        )
                        oeuvres.append(o)
                except Exception as e:
                    print(f"Erreur lecture {filename}: {e}")
        return oeuvres

    def get_oeuvre_by_id(self, id_oeuvre: str) -> Optional[Oeuvre]:
        """
        Récupère une œuvre par son ID
        ✅ CORRIGÉ : Restaure l'état directement sans passer par les transitions
        """
        for dossier in ["a_moderer", "fond_commun", "sequestre", "archives"]:
            path = self._get_path(dossier, id_oeuvre)
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = self._parse_from_markdown(f.read())
                    
                    user_stub = Utilisateur(
                        nom="Inconnu", 
                        prenom="", 
                        email=data.get("soumis_par", "inconnu"), 
                        mdp=""
                    )
                    
                    o = Oeuvre(
                        data.get("titre", "Sans titre"), 
                        data.get("auteur", "Inconnu"), 
                        data.get("fichier", ""), 
                        user_stub
                    )
                    
                    # ✅ CORRECTION : Restaurer l'état DIRECTEMENT
                    etat_str = data.get("etat")
                    
                    if etat_str == "EN_TRAITEMENT":
                        from src.app.domain.modeles import EtatEnTraitement
                        o._etat_actuel = EtatEnTraitement()
                        
                    elif etat_str == "VALIDEE":
                        from src.app.domain.modeles import EtatValidee
                        o._etat_actuel = EtatValidee()
                        
                    elif etat_str == "REFUSEE":
                        from src.app.domain.modeles import EtatRefusee
                        o._etat_actuel = EtatRefusee()
                    
                    # Si "SOUMISE", on ne fait rien (état par défaut)
                    
                    return o
        return None

    def deplacer_vers_catalogue(self, oeuvre: Oeuvre, destination: str):
        """Déplace une œuvre vers un catalogue (fond_commun, etc.)"""
        filename = f"{oeuvre.titre.replace(' ', '_')}.md"
        old_path = self._get_path("a_moderer", filename)
        new_path = self._get_path(destination, filename)
        self._ensure_dir(destination)

        if os.path.exists(old_path):
            content = self._serialize_to_markdown(oeuvre)
            
            # Écrire dans le nouveau dossier
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Supprimer l'ancien
            os.remove(old_path)

            # Git
            self.repo.index.remove([old_path])
            self.repo.index.add([new_path])
            self.repo.index.commit(f"Publication: {oeuvre.titre}")

    def archiver_rejet(self, oeuvre: Oeuvre, motif: str):
        """Archive une œuvre rejetée"""
        oeuvre.set_metadonnee("motif_rejet", motif)
        
        filename = f"{oeuvre.titre.replace(' ', '_')}.md"
        old_path = self._get_path("a_moderer", filename)
        new_path = self._get_path("archives", filename)
        
        self._ensure_dir("archives")
        
        content = self._serialize_to_markdown(oeuvre)
        with open(new_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if os.path.exists(old_path):
            os.remove(old_path)
            self.repo.index.remove([old_path])
        
        self.repo.index.add([new_path])
        self.repo.index.commit(f"Rejet: {oeuvre.titre}")

    def lire_contenu_oeuvre(self, id_oeuvre: str) -> bytes:
        """Lit le contenu d'une œuvre pour chiffrement"""
        for dossier in ["a_moderer", "fond_commun", "sequestre"]:
            path = self._get_path(dossier, id_oeuvre)
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    return f.read()
        
        raise FileNotFoundError(f"Oeuvre '{id_oeuvre}' introuvable")

    def sauvegarder_emprunt(self, emprunt):
        """Sauvegarde un emprunt"""
        import json
        
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
        print(f"[Git] Emprunt sauvegardé : {emprunt.id}")

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
        """Liste toutes les œuvres (tous dossiers)"""
        toutes = []
        for dossier in ["a_moderer", "fond_commun", "sequestre", "archives"]:
            path = os.path.join(self.root_dir, "data", dossier)
            if not os.path.exists(path):
                continue
            
            for filename in os.listdir(path):
                if filename.endswith(".md"):
                    try:
                        with open(os.path.join(path, filename), 'r') as f:
                            data = self._parse_from_markdown(f.read())
                            user_stub = Utilisateur("Inc", "", data.get("soumis_par", "?"), "")
                            o = Oeuvre(
                                data.get("titre", "?"),
                                data.get("auteur", "?"),
                                data.get("fichier", ""),
                                user_stub
                            )
                            toutes.append(o)
                    except:
                        pass
        return toutes




# ============================================
# AJOUT À src/app/infra/repositories.py
# À AJOUTER À LA FIN DU FICHIER EXISTANT
# ============================================

import json
from typing import Optional

class RepoUtilisateurs:
    """
    Gestion des utilisateurs dans un fichier JSON
    
    STRUCTURE SUPPORTÉE :
    {
      "email@example.com": {
        "nom": "Nom",
        "prenom": "Prenom",
        "email": "email@example.com",
        "roles": ["Role"],
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
            print(f"[RepoUsers] Dossier créé : {users_dir}")
        
        # Initialiser le fichier s'il n'existe pas
        if not os.path.exists(users_file):
            self._init_users_file()
            print(f"[RepoUsers] Fichier initialisé : {users_file}")
    
    def _init_users_file(self):
        """Initialise le fichier users.json vide"""
        initial_data = {}
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2, ensure_ascii=False)
        
        print(f"[RepoUsers] Fichier users.json créé")
    
    def _load_users(self) -> Dict:
        """Charge les utilisateurs depuis le JSON"""
        try:
            if not os.path.exists(self.users_file):
                print(f"[RepoUsers] Fichier inexistant, création...")
                self._init_users_file()
                return {}
            
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data
        
        except json.JSONDecodeError as e:
            print(f"[RepoUsers] ERREUR JSON : {e}")
            return {}
        
        except Exception as e:
            print(f"[RepoUsers] ERREUR : {e}")
            return {}
    
    def _save_users(self, data: Dict):
        """Sauvegarde les utilisateurs dans le JSON"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[RepoUsers] ERREUR sauvegarde : {e}")
    
    def save_user(self, utilisateur: Utilisateur):
        """
        Sauvegarde un utilisateur
        Utilise l'email comme clé
        """
        data = self._load_users()
        
        user_dict = {
            "nom": utilisateur.nom,
            "prenom": utilisateur.prenom,
            "email": utilisateur.email,
            "courriel": utilisateur.email,
            "roles": [r.nom_role for r in utilisateur.roles],
            "espace_disque_mb": getattr(utilisateur, 'espace_disque_mb', 1000),
            "date_inscription": getattr(utilisateur, 'date_inscription', datetime.now()).isoformat() if hasattr(getattr(utilisateur, 'date_inscription', None), 'isoformat') else datetime.now().isoformat()
        }
        
        # Utiliser l'email comme clé
        data[utilisateur.email] = user_dict
        
        self._save_users(data)
        print(f"[RepoUsers] Utilisateur sauvegardé : {utilisateur.email}")
    
    def get_by_email(self, email: str) -> Optional[Utilisateur]:
        """
        Récupère un utilisateur par email
        ADAPTÉ À VOTRE STRUCTURE : email comme clé
        """
        try:
            data = self._load_users()
            
            # Chercher l'utilisateur avec email comme clé
            if email in data:
                u = data[email]
                
                # Créer l'objet Utilisateur
                from src.app.domain.modeles import PermissionsSysteme, Role
                
                user = Utilisateur(
                    u.get("nom", "Inconnu"),
                    u.get("prenom", ""),
                    u.get("email"),
                    ""  # Pas de mot de passe pour la récupération
                )
                
                # Restaurer les rôles
                for role_name in u.get("roles", []):
                    if role_name == "Bibliothécaire":
                        role = PermissionsSysteme.creer_role_bibliothecaire()
                    elif role_name == "Membre":
                        role = PermissionsSysteme.creer_role_membre()
                    else:
                        # Rôle custom
                        role = Role(role_name)
                    
                    user.ajouter_role(role)
                
                return user
            
            # Utilisateur non trouvé
            print(f"[RepoUsers] Utilisateur non trouvé : {email}")
            return None
        
        except Exception as e:
            print(f"[RepoUsers] ERREUR dans get_by_email : {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def list_all(self) -> List[Dict]:
        """Liste tous les utilisateurs"""
        data = self._load_users()
        return list(data.values())
    
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
