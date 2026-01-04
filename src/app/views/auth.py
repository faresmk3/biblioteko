# src/app/views/api.py (NETTOYÉ)
import os
import tempfile
from pyramid.view import view_config
from src.app.domain.modeles import Oeuvre, Utilisateur
from src.app.auth.decorators import require_auth, require_permission

# --- LISTE ET MODÉRATION ---

@view_config(route_name='api_oeuvres', renderer='json', request_method='GET')
@require_permission('peut_moderer_oeuvre') # Remplace get_fake_user
def api_lister_oeuvres(request):
    service = request.registry.service_oeuvre
    # request.user est injecté par le décorateur
    oeuvres = service.lister_oeuvres_a_moderer(request.user) 
    return [
        {
            "id": o.fichier_nom,
            "titre": o.titre,
            "auteur": o.auteur,
            "fichier": o.fichier_nom,
            "soumisPar": o.soumis_par_email,
            "etat": o.etat.nom,
            "dateSoumission": o.date_soumission
        }
        for o in oeuvres
    ]

@view_config(route_name='api_traiter', renderer='json', request_method='POST')
@require_permission('peut_moderer_oeuvre')
def api_traiter(request):
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    service.traiter_oeuvre(request.user, id_oeuvre)
    return {"success": True, "message": "Œuvre en cours de traitement"}

@view_config(route_name='api_valider', renderer='json', request_method='POST')
@require_permission('peut_moderer_oeuvre')
def api_valider(request):
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    destination = request.json_body.get('destination', 'fond_commun')
    msg = service.valider_oeuvre(request.user, id_oeuvre, destination)
    return {"success": True, "message": msg}

@view_config(route_name='api_rejeter', renderer='json', request_method='POST')
@require_permission('peut_moderer_oeuvre')
def api_rejeter(request):
    service = request.registry.service_oeuvre
    id_oeuvre = request.matchdict['id']
    motif = request.json_body.get('motif', 'Non spécifié')
    msg = service.rejeter_oeuvre(request.user, id_oeuvre, motif)
    return {"success": True, "message": msg}

# --- DÉPÔT ET CONVERSION ---

@view_config(route_name='api_depot', renderer='json', request_method='POST')
@require_auth # Sécurisé
def api_depot(request):
    service = request.registry.service_oeuvre
    titre = request.POST.get('titre')
    auteur = request.POST.get('auteur', 'Inconnu')
    fichier_input = request.POST.get('fichier')
    
    filename = fichier_input.filename if hasattr(fichier_input, 'filename') else "inconnu.pdf"
    
    if not titre:
        request.response.status = 400
        return {"error": "Titre requis"}

    nouvelle_oeuvre = Oeuvre(titre, auteur, filename, request.user)
    service.soumettre_oeuvre(nouvelle_oeuvre)
    return {"success": True, "message": f"Œuvre '{titre}' reçue !"}

@view_config(route_name='api_depot_pdf', renderer='json', request_method='POST')
@require_auth
def api_depot_pdf(request):
    service = request.registry.service_oeuvre
    titre = request.POST.get('titre')
    auteur = request.POST.get('auteur', 'Auteur inconnu')
    pdf_file = request.POST.get('pdf')

    if not pdf_file or not hasattr(pdf_file, 'filename'):
        request.response.status = 400
        return {"error": "PDF requis"}

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        pdf_file.file.seek(0)
        temp_pdf.write(pdf_file.file.read())
        temp_path = temp_pdf.name

    try:
        # On utilise request.user (le membre connecté)
        oeuvre = service.soumettre_oeuvre_depuis_pdf(
            pdf_path=temp_path,
            titre=titre,
            auteur=auteur,
            soumis_par=request.user
        )
        return {"success": True, "message": "Conversion réussie", "id": oeuvre.fichier_nom}
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)

@view_config(route_name='api_convertir_pdf', renderer='json', request_method='POST')
def api_convertir_pdf(request):
    """Conversion simple sans auth (pour démo) ou avec @require_auth si besoin"""
    from src.app.infra.pdf_to_md import PDFToMarkdownConverter
    pdf_file = request.POST.get('pdf')
    
    if not pdf_file or not hasattr(pdf_file, 'filename'):
        return {"error": "PDF requis"}

    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
        pdf_file.file.seek(0)
        temp_pdf.write(pdf_file.file.read())
        temp_path = temp_pdf.name
        
    try:
        converter = PDFToMarkdownConverter()
        # Note: assurez-vous que votre converter.convert renvoie le chemin du MD ou le contenu
        # Ici on suppose qu'il retourne le chemin
        md_path = converter.convert(temp_path) 
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"success": True, "contenu_md": content}
    except Exception as e:
        return {"error": str(e)}
    finally:
        if os.path.exists(temp_path): os.unlink(temp_path)