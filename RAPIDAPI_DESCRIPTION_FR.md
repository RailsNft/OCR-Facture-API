# 📝 Description complète RapidAPI - Version française

## 🎯 Informations à copier-coller dans RapidAPI Dashboard

---

## 1️⃣ TITRE DE L'API

```
OCR Facture France – Extraction & Validation Factur-X (TVA, SIREN, mentions légales)
```

**Alternative (si trop long) :**
```
OCR Facture FR → JSON + Factur-X (TVA, SIREN, Compliance)
```

---

## 2️⃣ DESCRIPTION COURTE (Short Description)

```
API d'extraction et de validation de factures françaises (OCR Factur-X). Convertissez vos factures PDF en JSON structuré et conforme aux obligations légales françaises. Détection automatique TVA, SIREN/SIRET, mentions obligatoires. Génération Factur-X EN16931 optionnelle.
```

**Version encore plus courte (si limite de caractères) :**
```
Extraction OCR de factures françaises → JSON conforme (TVA, SIREN, Factur-X EN16931). Validation automatique des mentions légales obligatoires.
```

---

## 3️⃣ DESCRIPTION LONGUE (Long Description / API Details)

### Version complète (à copier tel quel) :

```markdown
# OCR Facture France – Extraction & Validation Factur-X

## 🎯 Vue d'ensemble

API professionnelle pour l'extraction automatique de données de factures françaises et européennes via OCR. Transformez vos factures PDF en données JSON structurées et conformes aux obligations légales françaises. Support complet du standard Factur-X (EN16931) pour la facturation électronique.

**Pourquoi cette API ?**

Les APIs OCR existantes sont calibrées sur des formats US/anglophones. Aucune ne valide les obligations légales françaises (TVA, SIRET, mentions "TVA non applicable art. 293 B..."). Cette API comble ce manque en proposant une solution spécialement conçue pour le marché français et européen.

---

## ✨ Fonctionnalités principales

### 📄 Extraction OCR automatique

- **Texte complet** : Extraction de tout le texte de la facture
- **Données structurées** : Montants HT, TTC, TVA, dates, numéros de facture
- **Lignes de facture** : Détection automatique des articles avec description, quantité, prix unitaire, total
- **Coordonnées bancaires** : Extraction IBAN, SWIFT/BIC, RIB, numéros de compte
- **Tableaux structurés** : Détection et extraction automatique des tableaux

### 🇫🇷 Conformité française

- **Validation mentions légales** : Vérification automatique des mentions obligatoires (date, numéro, montants, vendeur, client)
- **Validation TVA** : Vérification des taux TVA français (20%, 10%, 5.5%, 2.1%, 0%) et des calculs
- **Détection SIREN/SIRET** : Extraction automatique des numéros SIREN/SIRET dans la facture
- **Enrichissement SIRET** : Données complètes entreprise via API Sirene (Insee) - optionnel
- **Validation VIES** : Vérification des numéros TVA intracommunautaires via API européenne
- **Score de conformité** : Score 0-100 avec liste des champs manquants

### 📄 Factur-X (EN16931)

- **Génération XML Factur-X** : Création de XML conforme au standard EN16931
- **Parsing Factur-X** : Extraction du XML embarqué depuis PDF/A-3
- **Validation Factur-X** : Vérification structure XML + règles métier avec rapport détaillé
- **Format standard** : Compatible avec la facturation électronique française et européenne

### 🚀 Performance & Intégration

- **Traitement rapide** : Résultats en moins de 2 secondes pour la plupart des factures
- **Support PDF multi-pages** : Traitement automatique de toutes les pages
- **Cache intelligent** : Réponses instantanées pour fichiers déjà traités
- **Traitement par lot** : Jusqu'à 10 factures en une seule requête
- **Scores de confiance** : Score 0-1 pour chaque donnée extraite
- **Webhooks** : Intégrations directes Zapier, Make, Salesforce

---

## 📋 Endpoints disponibles

### Extraction OCR

- **`POST /ocr/upload`** : Upload fichier image/PDF → JSON structuré
- **`POST /ocr/base64`** : Traitement image encodée en base64
- **`POST /ocr/batch`** : Traitement par lot (jusqu'à 10 factures)

**Paramètres optionnels :**
- `language` : Code langue (fra, eng, deu, spa, ita, por) - Défaut: fra
- `check_compliance` : Activer validation conformité FR (bool) - Défaut: false

### Conformité française

- **`POST /compliance/check`** : Vérification complète conformité FR
- **`POST /compliance/validate-vat`** : Validation TVA uniquement
- **`POST /compliance/enrich-siret`** : Enrichissement données entreprise (SIRET)
- **`POST /compliance/validate-vies`** : Validation TVA intracommunautaire (VIES)

### Factur-X

- **`POST /facturx/generate`** : Génère XML Factur-X (EN16931) depuis données JSON
- **`POST /facturx/parse`** : Extrait XML Factur-X depuis PDF/A-3
- **`POST /facturx/parse-xml`** : Parse XML Factur-X et extrait données
- **`POST /facturx/validate`** : Valide XML Factur-X (structure + règles métier)

### Utilitaires

- **`GET /health`** : État de santé de l'API
- **`GET /languages`** : Liste des langues supportées

---

## 🎯 Cas d'usage

### 1. Automatisation comptable

Les cabinets comptables peuvent automatiser la saisie de factures :
- Upload PDF → Extraction automatique → Import dans logiciel comptable
- Validation automatique des mentions légales avant saisie
- Vérification TVA et calculs avant validation

### 2. Intégration ERP / Logiciels comptables

Les ERP (Sage, Cegid, EBP, Odoo, Dolibarr) peuvent :
- Importer automatiquement les factures fournisseurs
- Extraire les données structurées pour créer les écritures comptables
- Valider la conformité avant import

### 3. Facturation électronique

Les entreprises peuvent :
- Générer des factures Factur-X conformes EN16931
- Valider les factures reçues avant archivage
- Convertir leurs factures papier en format électronique

### 4. Marketplaces / E-commerce

Les plateformes peuvent :
- Traiter automatiquement les factures fournisseurs
- Extraire les données pour la gestion des commandes
- Valider la conformité avant paiement

### 5. SaaS facturation

Les applications SaaS (Sellsy, Pennylane, Axonaut) peuvent :
- Enrichir les données clients avec SIREN/SIRET
- Valider les factures avant émission
- Générer des Factur-X pour leurs clients

---

## 💡 Exemple d'utilisation

### Extraction OCR avec validation compliance

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -F "file=@facture.pdf" \
  -F "language=fra" \
  -F "check_compliance=true"
```

