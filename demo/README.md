# 🎨 Interface de Démonstration - OCR Facture API

Interface React moderne pour tester et démontrer l'API OCR Facture.

## 🚀 Installation

```bash
cd demo
npm install
```

## 🏃 Développement

```bash
npm run dev
```

L'interface sera accessible sur `http://localhost:3000`

## 📦 Build pour production

```bash
npm run build
```

Les fichiers seront générés dans le dossier `dist/`

## ⚙️ Configuration

### Option 1 : Via variables d'environnement (optionnel)

Créez un fichier `.env.local` à la racine du dossier `demo/` :

```env
VITE_API_URL=https://ocr-facture-api-production.up.railway.app
VITE_API_SECRET=votre_secret_rapidapi_ici
```

### Option 2 : Via l'interface (recommandé)

L'interface permet de saisir directement votre clé API RapidAPI dans le champ prévu à cet effet. La clé est sauvegardée dans le localStorage de votre navigateur pour les prochaines utilisations.

**Où trouver votre clé API ?**
1. Connectez-vous à [RapidAPI Provider Dashboard](https://rapidapi.com/provider/dashboard)
2. Sélectionnez votre API
3. Allez dans l'onglet "Security" ou "Settings"
4. Copiez votre `X-RapidAPI-Proxy-Secret`

## 🎯 Fonctionnalités

- ✅ Upload drag & drop de factures
- ✅ Prévisualisation de l'image/PDF
- ✅ Affichage des résultats OCR formatés
- ✅ Scores de confiance visuels
- ✅ Validation de conformité FR
- ✅ Export JSON/CSV
- ✅ Interface responsive

## 📝 Intégration avec FastAPI

Pour servir l'interface depuis FastAPI, ajoutez dans `main.py` :

```python
from fastapi.staticfiles import StaticFiles

# Après avoir créé l'app
app.mount("/demo", StaticFiles(directory="demo/dist", html=True), name="demo")
```

Puis déployez l'interface en buildant et en servant depuis `/demo`

