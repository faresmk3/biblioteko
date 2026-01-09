# ============================================
# FICHIER NOUVEAU: src/app/views/multi_ia.py
# ============================================
"""
Vues pour la reconnaissance multi-IA (Tesseract, Gemini, Pixtral)
"""
import os
import tempfile
from pyramid.view import view_config
from src.app.auth.decorators import require_permission
from src.app.domain.services import ServiceReconnaissanceIA


@view_config(route_name='api_ocr_multi_ia', renderer='json', request_method='POST')
@require_permission('peut_moderer_oeuvre')
def ocr_multi_ia(request):
    """
    POST /api/oeuvres/{id}/ocr-multi-ia
    
    Headers:
        Authorization: Bearer TOKEN (avec permission modérer)
    
    Body: multipart/form-data avec image
    
    Returns:
    {
        "success": true,
        "resultats": {
            "tesseract": "...",
            "gemini": "...",
            "pixtral": "..."
        },
        "meilleur": "gemini"
    }
    """
    service_ia = ServiceReconnaissanceIA()
    id_oeuvre = request.matchdict['id']
    
    # Récupérer le fichier image uploadé
    image_file = request.POST.get('image')
    
    if not image_file or not hasattr(image_file, 'filename'):
        request.response.status = 400
        return {"error": "Fichier image requis"}
    
    # Sauvegarder temporairement l'image
    temp_image = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    
    try:
        image_file.file.seek(0)
        temp_image.write(image_file.file.read())
        temp_image.close()
        
        # Lancer la reconnaissance avec les 3 IA
        resultats = service_ia.comparer_trois_ia(temp_image.name)
        
        # Déterminer le meilleur résultat
        meilleur = service_ia.meilleur_resultat(resultats)
        meilleur_ia = max(
            resultats.keys(), 
            key=lambda ia: len(resultats[ia].split())
        )
        
        # Enregistrer les résultats dans l'œuvre
        service_oeuvre = request.registry.service_oeuvre
        oeuvre = service_oeuvre.recuperer_oeuvre(id_oeuvre)
        
        if oeuvre:
            for ia_name, texte in resultats.items():
                oeuvre.enregistrer_resultat_ocr(ia_name, texte)
            
            # Sauvegarder l'œuvre avec les résultats
            request.registry.repo_oeuvres.sauvegarder(oeuvre)
        
        return {
            "success": True,
            "oeuvre": oeuvre.titre if oeuvre else id_oeuvre,
            "resultats": resultats,
            "meilleur_ia": meilleur_ia,
            "meilleur_texte": meilleur,
            "statistiques": {
                ia: {
                    "nb_mots": len(texte.split()),
                    "nb_caracteres": len(texte)
                }
                for ia, texte in resultats.items()
            }
        }
    
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors de l'OCR : {str(e)}"}
    
    finally:
        # Nettoyage
        if os.path.exists(temp_image.name):
            os.unlink(temp_image.name)


@view_config(route_name='api_comparer_ia', renderer='json', request_method='GET')
@require_permission('peut_moderer_oeuvre')
def comparer_ia(request):
    """
    GET /api/oeuvres/{id}/comparer-ia
    
    Headers:
        Authorization: Bearer TOKEN (avec permission modérer)
    
    Retourne les résultats OCR déjà enregistrés pour cette œuvre
    
    Returns:
    {
        "oeuvre": "Titre",
        "resultats_disponibles": ["tesseract", "gemini"],
        "scores": {...}
    }
    """
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    
    try:
        oeuvre = service.recuperer_oeuvre(id_oeuvre)
        
        if not oeuvre:
            request.response.status = 404
            return {"error": "Œuvre introuvable"}
        
        # Vérifier s'il y a des résultats OCR
        if not oeuvre.resultats_ocr:
            return {
                "oeuvre": oeuvre.titre,
                "message": "Aucun résultat OCR disponible",
                "aide": "Utilisez POST /api/oeuvres/{id}/ocr-multi-ia pour lancer une analyse"
            }
        
        # Comparer les résultats
        scores = oeuvre.comparer_qualite_ocr()
        
        # Déterminer le meilleur
        meilleur_ia = max(scores.keys(), key=lambda ia: scores[ia]['score'])
        
        return {
            "oeuvre": oeuvre.titre,
            "resultats_disponibles": list(oeuvre.resultats_ocr.keys()),
            "scores": scores,
            "meilleur_ia": meilleur_ia,
            "recommandation": f"Le résultat de {meilleur_ia.upper()} semble le plus complet"
        }
    
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors de la comparaison : {str(e)}"}


@view_config(route_name='api_resultat_ia', renderer='json', request_method='GET')
def obtenir_resultat_ia(request):
    """
    GET /api/oeuvres/{id}/resultat-ia/{ia}
    
    Récupère le texte complet d'une IA spécifique
    (Route bonus non définie dans routes.py mais utile)
    
    Exemple: GET /api/oeuvres/Livre.md/resultat-ia/gemini
    """
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    ia_name = request.matchdict.get('ia', 'gemini')
    
    oeuvre = service.recuperer_oeuvre(id_oeuvre)
    
    if not oeuvre:
        request.response.status = 404
        return {"error": "Œuvre introuvable"}
    
    if ia_name not in oeuvre.resultats_ocr:
        return {
            "error": f"Pas de résultat pour {ia_name}",
            "disponibles": list(oeuvre.resultats_ocr.keys())
        }
    
    return {
        "oeuvre": oeuvre.titre,
        "ia": ia_name,
        "texte": oeuvre.resultats_ocr[ia_name]
    }