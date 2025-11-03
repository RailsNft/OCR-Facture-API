# 🎨 Guide d'utilisation de l'interface de démonstration

## 🚀 Démarrage rapide

### 1. Installation des dépendances

```bash
cd demo
npm install
```

### 2. Lancer en mode développement

```bash
npm run dev
```

L'interface sera accessible sur `http://localhost:3000`

### 3. Configuration de la clé API

**Option A : Via l'interface (recommandé)**
1. Ouvrez l'interface dans votre navigateur
2. Entrez votre clé API RapidAPI dans le champ prévu en haut de la page
3. La clé sera automatiquement sauvegardée dans le localStorage

**Option B : Via variables d'environnement**
Créez un fichier `.env.local` :
```env
VITE_API_URL=https://ocr-facture-api-production.up.railway.app
VITE_API_SECRET=votre_cle_rapidapi
```

### 4. Trouver votre clé API RapidAPI

1. Connectez-vous à [RapidAPI Provider Dashboard](https://rapidapi.com/provider/dashboard)
2. Sélectionnez votre API "OCR Facture"
3. Allez dans l'onglet **Security** ou **Settings**
4. Copiez votre `X-RapidAPI-Proxy-Secret`

## 📦 Build pour production

```bash
npm run build
```

Les fichiers seront générés dans `demo/dist/`

## 🌐 Déploiement avec FastAPI

L'interface est automatiquement servie par FastAPI sur `/demo` si le dossier `demo/dist` existe.

1. Build l'interface : `cd demo && npm run build`
2. Lancer FastAPI : `python main.py`
3. Accéder à l'interface : `http://localhost:8000/demo`

## 🎯 Fonctionnalités

### Upload de factures
- **Drag & Drop** : Glissez-déposez votre facture directement
- **Sélection de fichier** : Cliquez sur "Parcourir les fichiers"
- **Formats supportés** : JPEG, PNG, PDF (max 10 MB)

### Options de traitement
- **Langue** : Sélectionnez la langue de la facture (Français, Anglais, Allemand, Espagnol, Italien, Portugais)
- **Validation conformité FR** : Cochez pour activer la vérification de conformité française (SIREN/SIRET, TVA, etc.)

### Résultats
- **Données extraites** : Numéro, date, vendeur, client, montants HT/TTC, TVA
- **Lignes de facture** : Tableau avec description, quantité, prix unitaire, total
- **Scores de confiance** : Barres de progression pour chaque champ extrait
- **Conformité** : Statut de conformité avec les détails des champs manquants
- **Export** : Téléchargez les résultats en JSON ou CSV

## 🔧 Configuration avancée

### Changer l'URL de l'API

Modifiez `VITE_API_URL` dans `.env.local` ou directement dans `src/App.jsx` :

```javascript
const API_BASE_URL = 'https://votre-api.com'
```

### Personnaliser le style

Les fichiers CSS sont modulaires :
- `src/App.css` : Styles principaux
- `src/components/*.css` : Styles des composants individuels

## 🐛 Dépannage

### L'interface ne se charge pas
- Vérifiez que `npm install` a bien installé toutes les dépendances
- Vérifiez la console du navigateur pour les erreurs

### Erreur "Veuillez entrer votre clé API"
- Assurez-vous d'avoir saisi votre clé API RapidAPI dans le champ prévu
- Vérifiez que la clé est correcte dans le dashboard RapidAPI

### L'API retourne une erreur 401
- Vérifiez que votre clé API est valide
- Vérifiez que l'en-tête `X-RapidAPI-Proxy-Secret` est bien envoyé (visible dans l'onglet Network du navigateur)

### Le build échoue
- Vérifiez que Node.js >= 16 est installé
- Supprimez `node_modules` et `package-lock.json`, puis relancez `npm install`

## 📝 Notes

- La clé API est stockée dans le **localStorage** du navigateur (local uniquement, jamais envoyée ailleurs)
- Pour tester avec une autre clé, videz le localStorage ou utilisez la navigation privée
- L'interface fonctionne uniquement avec l'API OCR Facture (pas avec d'autres APIs)



