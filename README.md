# OCR Facture API

API professionnelle pour l'extraction automatique de données de factures via OCR. Extrait automatiquement le texte, les montants (HT, TTC, TVA), dates, numéros de facture, vendeur, client et autres informations structurées depuis des images de factures.

## 🚀 Fonctionnalités

- ✅ Extraction automatique de texte via OCR (Tesseract)
- ✅ Détection intelligente des montants (Total, HT, TTC, TVA)
- ✅ Extraction des dates de facture
- ✅ Détection améliorée du numéro de facture
- ✅ Identification du vendeur et du client
- ✅ Extraction des lignes de facture (items) avec description, quantité, prix unitaire, total
- ✅ Scores de confiance pour chaque donnée extraite (0-1)
- ✅ Support PDF multi-pages (toutes les pages traitées et fusionnées)
- ✅ **Nouveau v1.2.0** : Détection des tableaux structurés avec colonnes automatiques
- ✅ **Nouveau v1.2.0** : Extraction coordonnées bancaires (IBAN, SWIFT/BIC, RIB)
- ✅ **Nouveau v1.2.0** : Traitement par lot (batch processing) - jusqu'à 10 factures
- ✅ **Nouveau v1.2.0** : Cache des résultats (réponse instantanée pour fichiers déjà traités)
- ✅ **Nouveau v1.2.0** : Intégrations directes Zapier, Make, Salesforce
- ✅ Support multi-langues (Français, Anglais, Allemand, Espagnol, Italien, Portugais)
- ✅ Format de réponse structuré JSON
- ✅ Authentification RapidAPI intégrée

## 📋 Prérequis

- Python 3.11+
- Tesseract OCR installé sur le système
- Bibliothèques de langues Tesseract (optionnel mais recommandé)

## 🔧 Installation locale

### 1. Installer Tesseract OCR

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Pour les langues supplémentaires
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-fra tesseract-ocr-eng
```

**Windows:**
Télécharger depuis: https://github.com/UB-Mannheim/tesseract/wiki

### 2. Créer l'environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du projet :

```env
# Clé secrète RapidAPI (obtenue lors de la création de l'API sur RapidAPI)
RAPIDAPI_PROXY_SECRET=votre_secret_rapidapi

# Mode debug (True pour développement local, False pour production)
DEBUG_MODE=True

# Langue par défaut
DEFAULT_LANGUAGE=fra
```

### 5. Démarrer le serveur

```bash
python main.py
```

Ou avec uvicorn directement :
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur `http://localhost:8000`

## 🌐 API en Production

