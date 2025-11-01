# Guide de publication sur RapidAPI Marketplace

Ce guide vous accompagne étape par étape pour publier votre API OCR Facture sur RapidAPI.

## 📋 Checklist avant publication

- [ ] API déployée et accessible publiquement
- [ ] Tous les endpoints testés et fonctionnels
- [ ] Authentification RapidAPI configurée
- [ ] Documentation complète
- [ ] Exemples de requêtes et réponses préparés
- [ ] Images de démonstration prêtes

## 🚀 Étape 1: Déployer votre API

### Option recommandée: Railway

1. Allez sur [railway.app](https://railway.app) et créez un compte
2. Créez un nouveau projet
3. Connectez votre dépôt GitHub/GitLab
4. Railway détectera automatiquement le `railway.json`
5. Dans les variables d'environnement, configurez:
   ```
   RAPIDAPI_PROXY_SECRET = [générez un secret unique et sécurisé]
   DEBUG_MODE = False
   DEFAULT_LANGUAGE = fra
   ```
6. Une fois déployé, notez l'URL (ex: `https://votre-app.railway.app`)

## 🔐 Étape 2: Créer votre API sur RapidAPI

1. Connectez-vous à [RapidAPI Provider Dashboard](https://rapidapi.com/provider/dashboard)
2. Cliquez sur **"Add New API"** ou **"Create API"**

### Informations de base

- **API Name**: `OCR Facture FR → JSON + Factur-X` ⭐ **RECOMMANDÉ pour SEO**
  - Alternative si le nom est pris : `OCR Facture FR JSON Factur-X`
- **API Base URL**: Votre URL de déploiement (ex: `https://ocr-facture-api-production.up.railway.app`)
- **Category**: 
  - **Primaire** : `Documents & OCR` (moins concurrentielle)
  - **Secondaire** : `Finance & Accounting` (très recherchée)
- **Short Description**: 
  ```
  Extract structured data from invoice images using OCR. Automatically detects amounts, dates, invoice numbers, vendor, and client information.
  ```
- **Long Description**:
  ```
  Professional OCR API for automatic invoice data extraction. Extract text, amounts (HT, TTC, VAT), dates, invoice numbers, vendor and client information from invoice images. Supports multiple languages including French, English, German, Spanish, Italian, and Portuguese.
  ```

### Configuration de l'authentification

1. Dans la section **Authentication**, sélectionnez **"Custom Header"**
2. Header Name: `X-RapidAPI-Proxy-Secret`
3. Générer un secret sécurisé (vous pouvez utiliser un générateur de mots de passe)
4. **Important**: Ajoutez ce même secret dans les variables d'environnement de votre déploiement!

## 📡 Étape 3: Configurer les endpoints

### Endpoint 1: `/ocr/upload`

**Configuration:**
- **Method**: `POST`
- **Path**: `/ocr/upload`
- **Content Type**: `multipart/form-data`

**Parameters:**
1. `file` (File, Required)
   - Type: File
   - Description: Invoice image file (JPEG, PNG)
   
2. `language` (String, Optional)
   - Type: String
   - Default: `fra`
   - Description: Language code for OCR (fra, eng, deu, spa, ita, por)
   - Enum: `fra`, `eng`, `deu`, `spa`, `ita`, `por`

**Example Request:**
```bash
curl --request POST \
  --url https://votre-app.railway.app/ocr/upload \
  --header 'X-RapidAPI-Proxy-Secret: votre-secret' \
  --form 'file=@/path/to/invoice.jpg' \
  --form 'language=fra'
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "text": "FACTURE\nNuméro: FAC-2024-001\nDate: 15/03/2024\n...",
    "language": "fra"
  },
  "extracted_data": {
    "text": "FACTURE\n...",
    "lines": ["FACTURE", "Numéro: FAC-2024-001", ...],
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

### Endpoint 2: `/ocr/base64`

**Configuration:**
- **Method**: `POST`
- **Path**: `/ocr/base64`
- **Content Type**: `application/x-www-form-urlencoded`

**Parameters:**
1. `image_base64` (String, Required)
   - Type: String
   - Description: Base64 encoded image (with or without data:image prefix)
   
2. `language` (String, Optional)
   - Type: String
   - Default: `fra`
   - Description: Language code for OCR

**Example Request:**
```bash
curl --request POST \
  --url https://votre-app.railway.app/ocr/base64 \
  --header 'X-RapidAPI-Proxy-Secret: votre-secret' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data 'image_base64=data:image/jpeg;base64,/9j/4AAQ...' \
  --data 'language=fra'
```

### Endpoint 3: `/languages`

**Configuration:**
- **Method**: `GET`
- **Path**: `/languages`

**Example Response:**
```json
{
  "languages": [
    {"code": "fra", "name": "Français"},
    {"code": "eng", "name": "English"},
    {"code": "deu", "name": "Deutsch"},
    {"code": "spa", "name": "Español"},
    {"code": "ita", "name": "Italiano"},
    {"code": "por", "name": "Português"}
  ]
}
```

## 💰 Étape 4: Définir les plans de tarification

Dans la section **Pricing**, créez plusieurs plans:

### Plan Free
- **Name**: Free
- **Price**: $0/month
- **Rate Limit**: 10 requests/day
- **Description**: Perfect for testing and small projects

### Plan Basic
- **Name**: Basic
- **Price**: $5/month
- **Rate Limit**: 100 requests/day
- **Description**: For small businesses and personal use

### Plan Pro
- **Name**: Pro
- **Price**: $20/month
- **Rate Limit**: 1000 requests/day
- **Description**: For growing businesses and applications

### Plan Enterprise
- **Name**: Enterprise
- **Price**: Custom
- **Rate Limit**: Unlimited
- **Description**: For large-scale applications and enterprises

## 📸 Étape 5: Ajouter des images et exemples

### Images de démonstration

Ajoutez des screenshots de:
- Interface de test sur `/docs`
- Exemple de facture traitée
- Résultat JSON formaté

### Exemples de code

Ajoutez des exemples dans différents langages:
- JavaScript/Node.js
- Python
- cURL
- PHP
- Ruby

## ✅ Étape 6: Soumettre pour review

1. Vérifiez que tout est bien configuré
2. Testez tous les endpoints depuis l'interface RapidAPI
3. Cliquez sur **"Submit for Review"**
4. Attendez la validation par l'équipe RapidAPI (généralement 1-3 jours ouvrables)

## 📊 Étape 7: Marketing et promotion

Une fois votre API approuvée:

1. **Partagez sur les réseaux sociaux**
2. **Créez un article de blog** expliquant votre API
3. **Participez aux communautés** (Reddit, HackerNews, etc.)
4. **Créez des tutoriels** sur YouTube ou Medium
5. **Répondez aux questions** des utilisateurs rapidement

## 🔧 Maintenance

- Surveillez les logs de votre API
- Répondez aux questions des utilisateurs
- Améliorez régulièrement votre API basé sur les retours
- Ajoutez de nouvelles fonctionnalités

## 📈 Optimisation pour plus de ventes

1. **Répondez rapidement** aux utilisateurs (moins de 24h)
2. **Améliorez la documentation** régulièrement
3. **Ajoutez des fonctionnalités** demandées par les utilisateurs
4. **Fixez les bugs** rapidement
5. **Maintenez un uptime élevé** (>99%)

## 💡 Conseils

- Le nom de votre API est important - choisissez quelque chose de descriptif
- La description doit être claire et mettre en avant les bénéfices
- Les exemples de code sont cruciaux - les développeurs veulent voir comment utiliser votre API
- Les images de démonstration aident beaucoup à comprendre l'utilité
- Les plans de tarification doivent être compétitifs

Bon succès avec votre API! 🚀

