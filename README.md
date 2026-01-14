# 📚 Biblioteko Frontend - Next.js

Frontend **Next.js 14** (App Router) pour la bibliothèque numérique **CultureDiffusion**.

## 🎯 Pourquoi Next.js plutôt que Create React App ?

| Avantage Next.js | Bénéfice |
|------------------|----------|
| ✅ **App Router** | Routing basé sur les fichiers (plus simple) |
| ✅ **SSR/SSG** | Meilleures performances et SEO |
| ✅ **API Routes** | Backend intégré si besoin |
| ✅ **Optimisations** | Images, fonts, bundles automatiques |
| ✅ **Production-ready** | Build optimisé par défaut |

---

## 🚀 Installation Rapide

```bash
# Installer les dépendances
npm install

# Démarrer en mode développement
npm run dev
```

L'application sera sur **http://localhost:3000**

---

## 📦 Commandes Disponibles

```bash
# Développement (avec hot reload)
npm run dev

# Build de production
npm run build

# Démarrer en production
npm start

# Linter
npm run lint
```

---

## 🏗️ Structure Next.js (App Router)

```
biblioteko-nextjs/
├── app/                    # Pages (App Router)
│   ├── layout.js          # Layout principal + Navbar
│   ├── page.js            # Page d'accueil (/)
│   ├── login/
│   │   └── page.js        # /login
│   ├── register/
│   │   └── page.js        # /register
│   ├── catalogue/
│   │   └── page.js        # /catalogue
│   ├── depot/
│   │   └── page.js        # /depot
│   ├── emprunts/
│   │   └── page.js        # /emprunts
│   ├── moderation/
│   │   └── page.js        # /moderation
│   └── globals.css        # Styles globaux
├── lib/
│   └── api.js             # ⚡ Client API centralisé
├── public/                # Assets statiques
├── next.config.js         # Configuration Next.js
├── package.json
└── README.md
```

---

## 🔌 Configuration Backend

### Option 1 : Proxy Next.js (Recommandé)

Le fichier `next.config.js` redirige automatiquement `/api/*` vers `http://localhost:6543/api/*`.

```javascript
// next.config.js
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:6543/api/:path*',
    },
  ]
}
```

### Option 2 : Variable d'environnement

Créez `.env.local` :

```env
NEXT_PUBLIC_API_URL=http://localhost:6543/api
```

---

## 🎨 Composants Clés

### Layout Principal (`app/layout.js`)

- Navbar avec authentification
- Footer
- Bootstrap intégré
- Gestion du state auth

### Pages

| Route | Fichier | Description |
|-------|---------|-------------|
| `/` | `app/page.js` | Accueil |
| `/login` | `app/login/page.js` | Connexion |
| `/register` | `app/register/page.js` | Inscription |
| `/catalogue` | `app/catalogue/page.js` | Œuvres publiques |
| `/depot` | `app/depot/page.js` | Déposer PDF |
| `/emprunts` | `app/emprunts/page.js` | Mes emprunts |
| `/moderation` | `app/moderation/page.js` | Modération |

---

## 🧪 Test 

### 1. Démarrer le backend

```bash
cd bibliotheque-backend
source env_bibliotheco/bin/activate
pserve development.ini --reload
```

```
# Structure du projet Bibliothèque Backend

Voici la structure du dossier `src/` de l'application backend :

src/
├── app
│ ├── api/
│ ├── auth/
│ │ ├── decorators.py
│ │ └── jwt_handler.py
│ ├── domain/
│ │ ├── modeles.py
│ │ └── services.py
│ ├── infra/
│ │ ├── crypto.py
│ │ ├── extract_book_meta_data.py
│ │ ├── pdf_to_md.py
│ │ └── repositories.py
│ ├── routes.py
│ ├── templates/
│ └── views/
│ ├── api.py
│ ├── auth.py
│ ├── auth_views.py
│ ├── catalogue.py
│ ├── classification.py
│ ├── demandes_view.py
│ ├── emprunts.py
│ └── multi_ia.py
├── cli/
│ ├── test_pdf_conversion.py
│ └── test_workflow_moderation.py
├── biblioteko_backend.egg-info/
└── init.py


> Les fichiers de cache Python (`__pycache__`) et les fichiers de backup ont été exclus pour plus de clarté.

---

Si tu veux, je peux te **faire une version complète du README.md** qui inclut :
- la structure du **frontend et backend**
- les **commandes pour lancer le projet**
- les **dépendances**
- et des **instructions pour contribuer / setup**  

```

### 2. Démarrer Next.js

```bash
cd biblioteko-nextjs
npm run dev
```

### 3. Tester

1. Ouvrir http://localhost:3000
2. S'inscrire
3. Déposer une œuvre PDF
4. Emprunter depuis le catalogue

---

## 🔐 Authentification JWT

Le token est stocké dans `localStorage` et ajouté automatiquement aux requêtes.

```javascript
// Vérification côté client uniquement
if (typeof window !== 'undefined') {
  const token = localStorage.getItem('token');
}
```

---

## 🎓 Conformité Cahier des Charges

| Exigence | ✅ Status |
|----------|-----------|
| Framework React | ✅ Next.js (React 18) |
| Routing | ✅ App Router (file-based) |
| Bootstrap | ✅ React Bootstrap 5 |
| JWT Auth | ✅ Implémenté |
| PDF Upload | ✅ Conversion backend |
| Modération | ✅ Workflow complet |
| Responsive | ✅ Mobile-first |

---

## 🚧 Différences vs Create React App

| Aspect | CRA | Next.js |
|--------|-----|---------|
| Routing | React Router | File-based |
| Build | Client-side | SSR/SSG |
| Config | Eject requis | next.config.js |
| Performance | Bon | Excellent |
| SEO | Limité | Optimisé |

---

## 🎯 Prochaines Étapes

- [ ] Ajouter metadata SEO (`metadata` export)
- [ ] Utiliser `next/image` pour les images
- [ ] Server Components pour les pages statiques
- [ ] API Routes si besoin d'un backend Node

---

## 📚 Documentation Next.js

- [Next.js 14 Docs](https://nextjs.org/docs)
- [App Router Guide](https://nextjs.org/docs/app)
- [React Bootstrap](https://react-bootstrap.github.io/)

---

## ✨ Projet Prêt !

Votre application Next.js est **100% fonctionnelle** ! 🚀

```bash
npm run dev
```
