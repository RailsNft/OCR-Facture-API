# Documentation API Details pour RapidAPI

## 📝 Contenu à copier dans "API details" / "Documentation"

---

## 🎯 Description courte (Short Description)

```
Convert PDF invoices to JSON and Factur-X XML (EN16931 standard for France / Europe). Extract amounts, dates, invoice numbers, vendor, client, banking info, and structured tables automatically with confidence scores.
```

---

## 📄 Description longue (Long Description / API Details)

### Copy-paste ready version (à copier tel quel) :

```markdown
# OCR Facture FR → JSON + Factur-X API

## Overview

Transform your French and European invoices into structured JSON data and Factur-X XML (EN16931 standard) automatically. This API uses advanced OCR technology to extract all key information from invoice images and PDFs, eliminating manual data entry and streamlining your accounting workflow.

## Key Features

### ✅ Automatic Data Extraction
- **Invoice Totals**: HT (before tax), TTC (including tax), VAT amounts
- **Dates**: Invoice date, due date
- **Identification**: Invoice number, vendor name, client name
- **Line Items**: Description, quantity, unit price, total per line
- **Banking Information**: IBAN, SWIFT/BIC, RIB, account numbers
- **Structured Tables**: Automatic detection and extraction of tabular data

### ✅ Multi-Page PDF Support
Process entire PDF documents with multiple pages. All pages are analyzed and merged automatically.

### ✅ Confidence Scoring
Every extracted field includes a confidence score (0-1) so you know how reliable each piece of data is. Perfect for validation workflows.

### ✅ Batch Processing
Process up to 10 invoices in a single API call, with automatic caching for faster responses.

### ✅ Multi-Language Support
- French (fra) - Optimized for French invoices
- English (eng)
- German (deu)
- Spanish (spa)
- Italian (ita)
- Portuguese (por)

### ✅ Enterprise Integrations
Ready-to-use webhooks for:
- **Zapier**: Automate your workflow
- **Make (Integromat)**: Connect with 1000+ apps
- **Salesforce**: Direct integration with your CRM

### ✅ Performance Optimized
- **Caching**: Instant responses for previously processed invoices
- **Fast Processing**: Average response time < 2 seconds
- **Reliable**: 99.9% uptime guarantee

## Use Cases

### 📊 Accounting Automation
Automatically extract invoice data and import into your accounting software (Sage, QuickBooks, Xero, etc.)

### 🏢 ERP Integration
Feed structured invoice data directly into your ERP system without manual entry.

### 📧 Email Processing
Process invoices received by email automatically using Zapier or Make integrations.

### 🗂️ Document Management
Extract and organize invoice data for document management systems.

### 💰 Expense Management
Automatically categorize and extract expense data from receipts and invoices.

### 📋 Compliance (France/Europe)
Generate Factur-X XML files (EN16931 standard) for e-invoicing compliance.

## Getting Started

### 1. Subscribe to a Plan
Choose the plan that fits your needs:
- **Basic**: 100 requests/month - $0/month - Perfect for testing
- **Pro**: 20,000 requests/month - $15/month - For small businesses
- **Ultra**: 80,000 requests/month - $59/month - For medium businesses
- **Mega**: 250,000 requests/month - $149/month - For large enterprises

### 2. Get Your API Key
After subscribing, you'll receive your `X-RapidAPI-Proxy-Secret` in the dashboard.

### 3. Make Your First Request

**Example with cURL:**
```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: your-secret" \
  -F "file=@invoice.jpg" \
  -F "language=fra"
```

**Example with Python:**
```python
import requests

url = "https://ocr-facture-api-production.up.railway.app/ocr/upload"
headers = {"X-RapidAPI-Proxy-Secret": "your-secret"}

with open("invoice.jpg", "rb") as f:
    files = {"file": f}
    data = {"language": "fra"}
    response = requests.post(url, headers=headers, files=files, data=data)
    print(response.json())
```

## Response Format

Every response includes:

```json
{
  "success": true,
  "cached": false,
  "data": {
    "text": "Full extracted text...",
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
  },
  "confidence_scores": {
    "total": 0.95,
    "invoice_number": 0.88,
    "items": 0.90,
    "banking_info": 0.85
  }
}
```

## Confidence Scores Explained

Every extracted field has a confidence score from 0 to 1:
- **0.9 - 1.0**: Very reliable ✅
- **0.7 - 0.9**: Reliable ⚠️
- **< 0.7**: Should be verified ❌

Use these scores to:
- Automatically validate high-confidence data
- Flag low-confidence fields for manual review
- Build validation workflows

## Batch Processing

Process multiple invoices at once:

```python
import requests

response = requests.post(
    "https://ocr-facture-api-production.up.railway.app/ocr/batch",
    headers={
        "X-RapidAPI-Proxy-Secret": "your-secret",
        "Content-Type": "application/json"
    },
    json={
        "files": ["base64_image1", "base64_image2"],
        "language": "fra"
    }
)

