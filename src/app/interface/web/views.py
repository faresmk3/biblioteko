from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response

# Fonction utilitaire pour récupérer l'utilisateur connecté
def get_logged_in_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    repo = request.registry.service_auth.repo
    return repo.trouver_par_id(user_id)

# --- VUES ---

@view_config(route_name='accueil', renderer='interface.web:templates/accueil.pt')
def accueil_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    svc_oeuvre = request.registry.service_oeuvre
    svc_emprunt = request.registry.service_emprunt
    
    return {
        'project_name': 'Culture Diffusion', 
        'user': user,
        'catalog_public': svc_oeuvre.lister_publiques(),
        'catalog_loan': svc_oeuvre.lister_sequestre(),
        'my_loans': svc_emprunt.lister_mes_emprunts(user)
    }

@view_config(route_name='login', renderer='interface.web:templates/login.pt')
def login_view(request):
    message = ""
    if request.method == 'POST':
        email = request.params.get('email')
        password = request.params.get('password')
        auth_service = request.registry.service_auth
        
        user = auth_service.identifier_utilisateur(email, password)
        if user:
            request.session['user_id'] = user.id
            return HTTPFound(location='/')
        else:
            message = "Identifiants incorrects."
    return {'message': message}

@view_config(route_name='logout')
def logout_view(request):
    request.session.invalidate()
    return HTTPFound(location='/login')

@view_config(route_name='signup', renderer='interface.web:templates/signup.pt')
def signup_view(request):
    message = ""
    if request.method == 'POST':
        nom = request.params.get('nom')
        email = request.params.get('email')
        password = request.params.get('password')
        auth_service = request.registry.service_auth
        
        try:
            auth_service.inscrire_membre(nom, email, password)
            message = "Compte créé ! Connectez-vous."
        except Exception as e:
            message = f"Erreur : {e}"
    return {'message': message}

@view_config(route_name='depot', renderer='interface.web:templates/depot.pt')
def depot_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    service = request.registry.service_oeuvre
    message = ""

    if request.method == 'POST':
        titre = request.params.get('titre')
        auteur = request.params.get('auteur')
        # Récupération des catégories (liste)
        categories = request.params.getall('categories') 
        input_file = request.POST.get('fichier')
        
        if hasattr(input_file, 'file'):
            try:
                # CORRECTION ICI : Arguments nommés pour éviter les inversions
                service.soumettre_oeuvre(
                    membre=user, 
                    titre_form=titre, 
                    auteur_form=auteur, 
                    categories=categories,   # C'est bien la liste des chaînes
                    fichier_stream=input_file.file # C'est bien le fichier
                )
                message = "✅ Succès ! Œuvre soumise et analysée."
            except Exception as e:
                # On affiche l'erreur détaillée pour le debug
                import traceback
                traceback.print_exc()
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
    error = None
    
    try:
        oeuvres = service.lister_a_moderer(user)
    except PermissionError:
        error = "⛔ Accès refusé. Réservé aux bibliothécaires."
    
    return {'user': user, 'oeuvres': oeuvres, 'error': error}

@view_config(route_name='valider_form')
def valider_form_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    if request.method == 'POST':
        service = request.registry.service_oeuvre
        id_oeuvre = request.params.get('id')
        type_droit = request.params.get('type_droit')
        
        # Récupération des données enrichies
        titre = request.params.get('titre')
        auteur = request.params.get('auteur')
        categories = request.params.getall('categories')
        
        is_public = (type_droit == 'public')
        
        try:
            service.valider_oeuvre(
                bibliothecaire=user, 
                id_oeuvre=id_oeuvre, 
                est_domaine_public=is_public,
                nouveau_titre=titre,
                nouveau_auteur=auteur,
                nouvelles_categories=categories
            )
        except Exception as e:
            print(f"Erreur validation: {e}")

    return HTTPFound(location='/moderation')

@view_config(route_name='rejeter')
def rejeter_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    id_oeuvre = request.matchdict['id']
    service = request.registry.service_oeuvre
    
    try:
        service.rejeter_oeuvre(user, id_oeuvre)
    except Exception as e:
        print(f"Erreur rejet: {e}")
        
    return HTTPFound(location='/moderation')

@view_config(route_name='download_md')
def download_md(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login') # Protection minimale
    
    id_oeuvre = request.matchdict['id']
    repo = request.registry.service_oeuvre.repo
    
    # On cherche l'œuvre (peu importe le dossier pour le téléchargement)
    try:
        # On essaie d'abord dans a_moderer
        oeuvre = repo.charger(id_oeuvre, "a_moderer")
    except:
        try:
            oeuvre = repo.charger(id_oeuvre, "fond_commun")
        except:
            return Response("Fichier non trouvé", status=404)
            
    content = oeuvre.contenu_markdown or "Pas de contenu extrait."
    
    response = Response(body=content, content_type='text/markdown')
    response.content_disposition = f'attachment; filename="{oeuvre.titre}.md"'
    return response

@view_config(route_name='emprunter')
def emprunter_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    svc_emprunt = request.registry.service_emprunt
    id_oeuvre = request.matchdict['id']
    
    try:
        svc_emprunt.emprunter(user, id_oeuvre)
    except Exception as e:
        print(f"Erreur Emprunt: {e}")
        
    return HTTPFound(location='/')

@view_config(route_name='lire_emprunt')
def lire_emprunt_view(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound('/login')
    
    id_oeuvre = request.matchdict['id']
    svc_emprunt = request.registry.service_emprunt
    
    my_loans = svc_emprunt.lister_mes_emprunts(user)
    loan_info = next((l for l in my_loans if l['work_id'] == id_oeuvre), None)
    
    if not loan_info:
        return Response("Emprunt non trouvé ou expiré.", status=404)
        
    try:
        pdf_bytes = svc_emprunt.lire_fichier_chiffre(user, loan_info['encrypted_file'])
        response = Response(body=pdf_bytes, content_type='application/pdf')
        response.content_disposition = f'inline; filename="{loan_info["work_title"]}.pdf"'
        return response
    except Exception as e:
        return Response(f"Erreur déchiffrement: {e}", status=500)

@view_config(route_name='admin_cron_droits')
def admin_cron_droits(request):
    user = get_logged_in_user(request)
    if not user or not user.a_la_permission("peut_moderer_oeuvre"):
        return HTTPFound('/login')
        
    svc_oeuvre = request.registry.service_oeuvre
    svc_oeuvre.verifier_expiration_droits()
    
    return Response("Vérification des droits terminée. Voir logs serveur.")