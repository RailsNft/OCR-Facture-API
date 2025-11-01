# Changelog Version 2.0.0 - Factur-X & Compliance FR

## 🎉 Version majeure - Factur-X et Compliance française

### ✨ Nouvelles fonctionnalités

#### 🇫🇷 Compliance française

**Module `compliance.py`** - Vérification complète de conformité pour factures françaises

1. **Détection SIREN/SIRET**
   - Détection automatique dans le texte OCR
   - Support formats : SIRET (14 chiffres), SIREN (9 chiffres)
   - Extraction depuis les patterns "SIRET:", "SIREN:", ou numéros bruts

2. **Détection TVA intracommunautaire**
   - Détection format FR (FR + 2 lettres + 9 chiffres)
   - Support formats généraux UE

3. **Vérification compliance FR**
   - Vérification mentions légales obligatoires :
     - Date d'émission
     - Numéro de facture
     - Montants HT, TTC, TVA
     - Nom vendeur/client
     - Adresse complète
   - Score de conformité (0-100)
   - Liste des champs manquants
   - Avertissements

4. **Validation TVA FR**
   - Vérification taux valides (20%, 10%, 5.5%, 2.1%, 0%)
   - Validation calculs : HT + TVA = TTC
   - Détection incohérences
   - Messages d'erreur détaillés

5. **Enrichissement SIREN/SIRET**
   - Structure prête pour intégration API Sirene (Insee)
   - Nécessite `SIRENE_API_KEY` et `SIRENE_API_SECRET` dans `.env`

6. **Validation VIES**
   - Validation TVA intracommunautaire via API européenne
   - Récupération nom entreprise et adresse
   - Support SOAP via `zeep`

**Nouveaux endpoints :**
- `POST /compliance/check` - Vérification complète
- `POST /compliance/validate-vat` - Validation TVA uniquement
- `POST /compliance/enrich-siret` - Enrichissement SIRET
- `POST /compliance/validate-vies` - Validation VIES

**Intégration dans OCR :**
- Paramètre `check_compliance` dans `/ocr/upload` (optionnel, False par défaut)
- Retourne `compliance` dans la réponse si activé

---

#### 📄 Factur-X (EN16931)

**Module `facturx.py`** - Support complet Factur-X / ZUGFeRD 2.1.1

1. **Générateur XML Factur-X**
   - Génération XML conforme EN16931
   - Structure complète :
     - En-tête (numéro, date, type)
     - Vendeur (nom, adresse)
     - Client (nom, adresse)
     - Montants (HT, TTC, TVA)
     - Lignes de facture (items)
   - Namespaces XML corrects
   - Format conforme standard européen

2. **Parseur Factur-X**
   - Extraction XML depuis PDF/A-3
   - Parsing XML et extraction données structurées
   - Support PDF avec XML embarqué
   - Fallback sur recherche pattern dans PDF brut

3. **Validateur Factur-X**
   - Validation structure XML
   - Vérification champs obligatoires :
     - Numéro de facture
     - Date d'émission
     - Vendeur et client
     - Montants totaux
   - Vérification cohérence montants (HT + TVA = TTC)
   - Rapport lisible avec erreurs et avertissements

**Nouveaux endpoints :**
- `POST /facturx/generate` - Génère XML Factur-X depuis données JSON
- `POST /facturx/parse` - Extrait XML depuis PDF/A-3
- `POST /facturx/parse-xml` - Parse XML Factur-X et extrait données
- `POST /facturx/validate` - Valide XML Factur-X

---

### 📦 Nouvelles dépendances

- `lxml>=4.9.0` - Manipulation XML avancée
- `zeep>=4.2.0` - Client SOAP pour API VIES
- `reportlab>=4.0.0` - Génération PDF (préparé pour future fonctionnalité)

---

### 🔧 Configuration

**Nouvelles variables d'environnement (.env) :**
```env
# Optionnel : pour enrichissement SIREN/SIRET
SIRENE_API_KEY=votre_cle_api
SIRENE_API_SECRET=votre_secret_api
```

---

### 📊 Endpoints mis à jour

- `/ocr/upload` - Nouveau paramètre `check_compliance` (bool, optionnel)
- `/` - Liste des fonctionnalités mise à jour avec nouvelles features

---

### 🎯 Workflow complet

**Scénario 1 : OCR + Compliance**
```bash
POST /ocr/upload
{
  "file": "facture.pdf",
  "language": "fra",
  "check_compliance": true
}
# Retourne : extracted_data + compliance (SIREN/SIRET, TVA validation, etc.)
```

**Scénario 2 : OCR → Factur-X**
```bash
# 1. Extraire données
POST /ocr/upload → invoice_data

# 2. Générer XML Factur-X
POST /facturx/generate
{
  "invoice_data": {...}
}
# Retourne : XML Factur-X conforme EN16931
```

**Scénario 3 : PDF Factur-X → Données**
```bash
# 1. Parser PDF Factur-X
POST /facturx/parse
{
  "file": "facture_facturx.pdf"
}
# Retourne : XML + invoice_data

# 2. Valider XML
POST /facturx/validate
{
  "xml_content": "..."
}
# Retourne : validation report
```

---

### 🚀 Migration depuis v1.x

**Aucun breaking change** - Toutes les fonctionnalités existantes fonctionnent comme avant.

**Nouvelles fonctionnalités sont optionnelles** :
- `check_compliance` est `False` par défaut
- Nouveaux endpoints sont indépendants

---

### 📝 Notes techniques

**Factur-X :**
- Implémentation conforme EN16931 (profil basic)
- Support namespaces XML standards
- Structure XML complète avec tous les éléments obligatoires

**Compliance FR :**
- Détection regex robuste pour SIREN/SIRET
- Validation TVA avec tolérance d'arrondi (0.01€)
- API VIES fonctionnelle (SOAP)

**Améliorations futures possibles :**
- Validation XSD complète (schémas EN16931 volumineux)
- Génération PDF/A-3 avec XML embarqué
- Conversion Factur-X ↔ UBL (Peppol)
- Intégration complète API Sirene (OAuth2)

---

### ✅ Tests recommandés

1. **Compliance FR :**
   - Tester avec facture complète → `check_compliance=true`
   - Tester validation TVA avec différents taux
   - Tester validation VIES avec numéro réel

2. **Factur-X :**
   - Générer XML depuis données OCR
   - Parser PDF Factur-X réel
   - Valider XML généré

---

**Version 2.0.0** - API maintenant complètement "compliance-ready" avec Factur-X ! 🎉