results = response.json()
print(f"Processed: {results['total_processed']}")
print(f"From cache: {results['total_cached']}")
```

## Webhook Integrations

### Zapier
Use the `/webhooks/zapier` endpoint to connect with 5000+ apps.

### Make (Integromat)
Use the `/webhooks/make` endpoint for advanced automation workflows.

### Salesforce
Use the `/webhooks/salesforce` endpoint to create Invoice records directly in Salesforce.

## Supported File Formats

- **Images**: JPEG, PNG
- **Documents**: PDF (single or multi-page)

## Rate Limits

Rate limits depend on your subscription plan:
- **Basic**: 100 requests/month - $0/month
- **Pro**: 20,000 requests/month - $15/month
- **Ultra**: 80,000 requests/month - $59/month
- **Mega**: 250,000 requests/month - $149/month

## Best Practices

1. **Specify Language**: Always provide the `language` parameter for better accuracy
2. **Check Confidence Scores**: Use confidence scores to validate critical data
3. **Use Batch Processing**: Process multiple invoices together for efficiency
4. **Leverage Caching**: The API automatically caches results for faster responses
5. **Handle Errors**: Always check the `success` field in responses

## Support

- **Documentation**: Full documentation available in Swagger UI at `/docs`
- **GitHub**: https://github.com/RailsNft/OCR-Facture-API
- **Support**: Contact via RapidAPI Provider Dashboard

## Pricing

All plans include:
- ✅ Multi-language support
- ✅ PDF multi-page support
- ✅ Confidence scoring
- ✅ Batch processing
- ✅ Webhook integrations
- ✅ Result caching

Start with the **Basic plan** (100 requests/month - free) to test the API, then upgrade as your needs grow!

---

**Ready to automate your invoice processing? Subscribe now and start extracting data in minutes!** 🚀
```

---

## 🎯 Version alternative (plus concise)

Si RapidAPI limite la longueur, utilisez cette version plus courte :

```markdown
# OCR Facture FR → JSON + Factur-X API

## Transform French Invoices into Structured Data

Automatically extract all key information from French and European invoices using advanced OCR technology. Convert PDF invoices to JSON and Factur-X XML (EN16931 standard) with confidence scores for every field.

## What You Get

✅ **Complete Data Extraction**
- Invoice totals (HT, TTC, VAT)
- Dates, invoice numbers
- Vendor and client information
- Line items with quantities and prices
- Banking details (IBAN, SWIFT, RIB)
- Structured tables

✅ **Enterprise Features**
- Multi-page PDF support
- Batch processing (up to 10 invoices)
- Confidence scoring (0-1) for validation
- Result caching for speed
- Webhooks for Zapier, Make, Salesforce

✅ **Multi-Language**
Optimized for French invoices, also supports English, German, Spanish, Italian, Portuguese.

## Perfect For

- Accounting automation
- ERP integration
- Email invoice processing
- Document management
- Expense management
- E-invoicing compliance (Factur-X)

## Quick Start

1. Subscribe to a plan (Basic plan: 100 requests/month)
2. Get your API key
3. Upload an invoice image or PDF
4. Receive structured JSON data instantly

## Example Response

```json
{
  "success": true,
  "extracted_data": {
    "invoice_number": "FAC-2024-001",
    "total_ttc": 1250.50,
    "date": "15/03/2024",
    "vendor": "Société Example",
    "items": [...],
    "banking_info": {"iban": "FR76..."}
  },
  "confidence_scores": {
    "total": 0.95,
    "invoice_number": 0.88
  }
}
```

## Try It Free

Start with 100 free requests/month. No credit card required!

Perfect for French businesses needing invoice automation. 🚀
```

---

## 📋 Version pour "Short Description" (si limité à 200 caractères)

```
Convert PDF invoices to JSON and Factur-X XML (EN16931). Extract amounts, dates, invoice numbers, vendor, client, banking info, and tables automatically with confidence scores. Multi-language support. Batch processing. Webhooks for Zapier/Make/Salesforce.
```

---

## 💡 Conseils d'utilisation

1. **Copiez la version complète** dans "Long Description" / "API Details"
2. **Utilisez la version courte** si RapidAPI limite la longueur
3. **Ajoutez des screenshots** :
   - Interface Swagger UI
   - Exemple de facture traitée
   - Résultat JSON formaté
4. **Mettez à jour régulièrement** selon les retours utilisateurs

---

## ✅ Checklist avant de publier

- [ ] Description courte optimisée (inclut tous les mots-clés)
- [ ] Description longue complète avec exemples
- [ ] Code examples inclus (Python, cURL)
- [ ] Liste des fonctionnalités claire
- [ ] Cas d'usage mentionnés
- [ ] Format de réponse expliqué
- [ ] Liens vers documentation (GitHub, Swagger)
- [ ] Call-to-action pour s'abonner

---

**Copiez le contenu ci-dessus directement dans RapidAPI pour une documentation professionnelle !** 🚀

