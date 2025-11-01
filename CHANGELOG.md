# Changelog - OCR Facture API

## Version 1.2.0 (Novembre 2024)

### 🎉 Nouvelles fonctionnalités majeures

#### ✅ Détection des tableaux structurés
- **Détection automatique** des tableaux dans les factures
- **Colonnes détectées automatiquement** (jusqu'à 5 colonnes)
- Support de différents séparateurs : `|`, espaces multiples, tabulations
- Extraction des lignes de données avec mapping par colonne
- Détection intelligente des headers de tableaux

**Exemple de réponse :**
```json
{
  "tables": [
    {
      "header": ["Description", "Quantité", "Prix unitaire", "Total"],
      "rows": [
        {"Description": "Consultation", "Quantité": "1", "Prix unitaire": "500.00", "Total": "500.00"}
      ],
      "row_count": 1
    }
  ]
}
```

#### ✅ Extraction des coordonnées bancaires
- **IBAN** : Détection du format standard (15-34 caractères)
- **SWIFT/BIC** : Codes bancaires internationaux (8 ou 11 caractères)
- **RIB** : Relevé d'Identité Bancaire français (23 chiffres)
- **Numéro de compte** : Extraction automatique
- **Nom de la banque** : Détection contextuelle

**Exemple de réponse :**
```json
{
  "banking_info": {
    "iban": "FR7612345678901234567890123",
    "swift": "ABCDEFGH",
    "bic": "ABCDEFGH",
    "rib": "12345123451234567890123",
    "account_number": "123456789012",
    "bank_name": "Banque Example"
  }
}
```

#### ✅ Traitement par lot (Batch Processing)
- **Nouveau endpoint** `/ocr/batch`
- Traiter jusqu'à **10 factures en une seule requête**
- Toutes les fonctionnalités disponibles (OCR, extraction, scores)
- Utilise le cache automatiquement pour optimiser les performances
- Compteur de résultats cachés vs traités

**Exemple d'utilisation :**
```json
POST /ocr/batch
{
  "files": ["base64_image1", "base64_image2"],
  "language": "fra"
}
```

#### ✅ Cache des résultats
- **Cache automatique** basé sur le hash SHA256 du fichier
- **TTL de 24 heures** pour chaque résultat
- **Limite de 1000 entrées** avec éviction automatique des plus anciens
- **Indicateur `cached`** dans la réponse pour savoir si le résultat vient du cache
- **Réponse instantanée** pour les fichiers déjà traités

**Bénéfices :**
- ⚡ Réponse beaucoup plus rapide (pas de re-traitement OCR)
- 💰 Économie de ressources serveur
- 📊 Meilleure expérience utilisateur

#### ✅ Intégrations directes (Webhooks)
- **Zapier** : `/webhooks/zapier` - Format compatible Zapier
- **Make (Integromat)** : `/webhooks/make` - Format compatible Make
- **Salesforce** : `/webhooks/salesforce` - Format Salesforce Invoice object

**Format Zapier :**
```json
{
  "invoice_id": "abc123...",
  "invoice_data": {...},
  "timestamp": "2024-11-01T12:00:00",
  "source": "ocr_facture_api"
}
```

**Format Salesforce :**
```json
{
  "InvoiceNumber": "FAC-2024-001",
  "TotalAmount": 1250.50,
  "InvoiceDate": "15/03/2024",
  "VendorName": "Société Example",
  "CustomerName": "Client ABC",
  "Items": [...],
  "BankingInfo": {...},
  "ConfidenceScores": {...}
}
```

### 🔧 Améliorations techniques

- **Performance** : Cache réduit drastiquement le temps de réponse
- **Robustesse** : Gestion d'erreurs améliorée pour batch processing
- **Scalabilité** : Prêt pour de gros volumes avec le cache
- **Intégration** : Webhooks prêts pour automatisation

### 📊 Amélioration des performances

- **Cache** : Réponse instantanée pour fichiers déjà traités
- **Batch** : Traitement optimisé de plusieurs fichiers
- **Tableaux** : Extraction structurée améliorée

### 🔄 Changements de compatibilité

- **Réponse API enrichie** : Nouveaux champs `tables` et `banking_info`
- **Nouveau champ `cached`** : Indique si le résultat vient du cache
- **Format compatible** : Les anciennes intégrations continuent de fonctionner

---

## Version 1.1.0 (Novembre 2024)

### 🎉 Nouvelles fonctionnalités

#### ✅ Extraction des lignes de facture (Items)
- **Détection automatique** des articles/lignes de facture
- Extraction de :
  - Description de l'article
  - Quantité
  - Prix unitaire
  - Total par ligne
- Détection intelligente de la section items (entre headers et totaux)
- Support de différents formats de tableaux

**Exemple de réponse :**
```json
{
  "items": [
    {
      "description": "Consultation technique",
      "quantity": 1.0,
      "unit_price": 500.00,
      "total": 500.00
    },
    {
      "description": "Installation système",
      "quantity": 1.0,
      "unit_price": 350.00,
      "total": 350.00
    }
  ]
}
```

#### ✅ Scores de confiance
- **Score de confiance (0-1)** pour chaque donnée extraite
- Permet aux utilisateurs de savoir la fiabilité des données
- Score calculé selon :
  - Nombre de patterns trouvés
  - Qualité du contexte
  - Validité de la valeur

**Exemple de réponse :**
```json
{
  "confidence_scores": {
    "total": 0.95,
    "total_ht": 0.90,
    "total_ttc": 0.92,
    "tva": 0.91,
    "date": 0.95,
    "invoice_number": 0.88,
    "vendor": 0.85,
    "client": 0.85,
    "items": 0.90
  }
}
```

#### ✅ Détection améliorée du numéro de facture
- **Patterns améliorés** pour détecter plus de formats
- Recherche dans les premières lignes (où se trouve généralement le numéro)
- Support de formats variés :
  - FAC-2024-001
  - FAC2024001
  - INV-2024
  - Références personnalisées
- Validation de la longueur et format

#### ✅ Support PDF multi-pages
- **Traitement de tous les PDFs** (1 page ou plusieurs)
- Conversion PDF → Images page par page
- OCR sur chaque page
- **Fusion automatique** des résultats de toutes les pages
- Indication du nombre de pages traitées

**Nouveau dans la réponse :**
```json
{
  "data": {
    "text": "--- Page 1 ---\n...\n\n--- Page 2 ---\n...",
    "language": "fra",
    "pages_processed": 2
  }
}
```

### 🔧 Améliorations techniques

- **Performance** : Optimisation de la détection des patterns
- **Précision** : Meilleure extraction grâce aux scores de confiance
- **Robustesse** : Gestion d'erreurs améliorée
- **Documentation** : Mise à jour avec les nouvelles fonctionnalités

### 📦 Dépendances ajoutées

- `pdf2image>=1.16.3` - Support PDF via pdf2image
- `pymupdf>=1.23.0` - Support PDF via PyMuPDF (plus rapide)
- `poppler-utils` - Outil système pour pdf2image (dans Dockerfile)

### 🔄 Changements de compatibilité

- **Réponse API enrichie** : Nouveau champ `confidence_scores`
- **Items maintenant remplis** : `items` n'est plus vide par défaut
- **Format compatible** : Les anciennes intégrations continuent de fonctionner

### 📊 Amélioration des performances

- Détection plus rapide grâce aux patterns optimisés
- Cache des résultats OCR (à venir dans v1.2)
- Traitement parallèle des pages PDF (à venir)

---

## Version 1.0.0 (Octobre 2024)

### Fonctionnalités initiales

- Extraction de texte via OCR
- Détection des montants (HT, TTC, TVA)
- Extraction des dates
- Détection du numéro de facture (basique)
- Identification vendeur/client
- Support 6 langues
- Authentification RapidAPI

---

## Notes de migration

### Pour les utilisateurs existants

Toutes les améliorations sont **rétrocompatibles**. Votre code existant continuera de fonctionner.

**Nouveaux champs disponibles (optionnels) :**
- `confidence_scores` - Scores de confiance pour chaque donnée
- `items` - Lignes de facture détaillées
- `pages_processed` - Nombre de pages (pour PDFs)

Vous pouvez utiliser ces nouveaux champs pour améliorer votre application !

