# 🔍 État actuel : Factur-X / Peppol BIS 3 - Analyse de l'API

## ❌ RÉPONSE BRUTE : Ces fonctionnalités ne sont PAS implémentées

---

## 📊 Analyse détaillée par besoin

### 1️⃣ Factur-X / Peppol BIS 3 (EU e-invoicing)

#### ❌ **PAS IMPLÉMENTÉ**

#### Ce qui manque :

#### A. **Parseur Factur-X** ❌
- **Besoin** : Lire un PDF/A-3 avec XML Factur-X embarqué et extraire les données
- **État actuel** : L'API lit seulement le texte via OCR, pas le XML embarqué
- **Ce qu'il faut** :
  - Parser le PDF/A-3 pour extraire le XML Factur-X
  - Valider le schéma XML (XSD EN16931)
  - Extraire les données structurées du XML

#### B. **Générateur Factur-X** ❌
- **Besoin** : Convertir les données JSON extraites → XML Factur-X (profil EN16931)
- **État actuel** : L'API retourne seulement du JSON
- **Ce qu'il faut** :
  - Générer un XML conforme au schéma EN16931
  - Créer un PDF/A-3 avec XML embarqué
  - Valider le XML généré

#### C. **Validateur Factur-X** ❌
- **Besoin** : Valider un XML Factur-X et retourner un rapport lisible
- **État actuel** : Aucune validation
- **Ce qu'il faut** :
  - Valider contre le schéma XSD EN16931
  - Vérifier les règles métier (dates, montants, TVA)
  - Générer un rapport d'erreurs/warnings détaillé

#### D. **Conversion Factur-X ↔ UBL (Peppol)** ❌
- **Besoin** : Convertir Factur-X → UBL (Peppol BIS 3) et vice-versa
- **État actuel** : Aucune conversion
- **Ce qu'il faut** :
  - Mapping des champs Factur-X vers UBL
  - Mapping des champs UBL vers Factur-X
  - Gestion des différences de structure

#### E. **Webhook d'échec avec motif** ⚠️ PARTIEL
- **Besoin** : Envoyer un webhook si la validation/conversion échoue avec le motif d'erreur
- **État actuel** : Webhooks existent mais seulement pour succès
- **Ce qu'il faut** :
  - Détecter les erreurs de validation
  - Formater le motif d'erreur
  - Envoyer le webhook avec les détails

---

### 2️⃣ OCR facture FR "compliance-ready" (TVA, mentions légales)

#### ❌ **PARTIELLEMENT IMPLÉMENTÉ**

#### Ce qui est fait ✅ :
- Extraction des montants HT, TTC, TVA
- Extraction des dates
- Extraction du numéro de facture
- Extraction vendeur/client
- Extraction coordonnées bancaires (IBAN, SWIFT, RIB)

#### Ce qui manque ❌ :

#### A. **Vérification conformité FR (mentions légales)** ❌
- **Besoin** : Vérifier que la facture contient toutes les mentions obligatoires FR
- **État actuel** : Aucune vérification
- **Mentions obligatoires à vérifier** :
  - Numéro SIRET/SIREN du vendeur
  - Numéro SIRET/SIREN du client (si B2B)
  - Adresse complète du vendeur
  - Adresse complète du client
  - Date d'émission
  - Date d'échéance
  - Numéro de facture unique
  - Montant HT, TTC, TVA
  - Conditions de paiement
  - Mentions légales (SARL, SAS, etc.)
  - Numéro TVA intracommunautaire (si applicable)

#### B. **Vérification TVA FR** ❌
- **Besoin** : Vérifier que les taux de TVA sont conformes (20%, 10%, 5.5%, 2.1%, etc.)
- **État actuel** : Extraction de la TVA mais pas de validation
- **Ce qu'il faut** :
  - Vérifier que le taux est valide pour la France
  - Vérifier que le calcul HT × taux = TVA (avec arrondis)
  - Vérifier que HT + TVA = TTC

#### C. **Enrichissement SIREN/SIRET** ❌
- **Besoin** : Détecter un SIREN/SIRET dans la facture et enrichir avec les données de l'API Sirene
- **État actuel** : Aucune détection ni enrichissement
- **Ce qu'il faut** :
  - Détecter les numéros SIREN/SIRET dans le texte OCR
  - Appeler l'API Sirene (api.insee.fr) pour enrichir
  - Retourner : raison sociale, adresse, forme juridique, date création, etc.

#### D. **Enrichissement VIES (TVA intracom)** ❌
- **Besoin** : Vérifier un numéro TVA intracommunautaire via VIES
- **État actuel** : Aucune vérification
- **Ce qu'il faut** :
  - Détecter les numéros TVA intracom (format FR + 11 chiffres)
  - Appeler l'API VIES (ec.europa.eu) pour valider
  - Retourner : valide/invalide, nom de l'entreprise

#### E. **Génération PDF Factur-X optionnel** ❌
- **Besoin** : Option pour générer un PDF/A-3 avec XML Factur-X embarqué
- **État actuel** : Aucune génération de PDF
- **Ce qu'il faut** :
  - Créer un PDF/A-3 depuis les données extraites
  - Embédder le XML Factur-X
  - Retourner le PDF en téléchargement

