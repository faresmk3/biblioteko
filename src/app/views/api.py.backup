# src/app/views/api.py
from pyramid.view import view_config
import os       # <--- À ajouter
import tempfile # <--- À ajouter
from pyramid.response import Response
from pyramid.response import FileResponse # <--- AJOUTER CET IMPORT
from src.app.domain.modeles import Utilisateur, Role, Permission, Oeuvre

# Helper pour simuler l'utilisateur connecté (car on n'a pas encore fait l'auth JWT côté Python)
def get_fake_user(request):
    # Pour le MVP, on considère que tout le monde est admin "Jean"
    perm = Permission("peut_moderer_oeuvre")
    role = Role("Bibliothécaire")
    role.ajouter_permission(perm)
    u = Utilisateur("Admin", "Jean", "biblio@culture.org", "pass")
    u.ajouter_role(role)
    return u

# 1. Liste des œuvres
@view_config(route_name='api_oeuvres', renderer='json', request_method='GET')
def api_lister_oeuvres(request):
    service = request.registry.service_oeuvre
    user = get_fake_user(request)
    
    try:
        oeuvres = service.lister_oeuvres_a_moderer(user)
        # Transformation en dictionnaires pour le JSON
        return [
            {
                "id": o.fichier_nom, # On utilise le nom de fichier comme ID
                "titre": o.titre,
                "auteur": o.auteur,
                "fichier": o.fichier_nom,
                "soumisPar": o.soumis_par_email,
                "etat": o.etat.nom,
                "dateSoumission": o.date_soumission
            }
            for o in oeuvres
        ]
    except PermissionError:
        request.response.status = 403
        return {"error": "Accès interdit"}

# 2. Actions de modération
@view_config(route_name='api_traiter', renderer='json', request_method='POST')
def api_traiter(request):
    service = request.registry.service_oeuvre
    user = get_fake_user(request)
    id_oeuvre = request.matchdict['id'] # Récupère {id} dans l'URL
    
    try:
        service.traiter_oeuvre(user, id_oeuvre)
        return {"success": True, "message": "Œuvre en cours de traitement"}
    except Exception as e:
        request.response.status = 400
        return {"error": str(e)}

@view_config(route_name='api_valider', renderer='json', request_method='POST')
def api_valider(request):
    service = request.registry.service_oeuvre
    user = get_fake_user(request)
    id_oeuvre = request.matchdict['id']
    # On récupère la destination depuis le corps JSON de la requête React
    # ex: {"destination": "fond_commun"}
    payload = request.json_body 
    destination = payload.get('destination', 'fond_commun')

    try:
        msg = service.valider_oeuvre(user, id_oeuvre, destination)
        return {"success": True, "message": msg}
    except Exception as e:
        request.response.status = 400
        return {"error": str(e)}
    



# src/app/views/api.py

@view_config(route_name='api_depot', renderer='json', request_method='POST')
def api_depot(request):
    service = request.registry.service_oeuvre
    
    # 1. Récupération des données du formulaire React (FormData)
    # Note: request.POST gère le multipart/form-data
    titre = request.POST.get('titre')
    auteur = request.POST.get('auteur')
    email_membre = request.POST.get('soumisPar')
    
    # Gestion du fichier (Pour l'instant on ne stocke que le nom, plus tard le binaire)
    fichier_input = request.POST.get('fichier')
    filename = "inconnu.pdf"
    if hasattr(fichier_input, 'filename'):
        filename = fichier_input.filename

    if not titre or not email_membre:
        request.response.status = 400
        return {"error": "Titre et email requis"}

    # 2. Création de l'objet Métier (Domaine)
    # On crée un utilisateur temporaire juste pour porter l'email
    auteur_soumission = Utilisateur(nom="Membre", prenom="", email=email_membre, mdp="")
    
    nouvelle_oeuvre = Oeuvre(
        titre=titre, 
        auteur=auteur, 
        fichier_nom=filename, 
        soumis_par=auteur_soumission
    )

    # 3. Appel du Service
    try:
        service.soumettre_oeuvre(nouvelle_oeuvre)
        return {
            "success": True, 
            "message": f"Œuvre '{titre}' bien reçue !",
            "id": nouvelle_oeuvre.titre  # On renvoie l'ID (ici le titre pour simplifier)
        }
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}
    



    # NOUVELLE ROUTE : Upload PDF et conversion