L'API est déployée et accessible publiquement :
- **URL de Production**: `https://ocr-facture-api-production.up.railway.app`
- **Documentation interactive**: `https://ocr-facture-api-production.up.railway.app/docs`
- **Documentation alternative**: `https://ocr-facture-api-production.up.railway.app/redoc`
- **Disponible sur RapidAPI**: Recherchez "OCRFactureAPI" sur [RapidAPI Marketplace](https://rapidapi.com)

## 📚 Documentation API (Locale)

Une fois le serveur démarré localement, accédez à :
- **Documentation interactive (Swagger)** : `http://localhost:8000/docs`
- **Documentation alternative (ReDoc)** : `http://localhost:8000/redoc`

## 🔌 Endpoints

### `GET /`
Retourne les informations de base de l'API

### `GET /health`
Vérifie l'état de santé de l'API

### `GET /languages`
Retourne la liste des langues supportées

### `POST /ocr/upload`
Upload une image de facture et extrait les données structurées

**Paramètres (multipart/form-data):**
- `file` (required): Fichier image (JPEG, PNG)
- `language` (optional): Code langue (fra, eng, deu, spa, ita, por). Défaut: fra

**Exemple avec curl:**
```bash
curl -X POST "http://localhost:8000/ocr/upload" \
  -F "file=@facture.jpg" \
  -F "language=fra"
```

**Réponse:**
```json
{
  "success": true,
  "data": {
    "text": "Texte extrait complet...",
    "language": "fra"
  },
  "extracted_data": {
    "text": "...",
    "lines": ["...", "..."],
    "total": 1250.50,
    "total_ht": 1042.08,
    "total_ttc": 1250.50,
    "tva": 208.42,
    "date": "15/03/2024",
    "invoice_number": "FAC-2024-001",
    "vendor": "Société Example SARL",
    "client": "Client ABC",
    "currency": "EUR"
  }
}
```

### `POST /ocr/base64`
Traite une image encodée en base64

**Paramètres (form-data):**
- `image_base64` (required): Image encodée en base64
- `language` (optional): Code langue. Défaut: fra

## 🚢 Déploiement pour RapidAPI

### Option 1: Déploiement sur Railway

1. Créez un compte sur [Railway](https://railway.app)
2. Créez un nouveau projet
3. Connectez votre dépôt Git
4. Railway détectera automatiquement le `railway.json`
5. Configurez les variables d'environnement dans Railway:
   - `RAPIDAPI_PROXY_SECRET`: Votre secret RapidAPI
   - `DEBUG_MODE`: `False`
6. Déployez!

### Option 2: Déploiement sur Render

1. Créez un compte sur [Render](https://render.com)
2. Créez un nouveau "Web Service"
3. Connectez votre dépôt Git
4. Render utilisera automatiquement `render.yaml`
5. Configurez les variables d'environnement
6. Déployez!

### Option 3: Déploiement avec Docker

```bash
# Construire l'image
docker build -t ocr-facture-api .

# Lancer le conteneur
docker run -p 8000:8000 \
  -e RAPIDAPI_PROXY_SECRET=votre_secret \
  -e DEBUG_MODE=False \
  ocr-facture-api
```

### Option 4: Déploiement sur Heroku

1. Installez Heroku CLI
2. Créez une application:
```bash
heroku create votre-app-name
```
3. Configurez les variables:
```bash
heroku config:set RAPIDAPI_PROXY_SECRET=votre_secret
heroku config:set DEBUG_MODE=False
```
4. Déployez:
```bash
git push heroku main
```

## 📝 Publier sur RapidAPI Marketplace

### 1. Préparer votre API

- ✅ Déployez votre API sur un service cloud (Railway, Render, Heroku, etc.)
- ✅ Testez tous les endpoints
- ✅ Assurez-vous que l'authentification fonctionne
- ✅ Documentez votre API

### 2. Créer votre API sur RapidAPI

1. Connectez-vous à [RapidAPI Provider Dashboard](https://rapidapi.com/provider/dashboard)
2. Cliquez sur "Add New API"
3. Remplissez les informations:
   - **API Name**: OCR Facture API
   - **API Base URL**: Votre URL de déploiement (ex: https://votre-app.railway.app)
   - **Category**: Business, Finance, ou Developer Tools
   - **Description**: Décrivez votre API
4. Configurez l'authentification:
   - Sélectionnez "Custom Header"
   - Header Name: `X-RapidAPI-Proxy-Secret`
   - Généré un secret unique et ajoutez-le dans vos variables d'environnement

### 3. Configurer les endpoints

Pour chaque endpoint (`/ocr/upload`, `/ocr/base64`), configurez:
- Méthode HTTP (POST)
- Path
- Paramètres (décrivez `file`, `language`, etc.)
- Réponses d'exemple

### 4. Définir les plans de tarification

Sur RapidAPI, vous pouvez créer plusieurs plans:
- **Basic (Gratuit)**: 100 requêtes/mois
- **Pro**: 20 000 requêtes/mois - $15/mois
- **Ultra**: 80 000 requêtes/mois - $59/mois
- **Mega**: 250 000 requêtes/mois - $149/mois

### 5. Ajouter des exemples et documentation

- Ajoutez des exemples de requêtes
- Ajoutez des exemples de réponses
- Ajoutez des images de démonstration
- Rédigez une documentation claire

### 6. Soumettre pour review

Une fois tout configuré, soumettez votre API pour review par l'équipe RapidAPI.

## 🔐 Sécurité

- L'API vérifie le header `X-RapidAPI-Proxy-Secret` en production
- En mode debug (`DEBUG_MODE=True`), l'authentification est désactivée pour les tests locaux
- Ne commitez jamais votre `.env` avec des secrets réels

## 🛠️ Structure du projet

```
OCR-Facture-API/
├── main.py              # Application FastAPI principale
├── config.py            # Configuration et variables d'environnement
├── requirements.txt     # Dépendances Python
├── Dockerfile          # Configuration Docker
├── Procfile            # Configuration Heroku
├── railway.json        # Configuration Railway
├── render.yaml         # Configuration Render
├── .env                # Variables d'environnement (à créer, ne pas commiter)
├── .gitignore         # Fichiers à ignorer par Git
└── README.md          # Ce fichier
```

## 📊 Données extraites

L'API extrait automatiquement:
- **Texte complet**: Tout le texte de la facture
- **Lignes**: Texte organisé par lignes
- **Total**: Montant total détecté
- **Total HT**: Montant hors taxes
- **Total TTC**: Montant toutes taxes comprises
- **TVA**: Montant de la TVA (calculé si HT et TTC disponibles)
- **Date**: Date de la facture
- **Numéro de facture**: Référence/number de la facture
- **Vendeur**: Nom du fournisseur/vendeur
- **Client**: Nom du client
- **Devise**: Devise détectée (EUR, USD, GBP)

## 🌍 Langues supportées

- `fra`: Français
- `eng`: English
- `deu`: Deutsch
- `spa`: Español
- `ita`: Italiano
- `por`: Português

## ⚙️ Variables d'environnement

| Variable | Description | Requis | Défaut |
|----------|-------------|--------|--------|
| `RAPIDAPI_PROXY_SECRET` | Secret pour l'authentification RapidAPI | Oui (production) | - |
| `DEBUG_MODE` | Active le mode debug (désactive l'auth) | Non | `False` |
| `DEFAULT_LANGUAGE` | Langue par défaut pour OCR | Non | `fra` |

## 🐛 Dépannage

### Erreur: "tesseract not found"
Installez Tesseract OCR sur votre système (voir section Installation)

### Erreur: "language not found"
Installez les packs de langues Tesseract pour les langues que vous souhaitez utiliser

### L'API ne répond pas après déploiement
- Vérifiez que le port est correctement configuré (variable `PORT` sur certaines plateformes)
- Vérifiez les logs de déploiement
- Assurez-vous que Tesseract est installé dans le conteneur Docker

## 📄 Licence

Ce projet est fourni tel quel pour être utilisé et vendu sur RapidAPI.

## 🤝 Support

Pour toute question ou problème, créez une issue sur le dépôt Git.