---

## 📋 Comparaison : Ce qui existe vs Ce qui manque

| Fonctionnalité | État actuel | Nécessaire pour compliance |
|----------------|-------------|----------------------------|
| **OCR extraction** | ✅ Implémenté | ✅ |
| **Extraction montants (HT/TTC/TVA)** | ✅ Implémenté | ✅ |
| **Extraction dates** | ✅ Implémenté | ✅ |
| **Extraction numéro facture** | ✅ Implémenté | ✅ |
| **Extraction vendeur/client** | ✅ Implémenté | ✅ |
| **Extraction coordonnées bancaires** | ✅ Implémenté | ⚠️ Partiel |
| **Parseur Factur-X** | ❌ Manquant | ❌ **CRITIQUE** |
| **Générateur Factur-X** | ❌ Manquant | ❌ **CRITIQUE** |
| **Validateur Factur-X** | ❌ Manquant | ❌ **CRITIQUE** |
| **Conversion Factur-X ↔ UBL** | ❌ Manquant | ❌ **CRITIQUE** |
| **Vérification mentions légales FR** | ❌ Manquant | ❌ **CRITIQUE** |
| **Vérification TVA FR** | ❌ Manquant | ❌ **CRITIQUE** |
| **Enrichissement SIREN/SIRET** | ❌ Manquant | ⚠️ **Important** |
| **Enrichissement VIES** | ❌ Manquant | ⚠️ **Important** |
| **Génération PDF Factur-X** | ❌ Manquant | ⚠️ **Important** |
| **Webhook échec avec motif** | ⚠️ Partiel | ⚠️ **Important** |

---

## 🎯 Impact sur votre positionnement

### ⚠️ **PROBLÈME MAJEUR**

Votre documentation mentionne "Factur-X" dans :
- Le nom de l'API : `OCR Facture FR → JSON + Factur-X`
- La description : "Convert PDF invoices to JSON and Factur-X XML (EN16931)"
- Les tags : `facturx`

**MAIS** : Ces fonctionnalités ne sont **PAS implémentées** dans le code !

### 📊 Conséquences :

1. **Promesses non tenues** ❌
   - Les utilisateurs s'attendent à recevoir du XML Factur-X
   - Actuellement, ils reçoivent seulement du JSON

2. **Conformité non vérifiée** ❌
   - Pas de vérification des mentions légales FR
   - Pas de validation TVA
   - Pas de conformité Factur-X

3. **Opportunité manquée** ❌
   - Le marché cherche spécifiquement des APIs Factur-X
   - Vous êtes mentionné comme solution mais ne livrez pas

---

## 🚀 Ce qu'il faut implémenter pour être "compliance-ready"

### 🔴 Priorité CRITIQUE (pour Factur-X)

#### 1. **Générateur Factur-X** (EN16931)
```python
# Nouveau endpoint
POST /facturx/generate
{
    "invoice_data": {...},  # Données extraites par OCR
    "output_format": "xml" | "pdf"
}

# Retourne :
- XML Factur-X conforme EN16931
- OU PDF/A-3 avec XML embarqué
```

**Technologies nécessaires** :
- Bibliothèque Python pour générer XML Factur-X
- `factur-x` ou `pyfactur-x` (à vérifier si existe)
- Sinon, génération manuelle du XML selon schéma EN16931

#### 2. **Parseur Factur-X**
```python
# Nouveau endpoint
POST /facturx/parse
{
    "file": <PDF/A-3 avec XML embarqué>
}

# Retourne :
- Données extraites du XML Factur-X
- Validation du schéma
```

**Technologies nécessaires** :
- `pypdf` ou `PyPDF2` pour extraire le XML du PDF
- `lxml` pour parser et valider le XML
- Schémas XSD EN16931

#### 3. **Validateur Factur-X**
```python
# Nouveau endpoint
POST /facturx/validate
{
    "xml": "<XML Factur-X>"
}

# Retourne :
{
    "valid": true/false,
    "errors": [...],
    "warnings": [...],
    "report": "Rapport lisible"
}
```

**Technologies nécessaires** :
- `lxml` pour validation XSD
- Règles métier à implémenter manuellement

#### 4. **Conversion Factur-X ↔ UBL (Peppol)**
```python
# Nouveau endpoint
POST /convert/facturx-to-ubl
POST /convert/ubl-to-facturx
```

**Technologies nécessaires** :
- Mapping manuel des champs (complexe)
- Bibliothèques UBL si disponibles

---

### 🟡 Priorité HAUTE (pour compliance FR)