@view_config(route_name='api_depot_pdf', renderer='json', request_method='POST')
def api_depot_pdf(request):
    """
    Endpoint pour soumettre une œuvre depuis un PDF.
    
    Paramètres multipart/form-data:
        - pdf: Fichier PDF
        - titre: Titre de l'œuvre
        - auteur: Auteur de l'œuvre
        - soumisPar: Email du membre
    """
    service = request.registry.service_oeuvre
    
    # 1. Validation des données
    titre = request.POST.get('titre')
    auteur = request.POST.get('auteur', 'Auteur inconnu')
    email_membre = request.POST.get('soumisPar')
    
    if not titre or not email_membre:
        request.response.status = 400
        return {"error": "Titre et email requis"}
    
    # 2. Récupération du fichier PDF
    pdf_file = request.POST.get('pdf')

    # --- NOUVELLE VERSION COMPATIBLE PYTHON 3.12 ---
    if pdf_file is None or not hasattr(pdf_file, 'filename') or pdf_file.filename == '':
        request.response.status = 400
        return {"error": "Fichier PDF requis"}

    
    # 3. Sauvegarde temporaire du PDF
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        # Lecture et écriture du fichier uploadé
        pdf_file.file.seek(0)
        temp_pdf.write(pdf_file.file.read())
        temp_pdf.close()
        
        # 4. Création de l'utilisateur
        membre = Utilisateur(
            nom="Membre",
            prenom="",
            email=email_membre,
            mdp=""
        )
        
        # 5. Conversion et création de l'œuvre
        oeuvre = service.soumettre_oeuvre_depuis_pdf(
            pdf_path=temp_pdf.name,
            titre=titre,
            auteur=auteur,
            soumis_par=membre
        )
        
        return {
            "success": True,
            "message": f"Œuvre '{titre}' convertie et soumise avec succès !",
            "id": oeuvre.fichier_nom,
            "titre": oeuvre.titre,
            "auteur": oeuvre.auteur
        }
        
    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors de la conversion: {str(e)}"}
    
    finally:
        # Nettoyage du fichier temporaire
        if os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)


# NOUVELLE ROUTE : Reconversion d'une œuvre
@view_config(route_name='api_reconvertir', renderer='json', request_method='POST')
def api_reconvertir(request):
    """
    Reconvertit une œuvre avec des paramètres personnalisés.
    
    URL: /api/oeuvres/{id}/reconvertir
    Body JSON: {"dpi": 400, "langue": "fra"}
    """
    service = request.registry.service_oeuvre
    user = get_fake_user(request)
    id_oeuvre = request.matchdict['id']
    
    payload = request.json_body or {}
    dpi = payload.get('dpi', 300)
    langue = payload.get('langue', 'fra')
    
    try:
        nouveau_md = service.reconvertir_oeuvre_pdf(
            biblio=user,
            id_oeuvre=id_oeuvre,
            dpi=dpi,
            langue=langue
        )
        
        return {
            "success": True,
            "message": "Reconversion réussie",
            "fichier": nouveau_md
        }
        
    except PermissionError as e:
        request.response.status = 403
        return {"error": str(e)}
    except ValueError as e:
        request.response.status = 404
        return {"error": str(e)}
    except Exception as e:
        request.response.status = 500
        return {"error": str(e)}


# Vos routes existantes restent inchangées...
@view_config(route_name='api_oeuvres', renderer='json', request_method='GET')
def api_lister_oeuvres(request):
    service = request.registry.service_oeuvre
    user = get_fake_user(request)
    
    try:
        oeuvres = service.lister_oeuvres_a_moderer(user)
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
    except PermissionError:
        request.response.status = 403
        return {"error": "Accès interdit"}
    


#     // ============================================
# // FICHIER 1: Backend - src/app/views/api.py
# // NOUVELLE ROUTE : Conversion PDF sans dépôt
# // ============================================

"""
Ajoutez cette nouvelle route dans src/app/views/api.py
"""

@view_config(route_name='api_convertir_pdf', renderer='json', request_method='POST')
def api_convertir_pdf(request):
    """
    Convertit un PDF en Markdown SANS le déposer.
    Retourne uniquement le contenu Markdown.
    """
    from src.app.infra.pdf_to_md import PDFToMarkdownConverter
    import tempfile

    pdf_file = request.POST.get('pdf')
    if pdf_file is None or not hasattr(pdf_file, 'filename') or pdf_file.filename == '':
        request.response.status = 400
        return {"error": "Fichier PDF requis"}

    # Sauvegarde temporaire du PDF
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_md = None

    try:
        pdf_file.file.seek(0)
        temp_pdf.write(pdf_file.file.read())
        temp_pdf.close()

        converter = PDFToMarkdownConverter(dpi=300, lang="fra")
        temp_md = temp_pdf.name.replace('.pdf', '.md')
        converter.convert(temp_pdf.name, temp_md)

        # Lecture du Markdown
        with open(temp_md, 'r', encoding='utf-8') as f:
            contenu_md = f.read()

        return {
            "success": True,
            "contenu_md": contenu_md
        }

    except Exception as e:
        request.response.status = 500
        return {"error": f"Erreur lors de la conversion: {str(e)}"}

    finally:
        if os.path.exists(temp_pdf.name):
            os.unlink(temp_pdf.name)
        if temp_md and os.path.exists(temp_md):
            os.unlink(temp_md)



# cahier de recette

# matrice de tracabilité

# Avancement

# Temps pour finir le projet

# Liste des scénarios

# Usecases 

# Résulatats des tests unitaires

# Résulatats des tests d'intégration

# Résulatats des tests de validation


# justification technique

#architecture choisie

# languages et frameworks

#Captures

#PV  : nbscénarios OK
#PV  : nbscénarios NOK
