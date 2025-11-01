# 📚 Tutoriel complet - OCR Facture API sur RapidAPI

## 🎯 Introduction

Ce tutoriel vous guide pas à pas pour utiliser l'API OCR Facture sur RapidAPI. Vous apprendrez à extraire automatiquement les données de vos factures (montants, dates, numéros, etc.) en quelques minutes.

**Temps estimé** : 15 minutes  
**Niveau** : Débutant à Intermédiaire

---

## 📋 Prérequis

- Un compte RapidAPI (gratuit)
- Une clé API RapidAPI
- Une facture en format image (JPG, PNG) ou PDF
- Python 3.7+ (pour les exemples) ou un outil de test HTTP (curl, Postman)

---

## 🚀 Étape 1 : S'abonner à l'API

### 1.1 Créer un compte RapidAPI

1. Allez sur [rapidapi.com](https://rapidapi.com)
2. Cliquez sur **"Sign Up"** (inscription gratuite)
3. Créez votre compte avec email ou GitHub

### 1.2 Trouver l'API OCR Facture

1. Dans la barre de recherche, tapez **"OCR Facture"** ou **"OCR Facture API"**
2. Cliquez sur l'API dans les résultats
3. Vous verrez la page de l'API avec les plans disponibles

### 1.3 Choisir un plan

**Plan Basic (Gratuit - Recommandé pour commencer)** :
- ✅ 100 requêtes/mois
- ✅ OCR basique uniquement
- ✅ Support documentation

**Plan Pro** :
- ✅ 20 000 requêtes/mois - $15/mois
- ✅ Compliance FR + Factur-X
- ✅ Batch processing activé

**Plan Ultra** :
- ✅ 80 000 requêtes/mois - $59/mois
- ✅ Support prioritaire

**Plan Mega** :
- ✅ 250 000 requêtes/mois - $149/mois
- ✅ Support dédié

Cliquez sur **"Subscribe"** sur le plan de votre choix.

### 1.4 Obtenir votre clé API

1. Après abonnement, allez dans **"My Apps"** (Mes Applications)
2. Créez une nouvelle application ou sélectionnez-en une existante
3. Votre clé API (X-RapidAPI-Key) est affichée dans l'application
4. **Copiez cette clé** - vous en aurez besoin pour toutes les requêtes

---

## 🔧 Étape 2 : Configuration de base

### 2.1 Headers requis

Toutes les requêtes nécessitent ces headers :

```http
X-RapidAPI-Key: votre_cle_api_rapidapi
X-RapidAPI-Host: ocr-facture-api-production.up.railway.app
```

**Note** : Si vous utilisez directement l'API (sans passer par RapidAPI), utilisez :
```http
X-RapidAPI-Proxy-Secret: votre_secret_rapidapi
```

---

## 📤 Étape 3 : Votre première extraction

### 3.1 Préparer votre facture

- Format accepté : JPG, PNG, PDF
- Taille recommandée : Moins de 10 MB
- Qualité : Image claire et bien éclairée pour de meilleurs résultats

### 3.2 Requête avec cURL

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload" \
  -H "X-RapidAPI-Key: votre_cle_api_rapidapi" \
  -H "X-RapidAPI-Host: ocr-facture-api-production.up.railway.app" \
  -F "file=@/chemin/vers/votre/facture.jpg" \
  -F "language=fra"
```

### 3.3 Requête avec Python

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload"

headers = {
    "X-RapidAPI-Key": "votre_cle_api_rapidapi",
    "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app"
}

# Ouvrir le fichier facture
with open("facture.jpg", "rb") as f:
    files = {"file": f}
    data = {"language": "fra"}
    
    response = requests.post(url, headers=headers, files=files, data=data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Succès !")
        print(f"Numéro de facture: {result['extracted_data']['invoice_number']}")
        print(f"Total TTC: {result['extracted_data']['total_ttc']} €")
        print(f"Date: {result['extracted_data']['date']}")
    else:
        print(f"❌ Erreur: {response.status_code}")
        print(response.text)
```

### 3.4 Requête avec JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('file', fs.createReadStream('facture.jpg'));
form.append('language', 'fra');

axios.post('https://ocr-facture-api-production.up.railway.app/v1/ocr/upload', form, {
  headers: {
    ...form.getHeaders(),
    'X-RapidAPI-Key': 'votre_cle_api_rapidapi',
    'X-RapidAPI-Host': 'ocr-facture-api-production.up.railway.app'
  }
})
.then(response => {
  const data = response.data;
  console.log('✅ Succès !');
  console.log(`Numéro: ${data.extracted_data.invoice_number}`);
  console.log(`Total: ${data.extracted_data.total_ttc} €`);
})
.catch(error => {
  console.error('❌ Erreur:', error.response?.data || error.message);
});
```

---

## 📊 Étape 4 : Comprendre la réponse

### 4.1 Structure de la réponse

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
    "currency": "EUR"
  },
  "confidence_scores": {
    "total": 0.95,
    "invoice_number": 0.88,
    "items": 0.90
  }
}
```

### 4.2 Champs importants

- **`success`** : `true` si l'extraction a réussi
- **`cached`** : `true` si le résultat vient du cache (plus rapide)
- **`extracted_data`** : Toutes les données extraites de la facture
- **`confidence_scores`** : Scores de confiance (0-1) pour chaque donnée

### 4.3 Utiliser les scores de confiance

```python
confidence = result["confidence_scores"]

# Vérifier la fiabilité des données
if confidence["total"] > 0.9:
    print("✅ Montant total très fiable")
elif confidence["total"] > 0.7:
    print("⚠️ Montant total à vérifier")
else:
    print("❌ Montant total peu fiable - vérification manuelle requise")
```

---

## 🎯 Étape 5 : Cas d'usage pratiques

### Cas 1 : Traiter un dossier de factures

```python
import requests
from pathlib import Path
import json

def traiter_dossier_factures(dossier):
    """Traite toutes les factures d'un dossier"""
    results = []
    
    for fichier in Path(dossier).glob("*.jpg"):
        print(f"Traitement de {fichier.name}...")
        
        with open(fichier, "rb") as f:
            files = {"file": f}
            data = {"language": "fra"}
            
            response = requests.post(
                "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
                headers={
                    "X-RapidAPI-Key": "votre_cle_api_rapidapi",
                    "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app"
                },
                files=files,
                data=data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    extracted = data["extracted_data"]
                    results.append({
                        "fichier": fichier.name,
                        "numero": extracted.get("invoice_number"),
                        "date": extracted.get("date"),
                        "total": extracted.get("total_ttc"),
                        "vendeur": extracted.get("vendor")
                    })
    
    return results

# Utilisation
factures = traiter_dossier_factures("./mes_factures/")
print(json.dumps(factures, indent=2, ensure_ascii=False))
```

### Cas 2 : Traitement par lot (batch)

Pour traiter plusieurs factures en une seule requête :

```python
import base64
import requests

def encoder_image(chemin):
    """Encode une image en base64"""
    with open(chemin, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Préparer les fichiers
factures = [
    encoder_image("facture1.jpg"),
    encoder_image("facture2.jpg"),
    encoder_image("facture3.jpg")
]

# Requête batch
response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/v1/ocr/batch",
    headers={
        "X-RapidAPI-Key": "votre_cle_api_rapidapi",
        "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app",
        "Content-Type": "application/json"
    },
    json={
        "files": [f"data:image/jpeg;base64,{f}" for f in factures],
        "language": "fra"
    }
)

results = response.json()
print(f"✅ {results['total_processed']} factures traitées")
print(f"⚡ {results['total_cached']} depuis le cache")
```

### Cas 3 : Export vers CSV

```python
import requests
import csv
from pathlib import Path

def exporter_factures_csv(dossier_factures, fichier_csv):
    """Traite des factures et exporte les résultats en CSV"""
    
    with open(fichier_csv, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Fichier', 'Numéro', 'Date', 'Vendeur', 'Total HT', 'TVA', 'Total TTC'])
        
        for fichier in Path(dossier_factures).glob("*.jpg"):
            with open(fichier, "rb") as f:
                response = requests.post(
                    "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
                    headers={
                        "X-RapidAPI-Key": "votre_cle_api_rapidapi",
                        "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app"
                    },
                    files={"file": f},
                    data={"language": "fra"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        ext = data["extracted_data"]
                        writer.writerow([
                            fichier.name,
                            ext.get("invoice_number", ""),
                            ext.get("date", ""),
                            ext.get("vendor", ""),
                            ext.get("total_ht", ""),
                            ext.get("tva", ""),
                            ext.get("total_ttc", "")
                        ])

# Utilisation
exporter_factures_csv("./factures/", "resultats.csv")
print("✅ Export terminé dans resultats.csv")
```

---

## 🔍 Étape 6 : Gestion des erreurs

### 6.1 Liste des codes d'erreur

- **200** : Succès ✅
- **400** : Fichier invalide ou paramètres incorrects
- **401** : Clé API invalide ou manquante
- **429** : Trop de requêtes (rate limit)
- **500** : Erreur serveur

### 6.2 Gestion d'erreurs complète

```python
import requests

def traiter_facture_securise(chemin_fichier):
    """Traite une facture avec gestion d'erreurs complète"""
    
    try:
        with open(chemin_fichier, "rb") as f:
            response = requests.post(
                "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
                headers={
                    "X-RapidAPI-Key": "votre_cle_api_rapidapi",
                    "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app"
                },
                files={"file": f},
                data={"language": "fra"},
                timeout=30  # Timeout de 30 secondes
            )
        
        # Vérifier le code de statut
        response.raise_for_status()
        
        # Vérifier la réponse JSON
        data = response.json()
        
        if not data.get("success"):
            print(f"❌ Erreur API: {data.get('error', 'Erreur inconnue')}")
            return None
        
        return data
        
    except requests.exceptions.Timeout:
        print("❌ Timeout : La requête a pris trop de temps")
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Erreur d'authentification : Vérifiez votre clé API")
        elif e.response.status_code == 429:
            print("❌ Trop de requêtes : Attendez un peu avant de réessayer")
        else:
            print(f"❌ Erreur HTTP {e.response.status_code}: {e.response.text}")
        return None
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {chemin_fichier}")
        return None
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return None

# Utilisation
resultat = traiter_facture_securise("facture.jpg")
if resultat:
    print("✅ Extraction réussie !")
```

---

## ⚡ Étape 7 : Optimisations et bonnes pratiques

### 7.1 Utiliser le cache

L'API met en cache les résultats pendant 24h. Si vous traitez plusieurs fois la même facture :

```python
# Première requête - traitement complet
response1 = requests.post(...)
print(f"Cache: {response1.json()['cached']}")  # False

# Deuxième requête - depuis le cache (instantané)
response2 = requests.post(...)
print(f"Cache: {response2.json()['cached']}")  # True
```

### 7.2 Choisir la bonne langue

Spécifiez toujours la langue pour de meilleurs résultats :

- `fra` : Français (défaut)
- `eng` : Anglais
- `deu` : Allemand
- `spa` : Espagnol
- `ita` : Italien
- `por` : Portugais

### 7.3 Traitement par lot vs requêtes individuelles

**Utilisez le batch** si vous avez :
- Plusieurs factures à traiter (> 3)
- Besoin de performance
- Budget limité (compte les requêtes)

**Utilisez les requêtes individuelles** si vous avez :
- Une seule facture
- Besoin de gestion d'erreurs fine
- Traitement asynchrone

---

## 📚 Étape 8 : Fonctionnalités avancées

### 8.1 Extraction avec validation de conformité

```python
response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
    headers={...},
    files={"file": f},
    data={
        "language": "fra",
        "check_compliance": "true"  # Activer la validation FR
    }
)

if response.json()["compliance"]:
    compliance = response.json()["compliance"]
    print(f"Score de conformité: {compliance['compliance_check']['score']}/100")
```

### 8.2 Extraction des coordonnées bancaires

Les coordonnées bancaires sont automatiquement extraites :

```python
banking = result["extracted_data"]["banking_info"]
print(f"IBAN: {banking.get('iban')}")
print(f"SWIFT: {banking.get('swift')}")
print(f"RIB: {banking.get('rib')}")
```

### 8.3 Extraction des tableaux structurés

```python
tables = result["extracted_data"]["tables"]
for table in tables:
    print(f"Tableau avec {table['row_count']} lignes")
    print(f"Colonnes: {table['header']}")
```

---

## ❓ FAQ

**Q : Combien de requêtes puis-je faire par mois ?**  
R : Dépend de votre plan : Basic = 100/mois (gratuit), Pro = 20k/mois ($15), Ultra = 80k/mois ($59), Mega = 250k/mois ($149)

**Q : Les données sont-elles stockées ?**  
R : Non, seulement un cache temporaire de 24h pour performance

**Q : Puis-je traiter des PDFs ?**  
R : Oui, l'API supporte les PDFs (même multi-pages)

**Q : Quelle est la précision de l'OCR ?**  
R : Très bonne pour factures imprimées (>90%), moyenne pour manuscrites

**Q : Comment améliorer les résultats ?**  
R : Utilisez des images de bonne qualité, spécifiez la langue correcte

---

## 🎓 Ressources supplémentaires

- **Documentation complète** : `/docs` sur l'API
- **Exemples de code** : Voir les fichiers d'exemple dans le dépôt GitHub
- **Support** : Via RapidAPI Provider Dashboard

---

**Félicitations ! Vous savez maintenant utiliser l'API OCR Facture sur RapidAPI ! 🚀**

Pour des questions ou du support, n'hésitez pas à consulter la documentation complète ou à contacter le support RapidAPI.

