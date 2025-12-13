# src/app/interface/web/views.py
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

def get_logged_in_user(request):
    """Récupère l'utilisateur depuis la session (cookie)"""
    email = request.session.get('user_email')
    if not email:
        return None
    
    # On recharge l'utilisateur depuis le repo pour avoir ses droits à jour
    # Note: Dans un vrai projet, on injecterait le repo ici proprement
    # Pour ce MVP, on triche un peu en passant par le service_auth du registre
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
            # SUCCÈS : On met l'email en session
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
            # Auto-login après inscription
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
    # Si pas connecté, on redirige vers login (ou on affiche une page publique)
    if not user:
        return HTTPFound(location='/login')
        
    return {'project_name': 'Culture Diffusion', 'user': user}

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
                service.soumettre_oeuvre(user, titre, auteur, input_file.file)
                message = "✅ Succès ! Votre œuvre est en attente."
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

# Ajoutez les actions 'valider' et 'rejeter' ici (similaires à avant, mais avec get_logged_in_user)
@view_config(route_name='valider')
def valider_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    service = request.registry.service_oeuvre
    try:
        service.valider_oeuvre(user, request.matchdict['id'])
    except Exception: pass
    return HTTPFound(location='/moderation')

@view_config(route_name='rejeter')
def rejeter_action(request):
    user = get_logged_in_user(request)
    if not user: return HTTPFound(location='/login')
    
    service = request.registry.service_oeuvre
    try:
        service.rejeter_oeuvre(user, request.matchdict['id'])
    except Exception: pass
    return HTTPFound(location='/moderation')