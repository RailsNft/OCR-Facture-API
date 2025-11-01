# 📚 Documentation complète - OCR Facture API

**Version :** 2.0.0  
**Dernière mise à jour :** [Date actuelle]

---

## 📋 Table des matières

1. [Introduction](#introduction)
2. [Démarrage rapide](#démarrage-rapide)
3. [Authentification](#authentification)
4. [Endpoints OCR](#endpoints-ocr)
5. [Endpoints Compliance](#endpoints-compliance)
6. [Endpoints Factur-X](#endpoints-factur-x)
7. [Format des réponses](#format-des-réponses)
8. [Gestion des erreurs](#gestion-des-erreurs)
9. [Exemples d'intégration](#exemples-dintégration)
10. [Cas d'usage](#cas-dusage)
11. [FAQ](#faq)
12. [Support](#support)

---

## 🎯 Introduction

### Qu'est-ce que l'API OCR Facture France ?

L'API OCR Facture France est un service professionnel qui permet d'extraire automatiquement les données structurées des factures françaises et européennes via OCR (Reconnaissance Optique de Caractères). Elle inclut la validation de conformité française (TVA, SIREN/SIRET, mentions légales) et la génération de fichiers Factur-X conformes au standard EN16931.

### Fonctionnalités principales

- ✅ **Extraction OCR automatique** : Texte, montants, dates, numéros, vendeur, client
- ✅ **Validation conformité FR** : Vérification mentions légales, TVA, SIREN/SIRET
- ✅ **Génération Factur-X** : XML conforme EN16931 pour facturation électronique
- ✅ **Support multi-pages** : Traitement automatique des PDFs multi-pages
- ✅ **Scores de confiance** : Score 0-1 pour chaque donnée extraite
- ✅ **Traitement par lot** : Jusqu'à 10 factures en une requête
- ✅ **Cache intelligent** : Réponses instantanées pour fichiers déjà traités

### Cas d'usage

- **Cabinets comptables** : Automatisation de la saisie de factures
- **ERP / Logiciels comptables** : Import automatique de factures fournisseurs
- **SaaS facturation** : Enrichissement et validation de factures
- **Marketplaces** : Traitement automatique des factures fournisseurs
- **Entreprises** : Conversion factures papier → données structurées

---

## 🚀 Démarrage rapide

### Étape 1 : S'abonner à l'API

1. Allez sur [RapidAPI](https://rapidapi.com)
2. Recherchez **"OCR Facture France"**
3. Cliquez sur **"Subscribe"**
4. Choisissez le plan **Free** (10 requêtes/jour) pour tester
5. Obtenez votre clé API dans le dashboard

### Étape 2 : Obtenir votre clé API

1. Connectez-vous à votre compte RapidAPI
2. Allez dans **"My Apps"** → Sélectionnez votre application
3. Copiez votre **X-RapidAPI-Key**
4. Notez également le **X-RapidAPI-Proxy-Secret** (configuré par le fournisseur)

### Étape 3 : Votre première requête

#### Avec cURL

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -F "file=@facture.pdf" \
  -F "language=fra" \
  -F "check_compliance=true"
```

#### Avec Python

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/ocr/upload"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret"
}

files = {
    "file": open("facture.pdf", "rb")
}
data = {
    "language": "fra",
    "check_compliance": True
}

response = requests.post(url, headers=headers, files=files, data=data)
result = response.json()

print(f"Numéro : {result['extracted_data']['invoice_number']}")
print(f"Total TTC : {result['extracted_data']['total_ttc']}€")
print(f"Conforme : {result['compliance']['compliance_check']['compliant']}")
```

#### Avec JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('facture.pdf'));
form.append('language', 'fra');
form.append('check_compliance', 'true');

axios.post('https://ocr-facture-api-production.up.railway.app/ocr/upload', form, {
  headers: {
    ...form.getHeaders(),
    'X-RapidAPI-Proxy-Secret': 'votre-secret'
  }
})
.then(response => {
  console.log('Numéro :', response.data.extracted_data.invoice_number);
  console.log('Total TTC :', response.data.extracted_data.total_ttc + '€');
})
.catch(error => console.error(error));
```

---

## 🔐 Authentification

### Méthode d'authentification

L'API utilise l'authentification via header personnalisé :

```
X-RapidAPI-Proxy-Secret: votre-secret-rapidapi
```

Ce secret est configuré dans RapidAPI et vous est fourni lors de l'abonnement.

### Endpoints publics (sans authentification)

Les endpoints suivants ne nécessitent pas d'authentification :

- `GET /` - Informations sur l'API
- `GET /health` - État de santé de l'API
- `GET /docs` - Documentation Swagger UI
- `GET /languages` - Liste des langues supportées

### Endpoints protégés (authentification requise)

Tous les autres endpoints nécessitent le header `X-RapidAPI-Proxy-Secret`.

---

## 📄 Endpoints OCR

### 1. Upload de fichier

**Endpoint :** `POST /ocr/upload`

**Description :** Upload une image ou PDF de facture et extrait automatiquement les données structurées.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `file` | File | ✅ Oui | Fichier image (JPEG, PNG) ou PDF |
| `language` | String | ❌ Non | Code langue (fra, eng, deu, spa, ita, por). Défaut: `fra` |
| `check_compliance` | Boolean | ❌ Non | Activer validation conformité FR. Défaut: `false` |

**Formats supportés :**
- Images : JPEG, PNG
- Documents : PDF (multi-pages supporté)

**Taille maximale :** 10 Mo par défaut

**Exemple de requête :**

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -F "file=@facture.pdf" \
  -F "language=fra" \
  -F "check_compliance=true"
```

**Exemple de réponse :**

```json
{
  "success": true,
  "cached": false,
  "data": {
    "text": "FACTURE\nNuméro: FAC-2024-001\n...",
    "language": "fra",
    "pages_processed": 1
  },
  "extracted_data": {
    "invoice_number": "FAC-2024-001",
    "date": "15/03/2024",
    "total_ht": 1042.08,
    "total_ttc": 1250.50,
    "tva": 208.42,
    "vendor": "Société Example SARL",
    "client": "Client ABC",
    "items": [
      {
        "description": "Consultation technique",
        "quantity": 1.0,
        "unit_price": 500.00,
        "total": 500.00
      }
    ],
    "banking_info": {
      "iban": "FR7612345678901234567890123",
      "swift": "ABCDEFGH"
    },
    "currency": "EUR"
  },
  "confidence_scores": {
    "total": 0.95,
    "invoice_number": 0.88,
    "items": 0.90
  },
  "compliance": {
    "compliance_check": {
      "compliant": true,
      "score": 95.0,
      "missing_fields": [],
      "warnings": []
    },
    "vat_validation": {
      "valid": true,
      "vat_rate": 20.0
    },
    "siren_siret": {
      "siren": "479453193",
      "siret": "47945319300043"
    }
  }
}
```

---

### 2. Traitement base64

**Endpoint :** `POST /ocr/base64`

**Description :** Traite une image encodée en base64.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `image_base64` | String | ✅ Oui | Image encodée en base64 (avec ou sans préfixe `data:image`) |
| `language` | String | ❌ Non | Code langue. Défaut: `fra` |

**Exemple de requête :**

```python
import base64
import requests

# Encoder l'image en base64
with open("facture.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

url = "https://ocr-facture-api-production.up.railway.app/ocr/base64"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret"
}
data = {
    "image_base64": f"data:image/jpeg;base64,{image_base64}",
    "language": "fra"
}

response = requests.post(url, headers=headers, data=data)
print(response.json())
```

---

### 3. Traitement par lot

**Endpoint :** `POST /ocr/batch`

**Description :** Traite plusieurs factures en une seule requête (jusqu'à 10 fichiers).

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `files` | Array[String] | ✅ Oui | Liste d'images encodées en base64 |
| `language` | String | ❌ Non | Code langue. Défaut: `fra` |

**Limite :** Maximum 10 fichiers par requête

**Exemple de requête :**

```python
import base64
import requests

def encode_image(file_path):
    with open(file_path, "rb") as f:
        return f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"

url = "https://ocr-facture-api-production.up.railway.app/ocr/batch"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "files": [
        encode_image("facture1.jpg"),
        encode_image("facture2.pdf"),
        encode_image("facture3.jpg")
    ],
    "language": "fra"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

print(f"Traitées : {result['total_processed']}")
print(f"Depuis cache : {result['total_cached']}")
for i, res in enumerate(result['results']):
    print(f"Facture {i+1} : {res['extracted_data']['invoice_number']}")
```

---

## 🇫🇷 Endpoints Compliance

### 1. Vérification complète de conformité

**Endpoint :** `POST /compliance/check`

**Description :** Vérifie la conformité complète d'une facture française (mentions légales, TVA, SIREN/SIRET, TVA intracom).

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `invoice_data` | Object | ✅ Oui | Données extraites de la facture (format JSON) |

**Exemple de requête :**

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/compliance/check"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "invoice_data": {
        "text": "FACTURE\n...",
        "invoice_number": "FAC-2024-001",
        "date": "15/03/2024",
        "total_ht": 1042.08,
        "total_ttc": 1250.50,
        "tva": 208.42,
        "vendor": "Société Example SARL",
        "client": "Client ABC"
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

compliance = result['compliance']
print(f"Conforme : {compliance['compliance_check']['compliant']}")
print(f"Score : {compliance['compliance_check']['score']}/100")
print(f"SIRET détecté : {compliance['siren_siret'].get('siret')}")
```

**Exemple de réponse :**

```json
{
  "success": true,
  "compliance": {
    "compliance_check": {
      "compliant": true,
      "score": 95.0,
      "missing_fields": [],
      "warnings": ["Adresse complète du vendeur non détectée"]
    },
    "vat_validation": {
      "valid": true,
      "vat_rate": 20.0,
      "errors": [],
      "warnings": []
    },
    "siren_siret": {
      "siren": "479453193",
      "siret": "47945319300043"
    },
    "vat_intracom": {
      "detected": "FR47945319300",
      "validated": {
        "success": true,
        "valid": true,
        "name": "SOCIETE EXAMPLE SARL"
      }
    },
    "enrichment": {
      "siren_siret": {
        "success": false,
        "error": "Clé API Sirene non configurée"
      },
      "vies": {
        "success": true,
        "valid": true
      }
    }
  }
}
```

---

### 2. Validation TVA uniquement

**Endpoint :** `POST /compliance/validate-vat`

**Description :** Valide uniquement les taux et calculs de TVA pour une facture française.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `invoice_data` | Object | ✅ Oui | Données avec montants HT, TTC, TVA |

**Exemple de requête :**

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/compliance/validate-vat"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "invoice_data": {
        "total_ht": 1042.08,
        "total_ttc": 1250.50,
        "tva": 208.42
    }
}

response = requests.post(url, headers=headers, json=data)
validation = response.json()['validation']

if validation['valid']:
    print(f"✅ TVA valide : {validation['vat_rate']}%")
else:
    print("❌ Erreurs TVA :")
    for error in validation['errors']:
        print(f"  - {error['error']}")
```

**Taux TVA valides en France :**
- 20% (taux normal)
- 10% (taux réduit)
- 5.5% (taux réduit)
- 2.1% (taux réduit)
- 0% (taux zéro)

---

### 3. Enrichissement SIRET

**Endpoint :** `POST /compliance/enrich-siret`

**Description :** Enrichit les données avec l'API Sirene (Insee) à partir d'un numéro SIRET.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `siret` | String | ✅ Oui | Numéro SIRET (14 chiffres) |

**Note :** Nécessite la configuration de `SIRENE_API_KEY` et `SIRENE_API_SECRET` côté serveur.

**Exemple de requête :**

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/compliance/enrich-siret"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "siret": "47945319300043"
}

response = requests.post(url, headers=headers, json=data)
enrichment = response.json()['enrichment']

if enrichment['success']:
    print(f"Raison sociale : {enrichment.get('company_name')}")
    print(f"Adresse : {enrichment.get('address')}")
else:
    print(f"Erreur : {enrichment.get('error')}")
```

---

### 4. Validation VIES

**Endpoint :** `POST /compliance/validate-vies`

**Description :** Valide un numéro TVA intracommunautaire via l'API VIES européenne.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `vat_number` | String | ✅ Oui | Numéro TVA intracom (ex: FR47945319300) |

**Exemple de requête :**

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/compliance/validate-vies"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "vat_number": "FR47945319300"
}

response = requests.post(url, headers=headers, json=data)
validation = response.json()['validation']

if validation['success'] and validation['valid']:
    print(f"✅ TVA valide")
    print(f"Nom entreprise : {validation.get('name')}")
    print(f"Adresse : {validation.get('address')}")
else:
    print(f"❌ TVA invalide : {validation.get('error')}")
```

---

## 📄 Endpoints Factur-X

### 1. Génération XML Factur-X

**Endpoint :** `POST /facturx/generate`

**Description :** Génère un XML Factur-X conforme au standard EN16931 à partir des données de facture.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `invoice_data` | Object | ✅ Oui | Données de facture (date, numéro, montants, vendeur, client, items) |

**Exemple de requête :**

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/facturx/generate"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "invoice_data": {
        "invoice_number": "FAC-2024-001",
        "date": "15/03/2024",
        "total_ht": 1042.08,
        "total_ttc": 1250.50,
        "tva": 208.42,
        "vendor": "Société Example SARL",
        "client": "Client ABC",
        "currency": "EUR",
        "items": [
            {
                "description": "Consultation technique",
                "quantity": 1.0,
                "unit_price": 500.00,
                "total": 500.00
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

# Sauvegarder le XML
xml_content = result['xml']
with open("facture_facturx.xml", "w", encoding="utf-8") as f:
    f.write(xml_content)

print("✅ XML Factur-X généré")
```

**Exemple de réponse :**

```json
{
  "success": true,
  "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<rsm:CrossIndustryInvoice>...</rsm:CrossIndustryInvoice>",
  "format": "Factur-X EN16931"
}
```

---

### 2. Parsing depuis PDF/A-3

**Endpoint :** `POST /facturx/parse`

**Description :** Extrait le XML Factur-X embarqué dans un PDF/A-3.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `file` | File | ✅ Oui | PDF/A-3 avec XML Factur-X embarqué |

**Exemple de requête :**

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/facturx/parse"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret"
}

files = {
    "file": open("facture_facturx.pdf", "rb")
}

response = requests.post(url, headers=headers, files=files)
result = response.json()

print("XML extrait :")
print(result['xml'])
print("\nDonnées parsées :")
print(result['invoice_data'])
```

---

### 3. Parsing XML Factur-X

**Endpoint :** `POST /facturx/parse-xml`

**Description :** Parse un XML Factur-X et extrait les données structurées.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `xml_content` | String | ✅ Oui | XML Factur-X (format string) |

**Exemple de requête :**

```python
import requests

# Lire le XML depuis un fichier
with open("facture_facturx.xml", "r", encoding="utf-8") as f:
    xml_content = f.read()

url = "https://ocr-facture-api-production.up.railway.app/facturx/parse-xml"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "xml_content": xml_content
}

response = requests.post(url, headers=headers, json=data)
invoice_data = response.json()['invoice_data']

print(f"Numéro : {invoice_data['invoice_number']}")
print(f"Date : {invoice_data['date']}")
print(f"Total TTC : {invoice_data['total_ttc']}€")
```

---

### 4. Validation XML Factur-X

**Endpoint :** `POST /facturx/validate`

**Description :** Valide un XML Factur-X contre le schéma EN16931 et vérifie les règles métier.

**Paramètres :**

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `xml_content` | String | ✅ Oui | XML Factur-X à valider |

**Exemple de requête :**

```python
import requests

with open("facture_facturx.xml", "r", encoding="utf-8") as f:
    xml_content = f.read()

url = "https://ocr-facture-api-production.up.railway.app/facturx/validate"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret",
    "Content-Type": "application/json"
}
data = {
    "xml_content": xml_content
}

response = requests.post(url, headers=headers, json=data)
validation = response.json()['validation']

if validation['valid']:
    print("✅ XML Factur-X valide")
else:
    print("❌ Erreurs détectées :")
    for error in validation['errors']:
        print(f"  - {error}")

if validation['warnings']:
    print("\n⚠️ Avertissements :")
    for warning in validation['warnings']:
        print(f"  - {warning}")

print("\nRapport complet :")
print(validation['report'])
```

**Exemple de réponse :**

```json
{
  "success": true,
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": [],
    "report": "✅ Aucune erreur détectée"
  }
}
```

---

## 📊 Format des réponses

### Structure standard

Toutes les réponses suivent cette structure :

```json
{
  "success": true,
  "data": {...},
  "extracted_data": {...},
  "confidence_scores": {...},
  "compliance": {...},
  "cached": false,
  "error": null
}
```

### Données extraites (extracted_data)

```json
{
  "text": "Texte complet extrait...",
  "lines": ["Ligne 1", "Ligne 2", ...],
  "invoice_number": "FAC-2024-001",
  "date": "15/03/2024",
  "total": 1250.50,
  "total_ht": 1042.08,
  "total_ttc": 1250.50,
  "tva": 208.42,
  "vendor": "Société Example SARL",
  "client": "Client ABC",
  "items": [
    {
      "description": "Consultation technique",
      "quantity": 1.0,
      "unit_price": 500.00,
      "total": 500.00
    }
  ],
  "tables": [
    {
      "header": ["Description", "Quantité", "Prix"],
      "rows": [...],
      "row_count": 5
    }
  ],
  "banking_info": {
    "iban": "FR7612345678901234567890123",
    "swift": "ABCDEFGH",
    "rib": "12345123451234567890123"
  },
  "currency": "EUR"
}
```

### Scores de confiance (confidence_scores)

Chaque donnée extraite a un score de confiance de 0 à 1 :

```json
{
  "total": 0.95,
  "total_ht": 0.93,
  "total_ttc": 0.95,
  "tva": 0.94,
  "date": 0.98,
  "invoice_number": 0.88,
  "vendor": 0.85,
  "client": 0.82,
  "items": 0.90,
  "tables": 0.85,
  "banking_info": 0.78
}
```

**Interprétation :**
- **0.9 - 1.0** : Très fiable ✅
- **0.7 - 0.9** : Fiable ⚠️
- **< 0.7** : À vérifier ❌

---

## ⚠️ Gestion des erreurs

### Codes HTTP

| Code | Signification | Description |
|------|---------------|-------------|
| **200** | OK | Requête réussie |
| **400** | Bad Request | Paramètres invalides |
| **401** | Unauthorized | Authentification manquante ou invalide |
| **404** | Not Found | Ressource non trouvée |
| **422** | Unprocessable Entity | Erreur de conformité ou validation |
| **429** | Too Many Requests | Quota dépassé |
| **500** | Internal Server Error | Erreur serveur |
| **504** | Gateway Timeout | Timeout OCR (fichier trop gros) |

### Format des erreurs

```json
{
  "success": false,
  "error": "Message d'erreur détaillé",
  "error_code": "ERROR_CODE",
  "details": {
    "field": "nom_du_champ",
    "message": "Description détaillée"
  }
}
```

### Exemples d'erreurs

**Erreur 401 - Non autorisé :**
```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing X-RapidAPI-Proxy-Secret header"
}
```

**Erreur 400 - Fichier invalide :**
```json
{
  "error": "Bad Request",
  "message": "Le fichier doit être une image (jpeg, png) ou un PDF"
}
```

**Erreur 422 - Non conforme :**
```json
{
  "success": false,
  "error": "Facture non conforme",
  "compliance": {
    "compliant": false,
    "score": 65.0,
    "missing_fields": ["Date d'émission", "Numéro de facture"]
  }
}
```

---

## 💻 Exemples d'intégration

### Python - SDK simple

```python
import requests
from typing import Optional, Dict

class OCRFactureAPI:
    def __init__(self, api_secret: str, base_url: str = "https://ocr-facture-api-production.up.railway.app"):
        self.api_secret = api_secret
        self.base_url = base_url
        self.headers = {
            "X-RapidAPI-Proxy-Secret": api_secret
        }
    
    def extract(self, file_path: str, language: str = "fra", check_compliance: bool = False) -> Dict:
        """Extrait les données d'une facture"""
        url = f"{self.base_url}/ocr/upload"
        
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "language": language,
                "check_compliance": check_compliance
            }
            response = requests.post(url, headers=self.headers, files=files, data=data)
            response.raise_for_status()
            return response.json()
    
    def generate_facturx(self, invoice_data: Dict) -> str:
        """Génère un XML Factur-X"""
        url = f"{self.base_url}/facturx/generate"
        response = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json={"invoice_data": invoice_data}
        )
        response.raise_for_status()
        return response.json()["xml"]
    
    def validate_compliance(self, invoice_data: Dict) -> Dict:
        """Valide la conformité d'une facture"""
        url = f"{self.base_url}/compliance/check"
        response = requests.post(
            url,
            headers={**self.headers, "Content-Type": "application/json"},
            json={"invoice_data": invoice_data}
        )
        response.raise_for_status()
        return response.json()["compliance"]

# Utilisation
api = OCRFactureAPI(api_secret="votre-secret")

# Extraire une facture
result = api.extract("facture.pdf", check_compliance=True)
print(f"Numéro : {result['extracted_data']['invoice_number']}")
print(f"Conforme : {result['compliance']['compliance_check']['compliant']}")

# Générer Factur-X
xml_facturx = api.generate_facturx(result['extracted_data'])
with open("facture_facturx.xml", "w") as f:
    f.write(xml_facturx)
```

---

### JavaScript/Node.js

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

class OCRFactureAPI {
    constructor(apiSecret, baseUrl = 'https://ocr-facture-api-production.up.railway.app') {
        this.apiSecret = apiSecret;
        this.baseUrl = baseUrl;
        this.headers = {
            'X-RapidAPI-Proxy-Secret': apiSecret
        };
    }

    async extract(filePath, language = 'fra', checkCompliance = false) {
        const form = new FormData();
        form.append('file', fs.createReadStream(filePath));
        form.append('language', language);
        form.append('check_compliance', checkCompliance.toString());

        const response = await axios.post(
            `${this.baseUrl}/ocr/upload`,
            form,
            {
                headers: {
                    ...this.headers,
                    ...form.getHeaders()
                }
            }
        );

        return response.data;
    }

    async generateFacturX(invoiceData) {
        const response = await axios.post(
            `${this.baseUrl}/facturx/generate`,
            { invoice_data: invoiceData },
            {
                headers: {
                    ...this.headers,
                    'Content-Type': 'application/json'
                }
            }
        );

        return response.data.xml;
    }
}

// Utilisation
const api = new OCRFactureAPI('votre-secret');

(async () => {
    const result = await api.extract('facture.pdf', 'fra', true);
    console.log(`Numéro : ${result.extracted_data.invoice_number}`);
    console.log(`Conforme : ${result.compliance.compliance_check.compliant}`);

    const xmlFacturX = await api.generateFacturX(result.extracted_data);
    fs.writeFileSync('facture_facturx.xml', xmlFacturX);
})();
```

---

### PHP

```php
<?php

class OCRFactureAPI {
    private $apiSecret;
    private $baseUrl;
    
    public function __construct($apiSecret, $baseUrl = 'https://ocr-facture-api-production.up.railway.app') {
        $this->apiSecret = $apiSecret;
        $this->baseUrl = $baseUrl;
    }
    
    public function extract($filePath, $language = 'fra', $checkCompliance = false) {
        $url = $this->baseUrl . '/ocr/upload';
        
        $ch = curl_init($url);
        
        $postData = [
            'file' => new CURLFile($filePath),
            'language' => $language,
            'check_compliance' => $checkCompliance ? 'true' : 'false'
        ];
        
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $postData,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'X-RapidAPI-Proxy-Secret: ' . $this->apiSecret
            ]
        ]);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        return json_decode($response, true);
    }
    
    public function generateFacturX($invoiceData) {
        $url = $this->baseUrl . '/facturx/generate';
        
        $ch = curl_init($url);
        
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode(['invoice_data' => $invoiceData]),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => [
                'X-RapidAPI-Proxy-Secret: ' . $this->apiSecret,
                'Content-Type: application/json'
            ]
        ]);
        
        $response = curl_exec($ch);
        curl_close($ch);
        
        $result = json_decode($response, true);
        return $result['xml'];
    }
}

// Utilisation
$api = new OCRFactureAPI('votre-secret');

$result = $api->extract('facture.pdf', 'fra', true);
echo "Numéro : " . $result['extracted_data']['invoice_number'] . "\n";
echo "Conforme : " . ($result['compliance']['compliance_check']['compliant'] ? 'Oui' : 'Non') . "\n";

$xmlFacturX = $api->generateFacturX($result['extracted_data']);
file_put_contents('facture_facturx.xml', $xmlFacturX);
?>
```

---

## 🎯 Cas d'usage détaillés

### Cas d'usage 1 : Automatisation comptable

**Scénario :** Un cabinet comptable veut automatiser la saisie de factures.

**Workflow :**
1. Upload PDF facture → Extraction OCR
2. Validation conformité → Vérification mentions légales
3. Enrichissement SIRET → Données entreprise complètes
4. Import ERP → Création écritures comptables

**Code :**
```python
api = OCRFactureAPI("votre-secret")

# 1. Extraire avec compliance
result = api.extract("facture.pdf", check_compliance=True)

# 2. Vérifier conformité
if not result['compliance']['compliance_check']['compliant']:
    print("⚠️ Facture non conforme")
    print(f"Champs manquants : {result['compliance']['compliance_check']['missing_fields']}")
    # Arrêter le traitement ou notifier l'utilisateur
    exit(1)

# 3. Enrichir avec SIRET si disponible
siret = result['compliance']['siren_siret'].get('siret')
if siret:
    enrichment = requests.post(
        f"{api.base_url}/compliance/enrich-siret",
        headers=api.headers,
        json={"siret": siret}
    ).json()
    print(f"Entreprise : {enrichment['enrichment'].get('company_name')}")

# 4. Importer dans ERP (exemple)
erp_data = {
    "invoice_number": result['extracted_data']['invoice_number'],
    "date": result['extracted_data']['date'],
    "amount": result['extracted_data']['total_ttc'],
    "vendor": result['extracted_data']['vendor']
}
# ... import dans ERP
```

---

### Cas d'usage 2 : Génération Factur-X automatique

**Scénario :** Une entreprise veut convertir ses factures papier en Factur-X.

**Workflow :**
1. Scanner facture → PDF
2. Extraction OCR → Données JSON
3. Génération Factur-X → XML
4. Archivage → PDF/A-3 avec XML embarqué (à implémenter)

**Code :**
```python
api = OCRFactureAPI("votre-secret")

# 1. Extraire données
result = api.extract("facture_scannee.pdf")

# 2. Générer Factur-X
xml_facturx = api.generate_facturX(result['extracted_data'])

# 3. Valider le XML généré
validation = requests.post(
    f"{api.base_url}/facturx/validate",
    headers={**api.headers, "Content-Type": "application/json"},
    json={"xml_content": xml_facturx}
).json()

if validation['validation']['valid']:
    # Sauvegarder
    with open("facture_facturx.xml", "w", encoding="utf-8") as f:
        f.write(xml_facturx)
    print("✅ Factur-X généré et validé")
else:
    print("❌ Erreurs dans le XML généré")
    print(validation['validation']['report'])
```

---

### Cas d'usage 3 : Traitement par lot

**Scénario :** Traiter un dossier de 50 factures quotidiennement.

**Workflow :**
1. Lister fichiers → Dossier factures
2. Traitement par lot → 10 factures par requête
3. Vérification conformité → Filtrer factures non conformes
4. Export CSV → Pour import ERP

**Code :**
```python
import os
import base64
import csv
from pathlib import Path

api = OCRFactureAPI("votre-secret")

def encode_pdf(file_path):
    with open(file_path, "rb") as f:
        return f"data:application/pdf;base64,{base64.b64encode(f.read()).decode()}"

# 1. Lister tous les PDFs
factures_dir = Path("factures")
pdf_files = list(factures_dir.glob("*.pdf"))

# 2. Traiter par lots de 10
results = []
for i in range(0, len(pdf_files), 10):
    batch_files = pdf_files[i:i+10]
    
    batch_data = {
        "files": [encode_pdf(str(f)) for f in batch_files],
        "language": "fra"
    }
    
    response = requests.post(
        f"{api.base_url}/ocr/batch",
        headers={**api.headers, "Content-Type": "application/json"},
        json=batch_data
    )
    
    batch_results = response.json()['results']
    results.extend(batch_results)

# 3. Filtrer factures conformes
conformes = []
non_conformes = []

for result in results:
    if result['success']:
        # Vérifier compliance si disponible
        if result.get('compliance'):
            if result['compliance']['compliance_check']['compliant']:
                conformes.append(result)
            else:
                non_conformes.append(result)
        else:
            conformes.append(result)

# 4. Exporter CSV
with open("factures_conformes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Numéro", "Date", "Vendeur", "Total TTC", "SIRET"])
    
    for facture in conformes:
        ed = facture['extracted_data']
        writer.writerow([
            ed.get('invoice_number'),
            ed.get('date'),
            ed.get('vendor'),
            ed.get('total_ttc'),
            facture.get('compliance', {}).get('siren_siret', {}).get('siret')
        ])

print(f"✅ {len(conformes)} factures conformes exportées")
print(f"⚠️ {len(non_conformes)} factures non conformes à vérifier")
```

---

## ❓ FAQ

### Questions générales

**Q : Quelle est la précision de l'OCR ?**

R : La précision dépend de la qualité du document source. Pour des factures scannées de bonne qualité, la précision est généralement de 85-95%. Les scores de confiance fournis pour chaque donnée vous permettent de savoir ce qui doit être vérifié.

**Q : Puis-je traiter des factures de plusieurs pages ?**

R : Oui, l'API supporte les PDFs multi-pages. Toutes les pages sont traitées et fusionnées automatiquement.

**Q : Combien de temps prend le traitement ?**

R : La plupart des factures sont traitées en moins de 2 secondes. Les fichiers déjà traités sont servis instantanément depuis le cache.

**Q : Les données sont-elles stockées ?**

R : Les fichiers uploadés ne sont pas stockés de manière permanente. Les résultats peuvent être mis en cache jusqu'à 24 heures pour améliorer les performances.

---

### Questions sur la conformité

**Q : L'API garantit-elle la conformité légale de mes factures ?**

R : Non. L'API fournit des outils de validation mais ne constitue pas un conseil juridique ou comptable. Vous êtes responsable de vérifier la conformité complète selon vos obligations légales.

**Q : Quels sont les taux de TVA validés ?**

R : Les taux français standards : 20%, 10%, 5.5%, 2.1%, 0%. L'API vérifie également que les calculs sont corrects (HT + TVA = TTC).

**Q : Comment fonctionne l'enrichissement SIRET ?**

R : Si un SIRET est détecté dans la facture, l'API peut enrichir les données avec l'API Sirene (Insee). Cela nécessite la configuration de clés API Sirene côté serveur (optionnel).

---

### Questions sur Factur-X

**Q : Le XML généré est-il conforme EN16931 ?**

R : Oui, le XML généré suit le standard EN16931 (profil basic). Vous pouvez le valider avec l'endpoint `/facturx/validate`.

**Q : Puis-je générer un PDF/A-3 avec XML embarqué ?**

R : Actuellement, l'API génère uniquement le XML. La génération de PDF/A-3 avec XML embarqué est prévue dans une future version.

**Q : Puis-je convertir Factur-X vers UBL (Peppol) ?**

R : Cette fonctionnalité n'est pas encore disponible mais est prévue dans la roadmap.

---

### Questions techniques

**Q : Puis-je utiliser l'API en production ?**

R : Oui, l'API est conçue pour la production. Nous recommandons de commencer avec le plan Basic ou Pro pour une meilleure disponibilité.

**Q : Y a-t-il des limites de débit ?**

R : Oui, selon votre plan d'abonnement. Consultez la section "Tarification" pour les détails.

**Q : Que faire en cas d'erreur 429 (Too Many Requests) ?**

R : Vous avez dépassé votre quota. Attendez la réinitialisation (quotidienne ou mensuelle selon votre plan) ou passez à un plan supérieur.

**Q : L'API supporte-t-elle les webhooks ?**

R : Oui, des webhooks sont disponibles pour Zapier, Make et Salesforce. D'autres intégrations peuvent être ajoutées sur demande.

---

## 📞 Support

### Documentation

- **Swagger UI** : `https://ocr-facture-api-production.up.railway.app/docs`
- **GitHub** : [https://github.com/RailsNft/OCR-Facture-API](https://github.com/RailsNft/OCR-Facture-API)
- **Documentation complète** : Ce document

### Support technique

- **Via RapidAPI** : Support intégré dans le dashboard RapidAPI
- **Email** : Via le support RapidAPI (mentionnez "OCR Facture API")

### Rapporter un bug

Pour rapporter un bug :

1. Allez sur GitHub : [https://github.com/RailsNft/OCR-Facture-API/issues](https://github.com/RailsNft/OCR-Facture-API/issues)
2. Créez une nouvelle issue
3. Incluez :
   - Description du problème
   - Étapes pour reproduire
   - Fichier de test (si possible, anonymisé)
   - Message d'erreur complet

---

## 📝 Changelog

### Version 2.0.0 (Actuelle)

**Nouvelles fonctionnalités :**
- ✅ Validation conformité française (mentions légales, TVA)
- ✅ Détection et enrichissement SIREN/SIRET
- ✅ Validation VIES (TVA intracom)
- ✅ Génération XML Factur-X (EN16931)
- ✅ Parsing et validation Factur-X
- ✅ Support compliance dans `/ocr/upload`

**Améliorations :**
- Optimisation performances
- Cache intelligent amélioré
- Scores de confiance pour toutes les données

### Version 1.2.0

- Extraction lignes de facture (items)
- Scores de confiance
- Support PDF multi-pages
- Détection tableaux structurés
- Extraction coordonnées bancaires
- Traitement par lot
- Webhooks Zapier/Make/Salesforce

---

## 🔗 Liens utiles

- **API Base URL** : `https://ocr-facture-api-production.up.railway.app`
- **Swagger UI** : `https://ocr-facture-api-production.up.railway.app/docs`
- **GitHub** : [https://github.com/RailsNft/OCR-Facture-API](https://github.com/RailsNft/OCR-Facture-API)
- **RapidAPI** : [Lien vers votre API sur RapidAPI]

---

**Documentation créée le :** [Date actuelle]  
**Version API :** 2.0.0  
**Dernière mise à jour :** [Date actuelle]

