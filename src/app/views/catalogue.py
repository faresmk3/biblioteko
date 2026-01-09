# ============================================
# FICHIER NOUVEAU: src/app/views/catalogue.py
# ============================================
"""
Vues pour accéder aux catalogues (fond commun, séquestre)
"""
import os
from pyramid.view import view_config


@view_config(route_name='api_fond_commun', renderer='json', request_method='GET')
def liste_fond_commun(request):
    """
    GET /api/catalogue/fond-commun
    
    Liste toutes les œuvres du domaine public / fond commun
    
    Returns:
    {
        "total": 10,
        "oeuvres": [...]
    }
    """
    repo = request.registry.repo_oeuvres
    
    # Chemin vers le dossier fond_commun
    path = os.path.join(repo.root_dir, "data", "fond_commun")
    
    oeuvres = []
    
    if os.path.exists(path):
        for filename in os.listdir(path):
            if filename.endswith(".md"):
                try:
                    with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                        data = repo._parse_from_markdown(f.read())
                        
                        oeuvres.append({
                            "id": filename,
                            "titre": data.get("titre", "Sans titre"),
                            "auteur": data.get("auteur", "Auteur inconnu"),
                            "fichier": data.get("fichier", ""),
                            "date_publication": data.get("date", ""),
                            "etat": data.get("etat", "VALIDEE"),
                            "categories": data.get("categories", [])
                        })
                except Exception as e:
                    print(f"Erreur lecture {filename}: {e}")
    
    return {
        "catalogue": "Fond Commun (Domaine Public)",
        "total": len(oeuvres),
        "oeuvres": oeuvres
    }


@view_config(route_name='api_sequestre', renderer='json', request_method='GET')
def liste_sequestre(request):
    """
    GET /api/catalogue/sequestre
    
    Liste toutes les œuvres en attente de libération (séquestre)
    
    Returns:
    {
        "total": 5,
        "oeuvres": [...]
    }
    """
    repo = request.registry.repo_oeuvres
    
    # Chemin vers le dossier séquestre
    path = os.path.join(repo.root_dir, "data", "sequestre")
    
    oeuvres = []
    
    if os.path.exists(path):
        for filename in os.listdir(path):
            if filename.endswith(".md"):
                try:
                    with open(os.path.join(path, filename), 'r', encoding='utf-8') as f:
                        data = repo._parse_from_markdown(f.read())
                        
                        oeuvres.append({
                            "id": filename,
                            "titre": data.get("titre", "Sans titre"),
                            "auteur": data.get("auteur", "Auteur inconnu"),
                            "date_liberation": data.get("date_liberation", "Non définie"),
                            "statut_droit": data.get("statut_droit", "SEQUESTRE"),
                            "fichier": data.get("fichier", "")
                        })
                except Exception as e:
                    print(f"Erreur lecture {filename}: {e}")
    
    return {
        "catalogue": "Séquestre (En attente de libération)",
        "total": len(oeuvres),
        "oeuvres": oeuvres,
        "info": "Ces œuvres seront transférées automatiquement au fond commun à leur date de libération"
    }


@view_config(route_name='api_catalogues_stats', renderer='json', request_method='GET')
def statistiques_catalogues(request):
    """
    GET /api/catalogue/stats
    
    Statistiques sur tous les catalogues
    (Route bonus non définie dans routes.py mais utile)
    """
    repo = request.registry.repo_oeuvres
    
    def compter_oeuvres(dossier):
        path = os.path.join(repo.root_dir, "data", dossier)
        if not os.path.exists(path):
            return 0
        return len([f for f in os.listdir(path) if f.endswith(".md")])
    
    stats = {
        "a_moderer": compter_oeuvres("a_moderer"),
        "fond_commun": compter_oeuvres("fond_commun"),
        "sequestre": compter_oeuvres("sequestre"),
        "archives": compter_oeuvres("archives")
    }
    
    stats["total"] = sum(stats.values())
    
    return {
        "statistiques": stats,
        "details": {
            "en_attente_moderation": stats["a_moderer"],
            "disponibles_publiquement": stats["fond_commun"],
            "en_attente_liberation": stats["sequestre"],
            "rejetees": stats["archives"]
        }
    }


@view_config(route_name='api_oeuvre_detail', renderer='json', request_method='GET')
def detail_oeuvre_catalogue(request):
    """
    GET /api/catalogue/oeuvre/{id}
    
    Détails complets d'une œuvre dans le catalogue
    (Route bonus non définie dans routes.py mais utile)
    """
    repo = request.registry.repo_oeuvres
    id_oeuvre = request.matchdict['id']
    
    # Chercher dans tous les catalogues
    oeuvre = repo.get_oeuvre_by_id(id_oeuvre)
    
    if not oeuvre:
        request.response.status = 404
        return {"error": "Œuvre introuvable"}
    
    return {
        "id": oeuvre.fichier_nom,
        "titre": oeuvre.titre,
        "auteur": oeuvre.auteur,
        "etat": oeuvre.etat.nom,
        "soumis_par": oeuvre.soumis_par_email,
        "date_soumission": oeuvre.date_soumission,
        "categories": [c.value for c in oeuvre.categories],
        "metadonnees": oeuvre.metadonnees,
        "statut_droit": oeuvre.statut_droit.value if hasattr(oeuvre, 'statut_droit') else None,
        "resultats_ocr": list(oeuvre.resultats_ocr.keys()) if oeuvre.resultats_ocr else []
    }