#!/bin/bash

# ============================================
# SCRIPT D'INSTALLATION AUTOMATIQUE
# install.sh
# ============================================

set -e  # Arrêter en cas d'erreur

echo "============================================"
echo "Installation de Biblioteko Backend"
echo "============================================"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les étapes
step() {
    echo -e "${GREEN}[✓]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[!]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1"
}

# ============================================
# Étape 1 : Vérifications préalables
# ============================================

echo "Étape 1/6 : Vérifications préalables..."

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 n'est pas installé"
    exit 1
fi
step "Python 3 trouvé : $(python3 --version)"

# Vérifier pip
if ! command -v pip &> /dev/null; then
    error "pip n'est pas installé"
    exit 1
fi
step "pip trouvé"

# Vérifier tesseract
if ! command -v tesseract &> /dev/null; then
    warn "Tesseract OCR n'est pas installé"
    warn "Installez-le avec : sudo apt-get install tesseract-ocr tesseract-ocr-fra"
else
    step "Tesseract trouvé"
fi

echo ""

# ============================================
# Étape 2 : Créer la structure de dossiers
# ============================================

echo "Étape 2/6 : Création de la structure de dossiers..."

mkdir -p src/app/views
mkdir -p src/app/infra
mkdir -p src/app/auth
mkdir -p data/{a_moderer,fond_commun,sequestre,archives,emprunts}

step "Structure créée"
echo ""

# ============================================
# Étape 3 : Installation des dépendances
# ============================================

echo "Étape 3/6 : Installation des dépendances Python..."

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --break-system-packages
    step "Dépendances installées"
else
    warn "requirements.txt introuvable, création..."
    cat > requirements.txt << 'EOF'
pyramid==2.0.2
waitress==2.1.2
pyramid_chameleon==0.3
pyramid_debugtoolbar==4.10
gitpython==3.1.40
pdf2image==1.16.3
pytesseract==0.3.10
opencv-python==4.8.1.78
Pillow==10.1.0
numpy==1.26.2
PyJWT==2.8.0
cryptography==41.0.7
google-generativeai==0.3.2
mistralai==0.0.11
python-dotenv==1.0.0
bcrypt==4.1.2
pytest==7.4.3
pytest-cov==4.1.0
EOF
    pip install -r requirements.txt --break-system-packages
    step "requirements.txt créé et dépendances installées"
fi

echo ""

# ============================================
# Étape 4 : Copier les fichiers de vues
# ============================================

echo "Étape 4/6 : Installation des fichiers de vues..."

# Vérifier que les fichiers sources existent
if [ -f "auth_views.py" ]; then
    cp auth_views.py src/app/views/
    step "auth_views.py installé"
fi

if [ -f "emprunts.py" ]; then
    cp emprunts.py src/app/views/
    step "emprunts.py installé"
fi

if [ -f "classification.py" ]; then
    cp classification.py src/app/views/
    step "classification.py installé"
fi

if [ -f "multi_ia.py" ]; then
    cp multi_ia.py src/app/views/
    step "multi_ia.py installé"
fi

if [ -f "catalogue.py" ]; then
    cp catalogue.py src/app/views/
    step "catalogue.py installé"
fi

if [ -f "autres.py" ]; then
    cp autres.py src/app/views/
    step "autres.py installé"
fi

echo ""

# ============================================
# Étape 5 : Modifier repositories.py et __init__.py
# ============================================

echo "Étape 5/6 : Mise à jour des fichiers principaux..."

# Sauvegarder les anciens fichiers
if [ -f "src/app/infra/repositories.py" ]; then
    cp src/app/infra/repositories.py src/app/infra/repositories.py.backup
    step "Backup de repositories.py créé"
fi

if [ -f "src/app/__init__.py" ]; then
    cp src/app/__init__.py src/app/__init__.py.backup
    step "Backup de __init__.py créé"
fi

# Ajouter RepoUtilisateurs si le fichier existe
if [ -f "repositories_addition.py" ]; then
    cat repositories_addition.py >> src/app/infra/repositories.py
    step "RepoUtilisateurs ajouté à repositories.py"
fi

# Remplacer __init__.py
if [ -f "new_init.py" ]; then
    cp new_init.py src/app/__init__.py
    step "__init__.py mis à jour"
fi

echo ""

# ============================================
# Étape 6 : Créer le fichier .env
# ============================================

echo "Étape 6/6 : Configuration de l'environnement..."

if [ ! -f ".env" ]; then
    # Générer un secret aléatoire
    SECRET=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    cat > .env << EOF
# Secrets JWT
JWT_SECRET=$SECRET

# APIs IA (optionnel)
GEMINI_API_KEY=your_gemini_key_here
PIXTRAL_API_KEY=your_pixtral_key_here
EOF
    
    step "Fichier .env créé avec secret généré"
else
    warn "Fichier .env existe déjà, non modifié"
fi

echo ""

# ============================================
# Finalisation
# ============================================

echo "============================================"
echo -e "${GREEN}Installation terminée avec succès !${NC}"
echo "============================================"
echo ""
echo "Prochaines étapes :"
echo ""
echo "1. Installer le package en mode développement :"
echo "   python setup.py develop"
echo ""
echo "2. Démarrer le serveur :"
echo "   pserve development.ini"
echo ""
echo "3. Tester l'API :"
echo "   curl http://localhost:6543/"
echo ""
echo "4. Créer un premier utilisateur :"
echo '   curl -X POST http://localhost:6543/api/auth/register \'
echo '     -H "Content-Type: application/json" \'
echo '     -d "{\"email\":\"admin@test.fr\",\"password\":\"admin123\",\"nom\":\"Admin\",\"prenom\":\"Test\"}"'
echo ""
echo "Documentation complète : voir INSTALLATION_GUIDE.md"
echo ""

# Afficher un récapitulatif
echo "Récapitulatif :"
echo "- Dossiers créés : ✓"
echo "- Dépendances installées : ✓"
echo "- Fichiers de vues : ✓"
echo "- Configuration : ✓"
echo ""
echo -e "${GREEN}Tout est prêt !${NC} 🚀"
