# ============================================
# FICHIER 6: Script de test CLI
# src/cli/test_pdf_conversion.py
# ============================================
"""
Script pour tester la conversion PDF en ligne de commande
"""
import os
import sys
from datetime import datetime
import shutil
from src.app.domain.modeles import Utilisateur
from src.app.domain.services import ServiceOeuvre
from src.app.infra.repositories import FileSystemGitRepository

def test_conversion_pdf(pdf_path, titre, auteur):
    """Test de conversion d'un PDF"""
    
    # Setup
    repo = FileSystemGitRepository(os.getcwd())
    service = ServiceOeuvre(repo)
    
    # Utilisateur de test
    membre = Utilisateur(
        nom="Test",
        prenom="User",
        email="test@example.com",
        mdp="pass"
    )
    
    print(f"🔄 Conversion du PDF: {pdf_path}")
    print(f"   Titre: {titre}")
    print(f"   Auteur: {auteur}")
    print()
    
    try:
        oeuvre = service.soumettre_oeuvre_depuis_pdf(
            pdf_path=pdf_path,
            titre=titre,
            auteur=auteur,
            soumis_par=membre
        )
        
        print("✅ Conversion réussie!")
        print(f"   ID: {oeuvre.fichier_nom}")
        print(f"   État: {oeuvre.etat.nom}")
        print(f"   Fichier: data/a_moderer/{oeuvre.fichier_nom}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test conversion PDF")
    parser.add_argument("pdf", help="Chemin vers le PDF")
    parser.add_argument("--titre", required=True, help="Titre de l'œuvre")
    parser.add_argument("--auteur", default="Auteur inconnu", help="Auteur")
    
    args = parser.parse_args()
    test_conversion_pdf(args.pdf, args.titre, args.auteur)