# Tutoriel RapidAPI - Comment utiliser OCR Facture FR → JSON + Factur-X

## 🎯 Introduction

Cette API permet d'extraire automatiquement les données structurées de vos factures françaises et européennes, avec support du standard Factur-X (EN16931).

**Cas d'usage :**
- Automatisation comptable
- Extraction de données pour ERP
- Traitement par lot de factures
- Intégration dans workflows Zapier/Make

---

## 🚀 Démarrage rapide

### Étape 1 : S'abonner à l'API

1. Allez sur [RapidAPI](https://rapidapi.com) et cherchez **"OCR Facture FR"**
2. Cliquez sur l'API
3. Choisissez le plan **Basic** (100 requêtes/mois - gratuit)
4. Cliquez sur "Subscribe"
5. Obtenez votre clé API dans le dashboard

### Étape 2 : Votre première requête

#### Avec cURL

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -F "file=@facture.jpg" \
  -F "language=fra"
```

#### Avec Python

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/ocr/upload"
headers = {
    "X-RapidAPI-Proxy-Secret": "votre-secret"
}

files = {
    "file": open("facture.jpg", "rb")
}
data = {
    "language": "fra"
}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

#### Avec JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('facture.jpg'));
form.append('language', 'fra');

axios.post('https://ocr-facture-api-production.up.railway.app/ocr/upload', form, {
  headers: {
    ...form.getHeaders(),
    'X-RapidAPI-Proxy-Secret': 'votre-secret'
  }
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

---

## 📋 Endpoints disponibles

### 1. Upload de fichier (`/ocr/upload`)

**Méthode** : `POST`  
**Content-Type** : `multipart/form-data`

**Paramètres :**
- `file` (File, requis) : Image ou PDF de la facture
- `language` (String, optionnel) : Code langue (fra, eng, deu, spa, ita, por). Défaut: fra

**Réponse :**
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
    "total": 1250.50,
    "total_ht": 1042.08,
    "total_ttc": 1250.50,
    "tva": 208.42,
    "date": "15/03/2024",
    "invoice_number": "FAC-2024-001",
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
    "tables": [...],
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
  }
}
```

### 2. Base64 (`/ocr/base64`)

**Méthode** : `POST`  
**Content-Type** : `application/x-www-form-urlencoded`

**Paramètres :**
- `image_base64` (String, requis) : Image encodée en base64
- `language` (String, optionnel) : Code langue

**Exemple :**
```python
import base64
import requests

with open("facture.jpg", "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/ocr/base64",
    headers={"X-RapidAPI-Proxy-Secret": "votre-secret"},
    data={
        "image_base64": f"data:image/jpeg;base64,{image_base64}",
        "language": "fra"
    }
)
```

### 3. Traitement par lot (`/ocr/batch`)

**Méthode** : `POST`  
**Content-Type** : `application/json`

**Limite** : Maximum 10 fichiers par requête

**Exemple :**
```python
import base64
import requests

def encode_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

files = [
    f"data:image/jpeg;base64,{encode_image('facture1.jpg')}",
    f"data:image/jpeg;base64,{encode_image('facture2.jpg')}"
]

response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/ocr/batch",
    headers={
        "X-RapidAPI-Proxy-Secret": "votre-secret",
        "Content-Type": "application/json"
    },
    json={
        "files": files,
        "language": "fra"
    }
)

results = response.json()
print(f"Traités: {results['total_processed']}")
print(f"Depuis cache: {results['total_cached']}")
```

---

## 🎨 Cas d'usage pratiques

### Cas 1 : Automatisation comptable

```python
import requests
import json
from pathlib import Path

def process_invoice_folder(folder_path):
    """Traite tous les fichiers d'un dossier"""
    results = []
    
    for file_path in Path(folder_path).glob("*.jpg"):
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {"language": "fra"}
            
            response = requests.post(
                "https://ocr-facture-api-production.up.railway.app/ocr/upload",
                headers={"X-RapidAPI-Proxy-Secret": "votre-secret"},
                files=files,
                data=data
            )
            
            if response.json()["success"]:
                extracted = response.json()["extracted_data"]
                results.append({
                    "file": file_path.name,
                    "invoice_number": extracted["invoice_number"],
                    "total": extracted["total_ttc"],
                    "date": extracted["date"]
                })
    
    return results

# Utilisation
invoices = process_invoice_folder("./factures/")
print(json.dumps(invoices, indent=2, ensure_ascii=False))
```

### Cas 2 : Intégration Zapier

1. Dans Zapier, créez un nouveau Zap
2. Déclencheur : "Email" (nouvelle facture reçue)
3. Action : "Code by Zapier" → Utilisez le webhook `/webhooks/zapier`
4. Action suivante : Créer un enregistrement dans votre ERP

### Cas 3 : Traitement par lot avec cache

```python
import requests

def process_multiple_invoices(invoice_paths):
    """Traite plusieurs factures en utilisant le cache"""
    
    # Encoder toutes les images
    files_base64 = []
    for path in invoice_paths:
        with open(path, "rb") as f:
            files_base64.append(
                f"data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
            )
    
    # Requête batch
    response = requests.post(
        "https://ocr-facture-api-production.up.railway.app/ocr/batch",
        headers={
            "X-RapidAPI-Proxy-Secret": "votre-secret",
            "Content-Type": "application/json"
        },
        json={
            "files": files_base64,
            "language": "fra"
        }
    )
    
    results = response.json()
    
    # Afficher les résultats
    for i, result in enumerate(results["results"]):
        if result["success"]:
            cached_status = "✅ Cache" if result["cached"] else "🔄 Nouveau"
            print(f"{cached_status} - Facture {i+1}: {result['extracted_data']['invoice_number']}")
```

---

## 📊 Comprendre les scores de confiance

Chaque donnée extraite a un score de confiance (0-1) :

- **0.9-1.0** : Très fiable ✅
- **0.7-0.9** : Fiable ⚠️
- **<0.7** : À vérifier ❌

**Exemple d'utilisation :**
```python
confidence = response.json()["confidence_scores"]

if confidence["total"] > 0.9:
    print("Montant total fiable")
else:
    print("Vérifier manuellement le montant total")
```

---

## 🔧 Gestion des erreurs

```python
try:
    response = requests.post(url, ...)
    response.raise_for_status()
    
    data = response.json()
    
    if not data["success"]:
        print(f"Erreur: {data.get('error')}")
    else:
        # Traiter les données
        pass
        
except requests.exceptions.RequestException as e:
    print(f"Erreur réseau: {e}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

---

## 💡 Conseils et bonnes pratiques

1. **Utilisez le cache** : Si vous traitez plusieurs fois la même facture, le cache accélère la réponse
2. **Vérifiez les scores** : Utilisez `confidence_scores` pour valider les données critiques
3. **Batch processing** : Pour plusieurs factures, utilisez `/ocr/batch` au lieu de plusieurs requêtes
4. **Gestion des erreurs** : Toujours vérifier `success` dans la réponse
5. **Langue** : Spécifiez toujours la langue pour de meilleurs résultats

---

## 📚 Ressources supplémentaires

- **Documentation complète** : [GitHub Repository](https://github.com/RailsNft/OCR-Facture-API)
- **Swagger UI** : `https://ocr-facture-api-production.up.railway.app/docs`
- **Support** : Via RapidAPI Provider Dashboard

---

## ❓ FAQ

**Q : Quelle est la limite du plan Basic ?**  
R : Basic = 100/mois (gratuit), Pro = 20k/mois ($15), Ultra = 80k/mois ($59), Mega = 250k/mois ($149)

**Q : Puis-je traiter des PDFs ?**  
R : Oui, l'API supporte les PDFs (multi-pages)

**Q : Les données sont-elles stockées ?**  
R : Non, l'API ne stocke pas vos données (seulement cache temporaire)

**Q : Quelle langue dois-je utiliser ?**  
R : Utilisez `fra` pour les factures françaises, `eng` pour anglaises, etc.

---

**Bon traitement de factures ! 🚀**