#### écrire une fonction pour vérifier les mentions légales
```python
def check_french_compliance(extracted_data):
    """
    Vérifie que la facture contient toutes les mentions obligatoires FR
    """
    missing_fields = []
    
    # Vérifier SIRET/SIREN vendeur
    if not has_siret(extracted_data.get("vendor")):
        missing_fields.append("SIRET/SIREN vendeur")
    
    # Vérifier adresse complète
    if not has_complete_address(extracted_data.get("vendor")):
        missing_fields.append("Adresse complète vendeur")
    
    # Vérifier date d'émission
    if not extracted_data.get("date"):
        missing_fields.append("Date d'émission")
    
    # ... etc
    
    return {
        "compliant": len(missing_fields) == 0,
        "missing_fields": missing_fields,
        "score": calculate_compliance_score(extracted_data)
    }
```

#### Vérification TVA FR
```python
def validate_french_vat(extracted_data):
    """
    Vérifie que les taux de TVA sont conformes
    """
    valid_rates = [20.0, 10.0, 5.5, 2.1, 0.0]  # Taux FR
    
    tva_rate = calculate_vat_rate(
        extracted_data.get("total_ht"),
        extracted_data.get("tva")
    )
    
    if tva_rate not in valid_rates:
        return {
            "valid": False,
            "error": f"Taux TVA {tva_rate}% non valide pour la France"
        }
    
    # Vérifier le calcul
    expected_tva = extracted_data.get("total_ht") * (tva_rate / 100)
    if abs(expected_tva - extracted_data.get("tva")) > 0.01:
        return {
            "valid": False,
            "error": "Calcul TVA incorrect"
        }
    
    return {"valid": True}
```

#### Enrichissement SIREN/SIRET
```python
# Nouveau endpoint
POST /enrich/siren
{
    "siret": "47945319300043"
}

# Appelle l'API Sirene
# Retourne : raison sociale, adresse, forme juridique, etc.
```

**Technologies nécessaires** :
- `requests` pour appeler l'API Sirene (api.insee.fr)
- Clé API Insee (gratuite mais nécessite inscription)

#### Enrichissement VIES
```python
# Nouveau endpoint
POST /enrich/vies
{
    "vat_number": "FR47945319300"
}

# Appelle l'API VIES (ec.europa.eu)
# Retourne : valide/invalide, nom entreprise
```

**Technologies nécessaires** :
- `requests` pour appeler l'API VIES
- Gestion du SOAP (VIES utilise SOAP)

---

## 📦 Bibliothèques Python nécessaires

```txt
# Ajouter à requirements.txt

# Pour Factur-X
lxml>=4.9.0  # Parser et valider XML
xmlschema>=2.0.0  # Validation XSD
reportlab>=4.0.0  # Génération PDF
pypdf>=3.0.0  # Manipulation PDF/A-3

# Pour API Sirene
requests>=2.31.0  # Appels API
requests-oauthlib>=1.3.0  # Authentification OAuth pour Sirene

# Pour API VIES
zeep>=4.2.0  # Client SOAP pour VIES
```

---

## 🎯 Plan d'implémentation recommandé

### Phase 1 : Compliance FR (2-3 semaines)
1. ✅ Vérification mentions légales
2. ✅ Validation TVA FR
3. ✅ Enrichissement SIREN/SIRET
4. ✅ Enrichissement VIES

### Phase 2 : Factur-X de base (3-4 semaines)
1. ✅ Générateur XML Factur-X
2. ✅ Parseur Factur-X
3. ✅ Validateur Factur-X basique

### Phase 3 : Factur-X avancé (2-3 semaines)
1. ✅ Génération PDF/A-3 avec XML embarqué
 onversion Factur-X ↔ UBL
2. ✅ Webhook d'échec avec motif

---

## 💡 Recommandation immédiate

### Option 1 : Implémenter rapidement (recommandé)
- Commencer par la **compliance FR** (plus simple)
- Ajouter ensuite **Factur-X** progressivement
- Mettre à jour la documentation pour refléter ce qui est disponible

### Option 2 : Ajuster le marketing
- Retirer les mentions "Factur-X" jusqu'à implémentation
- Se concentrer sur "OCR facture FR → JSON"
- Ajouter Factur-X comme "feature à venir"

### Option 3 : Partenariat
- S'intégrer avec une API Factur-X existante
- Focus sur OCR + extraction
- Déléguer Factur-X à un partenaire

---

## 📝 Résumé

| Besoin | État | Action requise |
|--------|------|----------------|
| **Factur-X parseur** | ❌ Non | Implémenter parsing XML embarqué |
| **Factur-X générateur** | ❌ Non | Implémenter génération XML EN16931 |
| **Factur-X validateur** | ❌ Non | Implémenter validation XSD + règles métier |
| **Conversion Factur-X ↔ UBL** | ❌ Non | Implémenter mapping complexe |
| **Compliance FR (mentions)** | ❌ Non | Implémenter vérification |
| **Validation TVA FR** | ❌ Non | Implémenter validation taux |
| **Enrichissement SIREN/SIRET** | ❌ Non | Intégrer API Sirene |
| **Enrichissement VIES** | ❌ Non | Intégrer API VIES |
| **Génération PDF Factur-X** | ❌ Non | Implémenter génération PDF/A-3 |

**Conclusion** : Ces fonctionnalités représentent **2-3 mois de développement** pour être complètement "compliance-ready" avec Factur-X et Peppol.

