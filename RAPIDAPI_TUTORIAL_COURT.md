# Tutoriel OCR Facture API - Démarrage en 5 minutes

## 🎯 Introduction

Ce tutoriel vous guide pour extraire automatiquement les données de vos factures (montants, dates, numéros) en quelques minutes.

**Temps estimé** : 5 minutes | **Niveau** : Débutant

---

## 📋 Étape 1 : S'abonner à l'API

1. Allez sur [rapidapi.com](https://rapidapi.com) et créez un compte (gratuit)
2. Recherchez **"OCR Facture"** dans la barre de recherche
3. Cliquez sur l'API et choisissez le plan **Basic** (100 requêtes/mois - gratuit)
4. Cliquez sur **"Subscribe"**
5. Obtenez votre clé API dans **"My Apps"** → Créez une application → Copiez la clé

---

## 🚀 Étape 2 : Votre première requête

### Avec Python (Recommandé)

```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload"

headers = {
    "X-RapidAPI-Key": "VOTRE_CLE_API_ICI",
    "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app"
}

# Ouvrir votre facture
with open("facture.jpg", "rb") as f:
    files = {"file": f}
    data = {"language": "fra"}  # fra = français
    
    response = requests.post(url, headers=headers, files=files, data=data)
    result = response.json()
    
    if result["success"]:
        print(f"✅ Numéro: {result['extracted_data']['invoice_number']}")
        print(f"✅ Total: {result['extracted_data']['total_ttc']} €")
        print(f"✅ Date: {result['extracted_data']['date']}")
```

### Avec cURL

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload" \
  -H "X-RapidAPI-Key: VOTRE_CLE_API_ICI" \
  -H "X-RapidAPI-Host: ocr-facture-api-production.up.railway.app" \
  -F "file=@facture.jpg" \
  -F "language=fra"
```

### Avec JavaScript

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
    'X-RapidAPI-Key': 'VOTRE_CLE_API_ICI',
    'X-RapidAPI-Host': 'ocr-facture-api-production.up.railway.app'
  }
})
.then(response => {
  const data = response.data;
  console.log(`Numéro: ${data.extracted_data.invoice_number}`);
  console.log(`Total: ${data.extracted_data.total_ttc} €`);
});
```

---

## 📊 Comprendre la réponse

La réponse contient :

- **`extracted_data`** : Toutes les données extraites
  - `invoice_number` : Numéro de facture
  - `total_ttc` : Total TTC
  - `total_ht` : Total HT
  - `tva` : Montant TVA
  - `date` : Date de facture
  - `vendor` : Vendeur
  - `client` : Client
  - `items` : Lignes de facture (description, quantité, prix)

- **`confidence_scores`** : Scores de confiance (0-1)
  - > 0.9 : Très fiable ✅
  - 0.7-0.9 : Fiable ⚠️
  - < 0.7 : À vérifier ❌

---

## 💡 Cas d'usage pratique : Traiter un dossier

```python
import requests
from pathlib import Path

def traiter_dossier(dossier):
    for fichier in Path(dossier).glob("*.jpg"):
        with open(fichier, "rb") as f:
            response = requests.post(
                "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload",
                headers={
                    "X-RapidAPI-Key": "VOTRE_CLE_API_ICI",
                    "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app"
                },
                files={"file": f},
                data={"language": "fra"}
            )
            
            if response.json()["success"]:
                data = response.json()["extracted_data"]
                print(f"{fichier.name}: {data['invoice_number']} - {data['total_ttc']} €")

traiter_dossier("./mes_factures/")
```

---

## ⚡ Traitement par lot (Batch)

Pour traiter plusieurs factures en une requête :

```python
import base64
import requests

def encoder_image(chemin):
    with open(chemin, "rb") as f:
        return base64.b64encode(f.read()).decode()

factures = [
    f"data:image/jpeg;base64,{encoder_image('facture1.jpg')}",
    f"data:image/jpeg;base64,{encoder_image('facture2.jpg')}"
]

response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/v1/ocr/batch",
    headers={
        "X-RapidAPI-Key": "VOTRE_CLE_API_ICI",
        "X-RapidAPI-Host": "ocr-facture-api-production.up.railway.app",
        "Content-Type": "application/json"
    },
    json={"files": factures, "language": "fra"}
)

results = response.json()
print(f"✅ {results['total_processed']} factures traitées")
```

---

## 🔧 Gestion des erreurs

```python
try:
    response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
    response.raise_for_status()
    
    data = response.json()
    if not data.get("success"):
        print(f"Erreur: {data.get('error')}")
        
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 401:
        print("❌ Clé API invalide")
    elif e.response.status_code == 429:
        print("❌ Trop de requêtes - attendez un peu")
    else:
        print(f"❌ Erreur HTTP {e.response.status_code}")
except Exception as e:
    print(f"❌ Erreur: {e}")
```

---

## 💡 Conseils

1. **Langue** : Utilisez `fra` pour français, `eng` pour anglais
2. **Qualité** : Images claires = meilleurs résultats
3. **Cache** : L'API met en cache pendant 24h (réponses instantanées)
4. **Batch** : Utilisez `/ocr/batch` pour plusieurs factures
5. **Scores** : Vérifiez `confidence_scores` pour valider les données

---

## ❓ FAQ

**Q : Combien de requêtes par mois ?**  
R : Plan Basic = 100/mois (gratuit), Pro = 20k/mois ($15), Ultra = 80k/mois ($59), Mega = 250k/mois ($149)

**Q : Support PDF ?**  
R : Oui, PDFs multi-pages supportés

**Q : Données stockées ?**  
R : Non, seulement cache temporaire 24h

**Q : Précision ?**  
R : >90% pour factures imprimées, moyenne pour manuscrites

---

## 📚 Ressources

- **Documentation complète** : `/docs` sur l'API
- **Support** : RapidAPI Provider Dashboard

**Bon traitement de factures ! 🚀**

