# src/app/interface/web/views.py
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response # <--- Indispensable pour le téléchargement

def get_logged_in_user(request):
    """Récupère l'utilisateur depuis la session (cookie)"""
    email = request.session.get('user_email')
    if not email:
        return None
    # On passe par le service d'auth pour récupérer l'user complet
    service = request.registry.service_auth
    return service.repo.trouver_par_email(email)

@view_config(route_name='login', renderer='interface.web:templates/login.pt')
def login_view(request):
    message = ""
    if request.method == 'POST':
        email = request.params.get('email')
        mdp = request.params.get('password')
        service = request.registry.service_auth
        
        user = service.identifier_utilisateur(email, mdp)
        if user:
            request.session['user_email'] = user.email
            return HTTPFound(location='/')
        else:
            message = "Identifiants incorrects."
    return {'message': message}

@view_config(route_name='signup', renderer='interface.web:templates/signup.pt')
def signup_view(request):
    message = ""
    if request.method == 'POST':
        nom = request.params.get('nom')
        email = request.params.get('email')
        mdp = request.params.get('password')
        service = request.registry.service_auth
        
        try:
            service.inscrire_membre(nom, email, mdp)
            request.session['user_email'] = email
            return HTTPFound(location='/')
        except ValueError as e:
            message = str(e)
    return {'message': message}

@view_config(route_name='logout')
def logout_view(request):
    request.session.invalidate()
    return HTTPFound(location='/login')

@view_config(route_name='accueil', renderer='interface.web:templates/accueil.pt')
def accueil_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    svc_oeuvre = request.registry.service_oeuvre
    svc_emprunt = request.registry.service_emprunt
    
    # 1. Public Domain Works (Free Access)
    catalog_public = svc_oeuvre.lister_publiques()
    
    # 2. Copyrighted Works (Available for Loan)
    catalog_loan = svc_oeuvre.lister_sequestre()
    
    # 3. My Active Loans
    my_loans = svc_emprunt.lister_mes_emprunts(user)
    
    return {
        'project_name': 'Culture Diffusion', 
        'user': user,
        'catalog_public': catalog_public,
        'catalog_loan': catalog_loan,
        'my_loans': my_loans
    }

@view_config(route_name='depot', renderer='interface.web:templates/depot.pt')
def depot_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    service = request.registry.service_oeuvre
    message = ""

    if request.method == 'POST':
        titre = request.params.get('titre')
        auteur = request.params.get('auteur')
        input_file = request.POST.get('fichier')
        
        if hasattr(input_file, 'file'):
            try:
                # Appel avec le fichier pour l'OCR
                service.soumettre_oeuvre(user, titre, auteur, input_file.file)
                message = "✅ Succès ! Votre œuvre est en attente (Analyse IA en cours...)."
            except Exception as e:
                message = f"❌ Erreur : {e}"
        else:
            message = "❌ Fichier manquant."

    return {'message': message, 'user': user}

@view_config(route_name='moderation', renderer='interface.web:templates/moderation.pt')
def moderation_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    service = request.registry.service_oeuvre
    oeuvres = []
    error = ""

    try:
        oeuvres = service.lister_a_moderer(user)
    except PermissionError:
        error = "⛔ Accès Interdit : Espace réservé aux bibliothécaires."

    return {'oeuvres': oeuvres, 'error': error, 'user': user}

# --- C'EST ICI QUE CELA MANQUAIT PROBABLEMENT ---

@view_config(route_name='download_md')
def download_md_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    id_oeuvre = request.matchdict['id']
    service = request.registry.service_oeuvre
    
    # On cherche l'œuvre partout (a_moderer, fond_commun, sequestre)
    locations = ["a_moderer", "fond_commun", "sequestre"]
    oeuvre = None
    
    for loc in locations:
        try:
            oeuvre = service.repo.charger(id_oeuvre, loc)
            break
        except FileNotFoundError:
            continue
            
    if not oeuvre:
        return Response("Œuvre introuvable sur le disque.", status=404)
        
    # On renvoie le contenu Markdown en téléchargement
    response = Response(body=oeuvre.contenu_markdown, content_type='text/markdown')
    response.content_disposition = f'attachment; filename="{oeuvre.titre}_OCR.md"'
    return response

@view_config(route_name='valider_form')
def valider_form_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    if request.method == 'POST':
        service = request.registry.service_oeuvre
        id_oeuvre = request.params.get('id')
        type_droit = request.params.get('type_droit') # 'public' ou 'prive'
        
        is_public = (type_droit == 'public')
        
        try:
            service.valider_oeuvre(user, id_oeuvre, est_domaine_public=is_public)
        except Exception as e:
            print(f"Validation Error: {e}")

    return HTTPFound(location='/moderation')

@view_config(route_name='valider')
def valider_action(request):
    # Route legacy (simple clic sans choix de droits)
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    service = request.registry.service_oeuvre
    try:
        service.valider_oeuvre(user, request.matchdict['id'], est_domaine_public=False)
    except Exception: pass
    return HTTPFound(location='/moderation')

@view_config(route_name='rejeter')
def rejeter_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    service = request.registry.service_oeuvre
    try:
        service.rejeter_oeuvre(user, request.matchdict['id'])
    except Exception: pass
    return HTTPFound(location='/moderation')

@view_config(route_name='emprunter')
def emprunter_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    svc_emprunt = request.registry.service_emprunt
    id_oeuvre = request.matchdict['id']
    
    try:
        svc_emprunt.emprunter(user, id_oeuvre)
    except Exception as e:
        print(f"Loan Error: {e}")
        
    return HTTPFound(location='/')

@view_config(route_name='valider_form')
def valider_form_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    if request.method == 'POST':
        service = request.registry.service_oeuvre
        id_oeuvre = request.params.get('id')
        type_droit = request.params.get('type_droit')
        
        # --- NEW: Get Enriched Metadata ---
        titre_modifie = request.params.get('titre')
        auteur_modifie = request.params.get('auteur')
        
        is_public = (type_droit == 'public')
        
        try:
            # Call updated service method
            service.valider_oeuvre(
                user, id_oeuvre, 
                est_domaine_public=is_public,
                nouveau_titre=titre_modifie,
                nouveau_auteur=auteur_modifie
            )
        except Exception as e:
            print(f"Validation Error: {e}")

    return HTTPFound(location='/moderation')