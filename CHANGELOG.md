# Changelog - OCR Facture API

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

