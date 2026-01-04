# src/app/domain/services.py
import os
from typing import List, Optional
from src.app.domain.modeles import Oeuvre, Utilisateur
from src.app.infra.pdf_to_md import PDFToMarkdownConverter
from datetime import datetime


class ServiceOeuvre:
    def __init__(self, depot_git):
        # On injecte le dépôt Git (Infrastructure) pour ne pas être lié à une technologie précise
        self.depot = depot_git
        self.pdf_converter = PDFToMarkdownConverter(
            dpi=300,
            left_margin_ratio=0.26,
            lang="fra"
        )

    def lister_oeuvres_a_moderer(self, demandeur: Utilisateur) -> List[Oeuvre]:
        """
        Correspond au diagramme : listerOeuvresAModerer(demandeur)
        Vérifie le RBAC avant de lister.
        """
        # 1. Vérification des droits (RBAC)
        if not demandeur.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé : Vous n'êtes pas modérateur.")

        # 2. Appel à l'infra (Git)
        return self.depot.lister_oeuvres_en_attente()

    def recuperer_oeuvre(self, id_oeuvre: str) -> Optional[Oeuvre]:
        return self.depot.get_oeuvre_by_id(id_oeuvre)

    def traiter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str) -> Oeuvre:
        """
        Correspond au diagramme : traiterOeuvre(biblio, id)
        Passe l'oeuvre à l'état EN_TRAITEMENT (Verrouillage)
        """
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")

        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        if not oeuvre:
            raise ValueError("Œuvre introuvable.")

        # Pattern State : Transition d'état
        oeuvre.traiter()
        
        # Persistance de l'état (Sauvegarde Git)
        self.depot.sauvegarder(oeuvre)
        
        return oeuvre

    def valider_oeuvre(self, biblio: Utilisateur, id_oeuvre: str, destination: str):
        """
        Correspond au diagramme : validerOeuvre(biblio, id)
        """
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")

        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        
        # Pattern State : Validation
        oeuvre.accepter() 
        
        # Logique métier : Déplacement vers le dossier final (Fond commun ou Séquestre)
        self.depot.deplacer_vers_catalogue(oeuvre, destination)
        
        return f"L'œuvre '{oeuvre.titre}' a été validée et publiée dans {destination}."

    def rejeter_oeuvre(self, biblio: Utilisateur, id_oeuvre: str, motif: str):
        """
        Correspond au diagramme : rejeterOeuvre(biblio, id, motif)
        """
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé.")

        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        
        # Pattern State : Rejet
        oeuvre.refuser()
        
        # Logique métier : Déplacement vers archives ou suppression
        self.depot.archiver_rejet(oeuvre, motif)
        
        return f"L'œuvre a été rejetée pour le motif : {motif}"
    

    # Ajoutez ceci à la fin de la classe ServiceOeuvre dans src/app/domain/services.py
    def soumettre_oeuvre(self, oeuvre: Oeuvre):
        """
        Enregistre une nouvelle œuvre proposée par un membre.
        """
        # On pourrait ajouter ici des règles métier (ex: vérification doublon)
        self.depot.sauvegarder(oeuvre)
        return oeuvre
    




    # ============================================
    # NOUVELLES MÉTHODES : Conversion PDF
    # ============================================
    
    def soumettre_oeuvre_depuis_pdf(
        self, 
        pdf_path: str,
        titre: str,
        auteur: str,
        soumis_par: Utilisateur
    ) -> Oeuvre:
        """
        Soumet une œuvre à partir d'un fichier PDF.
        Convertit le PDF en Markdown avant de créer l'œuvre.
        
        Args:
            pdf_path: Chemin vers le fichier PDF uploadé
            titre: Titre de l'œuvre
            auteur: Auteur de l'œuvre
            soumis_par: Utilisateur qui soumet
            
        Returns:
            Oeuvre: L'œuvre créée
        """
        print(f"[Service] Conversion PDF -> MD pour '{titre}'")
        
        try:
            # 1. Déterminer le chemin de sortie
            output_dir = os.path.join(self.depot.root_dir, "data", "a_moderer")
            os.makedirs(output_dir, exist_ok=True)
            
            # 2. Nom de fichier sécurisé
            safe_titre = "".join(c for c in titre if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_titre = safe_titre.replace(' ', '_')
            md_filename = f"{safe_titre}.md"
            md_path = os.path.join(output_dir, md_filename)
            
            # 3. Conversion PDF -> Markdown
            self.pdf_converter.convert(pdf_path, md_path)
            
            # 4. Lecture du contenu généré
            with open(md_path, 'r', encoding='utf-8') as f:
                contenu_md = f.read()
            
            # 5. Création de l'entité Oeuvre
            oeuvre = Oeuvre(
                titre=titre,
                auteur=auteur,
                fichier_nom=md_filename,
                soumis_par=soumis_par
            )
            
            # Ajout de métadonnées
            oeuvre.set_metadonnee("pdf_source", pdf_path)
            oeuvre.set_metadonnee("date_conversion", datetime.now().isoformat())
            oeuvre.set_metadonnee("contenu_md", contenu_md)
            
            # 6. Sauvegarde
            self.depot.sauvegarder(oeuvre)
            
            print(f"[Service] ✅ Œuvre créée : {oeuvre.titre}")
            return oeuvre
            
        except Exception as e:
            raise RuntimeError(f"Échec de la conversion PDF: {e}")
        finally:
            self.pdf_converter.cleanup()
    
    def reconvertir_oeuvre_pdf(
        self, 
        biblio: Utilisateur, 
        id_oeuvre: str,
        dpi: int = 300,
        langue: str = "fra"
    ) -> str:
        """
        Reconvertit une œuvre PDF avec des paramètres personnalisés.
        """
        if not biblio.a_la_permission("peut_moderer_oeuvre"):
            raise PermissionError("Accès refusé : Seuls les modérateurs peuvent reconvertir.")
        
        oeuvre = self.depot.get_oeuvre_by_id(id_oeuvre)
        if not oeuvre:
            raise ValueError("Œuvre introuvable.")
        
        pdf_source = oeuvre.metadonnees.get('pdf_source')
        if not pdf_source or not os.path.exists(pdf_source):
            raise ValueError("Aucun fichier PDF source trouvé pour cette œuvre.")
        
        converter = PDFToMarkdownConverter(dpi=dpi, lang=langue)
        try:
            # Reconversion
            output_path = os.path.join(self.depot.root_dir, "data", "a_moderer", oeuvre.fichier_nom)
            converter.convert(pdf_source, output_path)
            
            #Mise à jour des métadonnées
            oeuvre.set_metadonnee('derniere_conversion', datetime.now().isoformat())
            oeuvre.set_metadonnee('dpi_conversion', str(dpi))
            oeuvre.set_metadonnee('langue_conversion', langue)
            
            self.depot.sauvegarder(oeuvre)
            
            return output_path
            
        finally:
            converter.cleanup()


    # Dans src/app/domain/services.py

    def convertir_pdf_simple(self, pdf_path: str) -> str:
        """
        Convertit le PDF en MD et retourne le chemin du fichier temporaire.
        Ne crée PAS d'objet Oeuvre en base.
        """
        import tempfile
        
        # Création d'un fichier temporaire pour le résultat MD
        temp_md = tempfile.NamedTemporaryFile(delete=False, suffix='.md')
        temp_md_path = temp_md.name
        temp_md.close()

        try:
            # Conversion
            self.pdf_converter.convert(pdf_path, temp_md_path)
            return temp_md_path
        except Exception as e:
            if os.path.exists(temp_md_path):
                os.unlink(temp_md_path)
            raise e