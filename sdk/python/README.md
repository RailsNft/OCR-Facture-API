# OCR Facture API - SDK Python

SDK Python officiel pour l'API OCR Facture France. Facilite l'intégration de l'extraction automatique de données de factures dans vos applications Python.

## 🚀 Installation

```bash
pip install ocr-facture-api
```

## 📖 Utilisation

### Configuration de base

```python
from ocr_facture_api import OCRFactureAPI

# Initialiser le client
api = OCRFactureAPI(
    api_key="votre_cle_api_rapidapi",
    base_url="https://ocr-facture-api-production.up.railway.app"  # Optionnel
)
```

### Extraire les données d'une facture

#### Depuis un fichier

```python
# Depuis un fichier local
result = api.extract_from_file("facture.pdf", language="fra")

# Accéder aux données extraites
invoice_data = result["extracted_data"]
print(f"Numéro de facture: {invoice_data['invoice_number']}")
print(f"Total TTC: {invoice_data['total_ttc']}€")
print(f"Date: {invoice_data['date']}")

# Scores de confiance
confidence = result["confidence_scores"]
print(f"Confiance numéro: {confidence['invoice_number']}")
```

#### Depuis une image base64

```python
import base64

with open("facture.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

result = api.extract_from_base64(image_data, language="fra")
```

### Traitement par lot (batch)

```python
# Traiter plusieurs factures en une requête
files = ["facture1.pdf", "facture2.pdf", "facture3.pdf"]
batch_result = api.batch_extract(files, language="fra")

# Parcourir les résultats
for i, result in enumerate(batch_result["results"]):
    if result["success"]:
        print(f"Facture {i+1}: {result['extracted_data']['invoice_number']}")
```

### Validation de conformité FR

```python
# Extraire puis valider
result = api.extract_from_file("facture.pdf", check_compliance=True)

# Ou valider séparément
invoice_data = result["extracted_data"]
compliance = api.check_compliance(invoice_data)

if compliance["compliance"]["compliant"]:
    print("✅ Facture conforme")
else:
    print(f"❌ Champs manquants: {compliance['compliance']['missing_fields']}")
```

### Génération Factur-X

```python
# Extraire les données
result = api.extract_from_file("facture.pdf")
invoice_data = result["extracted_data"]

# Générer XML Factur-X
facturx_result = api.generate_facturx(invoice_data)
xml_content = facturx_result["xml"]

# Sauvegarder le XML
with open("facture_facturx.xml", "w", encoding="utf-8") as f:
    f.write(xml_content)
```

### Validation TVA

```python
invoice_data = result["extracted_data"]
vat_validation = api.validate_vat(invoice_data)

if vat_validation["validation"]["valid"]:
    print("✅ TVA valide")
else:
    print(f"❌ Erreurs: {vat_validation['validation']['errors']}")
```

### Enrichissement SIRET

```python
# Enrichir avec API Sirene
enrichment = api.enrich_siret("12345678901234")
print(f"Raison sociale: {enrichment['enrichment']['uniteLegale']['denominationUniteLegale']}")
```

### Gestion des erreurs

```python
from ocr_facture_api import (
    OCRFactureAPIError,
    OCRFactureAuthError,
    OCRFactureRateLimitError,
    OCRFactureValidationError,
)

try:
    result = api.extract_from_file("facture.pdf")
except OCRFactureAuthError:
    print("❌ Clé API invalide")
except OCRFactureRateLimitError as e:
    print(f"❌ Quota dépassé. Réessayez dans {e.retry_after} secondes")
except OCRFactureValidationError as e:
    print(f"❌ Erreur de validation: {e.message}")
except OCRFactureAPIError as e:
    print(f"❌ Erreur API: {e.message}")
```

### Idempotence

```python
import uuid

# Utiliser une clé d'idempotence pour éviter les doublons
idempotency_key = str(uuid.uuid4())
result = api.extract_from_file(
    "facture.pdf",
    idempotency_key=idempotency_key
)

# Réutiliser la même clé retourne le même résultat sans retraitement
result2 = api.extract_from_file(
    "facture.pdf",
    idempotency_key=idempotency_key
)  # Résultat instantané depuis le cache
```

## 📚 API Reference

### Méthodes principales

- `extract_from_file(file_path, language="fra", check_compliance=False, idempotency_key=None)` - Extraction depuis fichier
- `extract_from_base64(base64_string, language="fra", check_compliance=False, idempotency_key=None)` - Extraction depuis base64
- `batch_extract(files, language="fra", idempotency_key=None)` - Traitement par lot (max 10 fichiers)
- `check_compliance(invoice_data)` - Validation conformité FR
- `validate_vat(invoice_data)` - Validation TVA
- `enrich_siret(siret)` - Enrichissement SIRET
- `validate_vies(vat_number)` - Validation VIES
- `generate_facturx(invoice_data)` - Génération XML Factur-X
- `parse_facturx(file_path)` - Extraction XML depuis PDF/A-3
- `validate_facturx_xml(xml_content)` - Validation XML Factur-X
- `get_supported_languages()` - Liste des langues supportées
- `get_quota()` - Informations sur quota restant
- `health_check()` - État de santé de l'API

## 🌍 Langues supportées

- `fra` - Français (défaut)
- `eng` - Anglais
- `deu` - Allemand
- `spa` - Espagnol
- `ita` - Italien
- `por` - Portugais

## 📝 Exemples complets

### Exemple 1 : Traitement automatique de factures

```python
from ocr_facture_api import OCRFactureAPI
import os

api = OCRFactureAPI(api_key=os.getenv("OCR_FACTURE_API_KEY"))

# Traiter toutes les factures d'un dossier
factures_dir = "./factures"
for filename in os.listdir(factures_dir):
    if filename.endswith(('.pdf', '.jpg', '.png')):
        filepath = os.path.join(factures_dir, filename)
        try:
            result = api.extract_from_file(filepath, check_compliance=True)
            
            invoice_data = result["extracted_data"]
            print(f"\n📄 {filename}")
            print(f"  Numéro: {invoice_data.get('invoice_number')}")
            print(f"  Date: {invoice_data.get('date')}")
            print(f"  Total TTC: {invoice_data.get('total_ttc')}€")
            
            # Vérifier conformité
            if result.get("compliance", {}).get("compliant"):
                print("  ✅ Conforme")
            else:
                print(f"  ⚠️ Non conforme: {result['compliance']['missing_fields']}")
                
        except Exception as e:
            print(f"❌ Erreur pour {filename}: {e}")
```

### Exemple 2 : Export vers CSV

```python
import csv
from ocr_facture_api import OCRFactureAPI

api = OCRFactureAPI(api_key="votre_cle")

# Traiter plusieurs factures
files = ["facture1.pdf", "facture2.pdf", "facture3.pdf"]
batch_result = api.batch_extract(files)

# Exporter vers CSV
with open("factures_export.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Numéro", "Date", "Vendeur", "Total TTC", "Confiance"])
    
    for result in batch_result["results"]:
        if result["success"]:
            data = result["extracted_data"]
            writer.writerow([
                data.get("invoice_number"),
                data.get("date"),
                data.get("vendor"),
                data.get("total_ttc"),
                result["confidence_scores"].get("total_ttc", 0)
            ])
```

## 🔗 Liens utiles

- [Documentation API complète](https://github.com/RailsNft/OCR-Facture-API)
- [RapidAPI Marketplace](https://rapidapi.com/)
- [Issues GitHub](https://github.com/RailsNft/OCR-Facture-API/issues)

## 📄 Licence

MIT License

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.





