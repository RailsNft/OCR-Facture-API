# Guide d'utilisation pour les utilisateurs - OCR Facture API

## 📍 Comment trouver l'API

### Méthode 1: Recherche sur RapidAPI

1. Allez sur [rapidapi.com](https://rapidapi.com)
2. Dans la barre de recherche, tapez : **"OCRFactureAPI"** ou **"OCR Facture"**
3. Cliquez sur votre API dans les résultats

### Méthode 2: Lien direct

Une fois votre API visible, vous pouvez partager le lien direct vers votre page API sur RapidAPI.

## 🔐 Comment s'abonner

### Étape 1: Créer un compte RapidAPI

1. Si l'utilisateur n'a pas de compte, il doit créer un compte gratuit sur RapidAPI
2. Confirmer l'email

### Étape 2: Choisir un plan

Sur la page de votre API, l'utilisateur verra les plans disponibles :

- **BASIC (Gratuit)** : $0/mois - 100 requêtes/mois
- **PRO** : $15/mois - 20 000 requêtes/mois  
- **ULTRA** : $59/mois - 80 000 requêtes/mois
- **MEGA** : $149/mois - 250 000 requêtes/mois

### Étape 3: S'abonner

1. Cliquer sur le plan souhaité
2. Confirmer l'abonnement
3. Obtenir la clé API automatiquement

## 🔑 Comment obtenir la clé API

Après l'abonnement, l'utilisateur recevra automatiquement :

1. **X-RapidAPI-Key** : Clé unique pour accéder à l'API
2. Cette clé sera visible dans le dashboard RapidAPI de l'utilisateur

## 💻 Comment utiliser l'API

### Méthode 1: Depuis l'interface RapidAPI (le plus simple)

1. Aller sur la page de votre API
2. Cliquer sur l'endpoint souhaité (ex: `/ocr/upload`)
3. Cliquer sur "Test Endpoint"
4. Uploadez l'image de facture
5. Sélectionner la langue
6. Cliquer sur "Run"
7. Voir les résultats directement

### Méthode 2: Avec curl (ligne de commande)

```bash
curl -X POST "https://rapidapi.com/[votre-api]/api/ocrfactureapi/ocr/upload" \
  -H "X-RapidAPI-Key: [clé-api-utilisateur]" \
  -H "X-RapidAPI-Host: [votre-api-host]" \
  -F "file=@facture.jpg" \
  -F "language=fra"
```

### Méthode 3: Avec Python

```python
import requests

url = "https://rapidapi.com/[votre-api]/api/ocrfactureapi/ocr/upload"

headers = {
    "X-RapidAPI-Key": "[clé-api-utilisateur]",
    "X-RapidAPI-Host": "[votre-api-host]"
}

files = {
    "file": ("facture.jpg", open("facture.jpg", "rb"), "image/jpeg")
}

data = {
    "language": "fra"
}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

print(f"Total: {result['extracted_data']['total']}")
print(f"Date: {result['extracted_data']['date']}")
print(f"Numéro: {result['extracted_data']['invoice_number']}")
```

### Méthode 4: Avec JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

const form = new FormData();
form.append('file', fs.createReadStream('facture.jpg'));
form.append('language', 'fra');

axios.post('https://rapidapi.com/[votre-api]/api/ocrfactureapi/ocr/upload', form, {
  headers: {
    'X-RapidAPI-Key': '[clé-api-utilisateur]',
    'X-RapidAPI-Host': '[votre-api-host]',
    ...form.getHeaders()
  }
})
.then(response => {
  console.log('Total:', response.data.extracted_data.total);
  console.log('Date:', response.data.extracted_data.date);
})
.catch(error => {
  console.error('Erreur:', error);
});
```

## 📊 Format de réponse

L'API retourne un JSON avec cette structure :

```json
{
  "success": true,
  "data": {
    "text": "Texte complet extrait...",
    "language": "fra"
  },
  "extracted_data": {
    "text": "...",
    "lines": ["ligne1", "ligne2", ...],
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

## 🌍 Langues supportées

- `fra` - Français
- `eng` - English
- `deu` - Deutsch
- `spa` - Español
- `ita` - Italiano
- `por` - Português

## 📝 Formats d'image supportés

- JPEG (.jpg, .jpeg)
- PNG (.png)
- PDF (.pdf)

## 💡 Cas d'usage

### 1. Automatisation comptable
- Extraire automatiquement les données de factures reçues
- Intégrer dans un système de comptabilité
- Réduire la saisie manuelle

### 2. Gestion de documents
- Numériser des factures papier
- Créer une base de données de factures
- Rechercher dans les factures par montant, date, vendeur

### 3. Validation de factures
- Vérifier automatiquement les montants
- Détecter les erreurs
- Valider les informations

### 4. Reporting financier
- Analyser les dépenses
- Générer des rapports automatiques
- Suivre les factures par période

## 📚 Documentation complète

Les utilisateurs peuvent accéder à :
- **Documentation interactive** : Sur la page RapidAPI de votre API
- **Exemples de code** : Disponibles dans différents langages sur RapidAPI
- **Support** : Via la section "Support" sur RapidAPI

## 🆘 Support

Si les utilisateurs ont des questions :
1. Ils peuvent utiliser la section "Support" sur RapidAPI
2. Vous pouvez répondre directement depuis votre dashboard RapidAPI
3. Consulter la documentation sur GitHub : https://github.com/RailsNft/OCR-Facture-API

## 💰 Tarification

Les utilisateurs paient selon leur plan :
- Les requêtes sont comptabilisées automatiquement
- Les limites sont appliquées automatiquement
- Ils peuvent upgrader leur plan à tout moment

## ✅ Avantages pour les utilisateurs

- ✅ **Pas besoin d'installer Tesseract** : Tout est géré côté serveur
- ✅ **Pas besoin de serveur** : Utilisation directe via API
- ✅ **Mises à jour automatiques** : Toujours la dernière version
- ✅ **Support multi-langues** : Fonctionne avec plusieurs langues
- ✅ **Résultats structurés** : Données prêtes à utiliser en JSON
- ✅ **Facile à intégrer** : API REST standard