**Réponse :**
```json
{
  "success": true,
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
    ]
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
      "vat_rate": 20.0,
      "errors": [],
      "warnings": []
    },
    "siren_siret": {
      "siren": "479453193",
      "siret": "47945319300043"
    }
  }
}
```

### Génération Factur-X

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/facturx/generate" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "invoice_number": "FAC-2024-001",
      "date": "15/03/2024",
      "total_ht": 1042.08,
      "total_ttc": 1250.50,
      "tva": 208.42,
      "vendor": "Société Example SARL",
      "client": "Client ABC",
      "items": [...]
    }
  }'
```

**Réponse :**
```json
{
  "success": true,
  "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
  "format": "Factur-X EN16931"
}
```

---

## 🔧 Configuration requise

- **Clé API RapidAPI** : Obtenez votre clé après abonnement
- **Header d'authentification** : `X-RapidAPI-Proxy-Secret` (configuré dans RapidAPI)
- **Format fichiers** : JPEG, PNG, PDF (multi-pages supporté)
- **Taille maximale** : 10 Mo par défaut (configurable)

---

## 📊 Tarification

- **Basic (Gratuit)** : 100 requêtes/mois - Parfait pour tester
- **Pro** : 20 000 requêtes/mois - $15/mois - Pour petites entreprises
- **Ultra** : 80 000 requêtes/mois - $59/mois - Pour PME
- **Mega** : 250 000 requêtes/mois - $149/mois - Pour grandes entreprises

---

## 🌍 Support multi-langues

Optimisé pour le français, support également :
- Français (fra) - **Optimisé**
- Anglais (eng)
- Allemand (deu)
- Espagnol (spa)
- Italien (ita)
- Portugais (por)

---

## ✅ Conformité & Sécurité

- **RGPD compliant** : Données traitées conformément au RGPD
- **Sécurité** : Chiffrement en transit (HTTPS)
- **Cache** : Résultats mis en cache pour performance (24h)
- **Traçabilité** : Horodatage et empreinte des fichiers traités

---

## 🎮 Démo Interactive - Testez Maintenant !

**Aucun code requis !** Testez notre API instantanément avec notre interface web :

👉 **[🎯 Essayer la Démo](https://ocr-facture-api-production.up.railway.app/demo/)**

Fonctionnalités de la démo :
- Upload d'images ou PDF de factures
- Visualisation des résultats en temps réel
- Scores de confiance pour chaque champ
- Export JSON ou CSV
- Test de la validation de conformité FR

Il suffit d'entrer votre clé RapidAPI et de commencer à tester !

---

## 📚 Documentation complète

- **🎮 Démo Interactive** : `https://ocr-facture-api-production.up.railway.app/demo/`
- **Swagger UI** : `https://ocr-facture-api-production.up.railway.app/docs`
- **GitHub** : [https://github.com/RailsNft/OCR-Facture-API](https://github.com/RailsNft/OCR-Facture-API)
- **Support** : Via RapidAPI support

---

## 🚀 Démarrage rapide

1. **Tester la démo** : Visitez [https://ocr-facture-api-production.up.railway.app/demo/](https://ocr-facture-api-production.up.railway.app/demo/)
2. **S'abonner** à l'API sur RapidAPI
3. **Obtenir votre clé API** dans le dashboard
4. **Tester** avec le plan Basic (100 req/mois - gratuit)
5. **Intégrer** dans votre application

**Prêt à automatiser votre traitement de factures ?** Abonnez-vous maintenant et commencez à extraire des données en quelques minutes ! 🚀

---

## 🇬🇧 English description below

**This API extracts structured data from French and European invoices using OCR. Convert PDF invoices to JSON compliant with French legal requirements. Automatic detection of VAT, SIREN/SIRET, mandatory mentions. Optional Factur-X EN16931 generation.**
```

---

## 4️⃣ CATÉGORIE (Category)

### Catégorie principale (recommandée) :
```
Documents & OCR
```

### Catégorie secondaire (optionnelle) :
```
Finance & Accounting
```

**Note** : RapidAPI permet généralement une seule catégorie principale. Choisissez "Documents & OCR" pour moins de concurrence, ou "Finance & Accounting" si vous visez le marché financier (plus concurrentiel mais très recherché).

---

## 5️⃣ TAGS (Mots-clés)

### Tags recommandés (copier-coller) :
```
ocr
facture
facturx
tva
siren
siret
france
compliance
en16931
pdf
json
extraction
validation
comptabilité
accounting
invoice
e-invoicing
```

**Sélectionner les 8-10 plus pertinents** selon les limites de RapidAPI.

---

## 6️⃣ TUTORIEL (Tutorial Section)

### Contenu pour la section Tutorial de RapidAPI :

```markdown
# Tutoriel : Comment utiliser l'API OCR Facture France

## Introduction

Cette API permet d'extraire automatiquement les données structurées de vos factures françaises et européennes, avec validation de conformité et génération Factur-X optionnelle.

## Étape 1 : S'abonner à l'API

1. Allez sur RapidAPI et cherchez "OCR Facture France"
2. Cliquez sur "Subscribe"
3. Choisissez le plan Basic (100 requêtes/mois - gratuit) pour tester
4. Obtenez votre clé API dans le dashboard

## Étape 2 : Votre première extraction

### Avec cURL

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -F "file=@facture.pdf" \
  -F "language=fra" \
  -F "check_compliance=true"
```

### Avec Python

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

print(f"Numéro facture : {result['extracted_data']['invoice_number']}")
print(f"Total TTC : {result['extracted_data']['total_ttc']}€")
print(f"Conforme : {result['compliance']['compliance_check']['compliant']}")
```

## Étape 3 : Générer un Factur-X

Après extraction, générez un XML Factur-X :

```python
import requests

# 1. Extraire les données
extract_response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/ocr/upload",
    headers={"X-RapidAPI-Proxy-Secret": "votre-secret"},
    files={"file": open("facture.pdf", "rb")},
    data={"language": "fra"}
)

invoice_data = extract_response.json()["extracted_data"]

# 2. Générer Factur-X
facturx_response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/facturx/generate",
    headers={
        "X-RapidAPI-Proxy-Secret": "votre-secret",
        "Content-Type": "application/json"
    },
    json={"invoice_data": invoice_data}
)

xml_facturx = facturx_response.json()["xml"]
print(xml_facturx)
```

## Cas d'usage avancés

### Validation TVA uniquement

```python
validation_response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/compliance/validate-vat",
    headers={"X-RapidAPI-Proxy-Secret": "votre-secret"},
    json={"invoice_data": invoice_data}
)

if validation_response.json()["validation"]["valid"]:
    print("TVA valide ✅")
else:
    print("Erreurs TVA :", validation_response.json()["validation"]["errors"])
```

### Traitement par lot

```python
import base64

# Encoder plusieurs factures en base64
files_base64 = []
for pdf_file in ["facture1.pdf", "facture2.pdf", "facture3.pdf"]:
    with open(pdf_file, "rb") as f:
        files_base64.append(f"data:application/pdf;base64,{base64.b64encode(f.read()).decode()}")

batch_response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/ocr/batch",
    headers={
        "X-RapidAPI-Proxy-Secret": "votre-secret",
        "Content-Type": "application/json"
    },
    json={"files": files_base64, "language": "fra"}
)

print(f"Traitées : {batch_response.json()['total_processed']}")
print(f"Depuis cache : {batch_response.json()['total_cached']}")
```

## Conseils d'optimisation

1. **Utilisez le cache** : Les fichiers déjà traités sont servis instantanément
2. **Langue optimale** : Utilisez `fra` pour factures françaises
3. **Batch processing** : Pour plusieurs factures, utilisez `/ocr/batch`
4. **Compliance optionnelle** : Activez `check_compliance=true` seulement si nécessaire (légèrement plus lent)

## Support

- Documentation complète : `/docs` (Swagger UI)
- GitHub : https://github.com/RailsNft/OCR-Facture-API
- Support RapidAPI : Via le dashboard RapidAPI
```

---

## 📋 CHECKLIST PUBLICATION

### À copier dans RapidAPI Dashboard :

- [ ] **Titre** : `OCR Facture France – Extraction & Validation Factur-X (TVA, SIREN, mentions légales)`
- [ ] **Description courte** : Version courte ci-dessus
- [ ] **Description longue** : Version complète ci-dessus (section 3)
- [ ] **Catégorie** : `Documents & OCR` (ou `Finance & Accounting`)
- [ ] **Tags** : Sélectionner 8-10 tags de la liste ci-dessus
- [ ] **Tutoriel** : Contenu section Tutorial ci-dessus
- [ ] **Base URL** : `https://ocr-facture-api-production.up.railway.app`
- [ ] **Authentification** : `X-RapidAPI-Proxy-Secret` (déjà configuré)

---

## 🎯 OPTIMISATION SEO

### Mots-clés stratégiques inclus :

- ✅ `OCR facture France`
- ✅ `Factur-X`
- ✅ `TVA`
- ✅ `SIREN`
- ✅ `SIRET`
- ✅ `compliance`
- ✅ `EN16931`
- ✅ `facturation électronique`
- ✅ `extraction PDF`
- ✅ `validation facture`

---

**Tout est prêt pour publication sur RapidAPI !** 🚀

Copiez-collez chaque section dans le dashboard RapidAPI lors de la publication.

