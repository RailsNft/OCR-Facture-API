# OCR Facture API - SDK JavaScript/TypeScript

SDK JavaScript/TypeScript officiel pour l'API OCR Facture France. Facilite l'intégration de l'extraction automatique de données de factures dans vos applications Node.js, React, Vue.js, etc.

## 🚀 Installation

```bash
npm install ocr-facture-api
# ou
yarn add ocr-facture-api
# ou
pnpm add ocr-facture-api
```

## 📖 Utilisation

### Configuration de base

```typescript
import { OCRFactureAPI } from 'ocr-facture-api';

// Initialiser le client
const api = new OCRFactureAPI(
  'votre_cle_api_rapidapi',
  'https://ocr-facture-api-production.up.railway.app' // Optionnel
);
```

### Extraire les données d'une facture

#### Depuis un fichier

```typescript
// Depuis un fichier local
const result = await api.extractFromFile('facture.pdf', {
  language: 'fra'
});

// Accéder aux données extraites
const invoiceData = result.extracted_data;
console.log(`Numéro de facture: ${invoiceData?.invoice_number}`);
console.log(`Total TTC: ${invoiceData?.total_ttc}€`);
console.log(`Date: ${invoiceData?.date}`);

// Scores de confiance
const confidence = result.confidence_scores;
console.log(`Confiance numéro: ${confidence?.invoice_number}`);
```

#### Depuis une image base64

```typescript
import * as fs from 'fs';

const imageBuffer = fs.readFileSync('facture.jpg');
const base64Data = `data:image/jpeg;base64,${imageBuffer.toString('base64')}`;

const result = await api.extractFromBase64(base64Data, {
  language: 'fra'
});
```

### Traitement par lot (batch)

```typescript
// Traiter plusieurs factures en une requête
const files = ['facture1.pdf', 'facture2.pdf', 'facture3.pdf'];
const batchResult = await api.batchExtract(files);

// Parcourir les résultats
batchResult.results.forEach((result, index) => {
  if (result.success) {
    console.log(`Facture ${index + 1}: ${result.extracted_data?.invoice_number}`);
  }
});
```

### Validation de conformité FR

```typescript
// Extraire puis valider
const result = await api.extractFromFile('facture.pdf', {
  checkCompliance: true
});

// Ou valider séparément
const invoiceData = result.extracted_data;
const compliance = await api.checkCompliance(invoiceData!);

if (compliance.compliance?.compliance_check?.compliant) {
  console.log('✅ Facture conforme');
} else {
  console.log(`❌ Champs manquants: ${compliance.compliance?.compliance_check?.missing_fields}`);
}
```

### Génération Factur-X

```typescript
// Extraire les données
const result = await api.extractFromFile('facture.pdf');
const invoiceData = result.extracted_data;

// Générer XML Factur-X
const facturXResult = await api.generateFacturX(invoiceData!);
const xmlContent = facturXResult.xml;

// Sauvegarder le XML
import * as fs from 'fs';
fs.writeFileSync('facture_facturx.xml', xmlContent, 'utf-8');
```

### Validation TVA

```typescript
const invoiceData = result.extracted_data;
const vatValidation = await api.validateVAT(invoiceData!);

if (vatValidation.validation?.valid) {
  console.log('✅ TVA valide');
} else {
  console.log(`❌ Erreurs: ${vatValidation.validation?.errors}`);
}
```

### Enrichissement SIRET

```typescript
// Enrichir avec API Sirene
const enrichment = await api.enrichSIRET('12345678901234');
console.log(`Raison sociale: ${enrichment.enrichment?.uniteLegale?.denominationUniteLegale}`);
```

### Gestion des erreurs

```typescript
import {
  OCRFactureAPIError,
  OCRFactureAuthError,
  OCRFactureRateLimitError,
  OCRFactureValidationError,
} from 'ocr-facture-api';

try {
  const result = await api.extractFromFile('facture.pdf');
} catch (error) {
  if (error instanceof OCRFactureAuthError) {
    console.error('❌ Clé API invalide');
  } else if (error instanceof OCRFactureRateLimitError) {
    console.error(`❌ Quota dépassé. Réessayez dans ${error.retryAfter} secondes`);
  } else if (error instanceof OCRFactureValidationError) {
    console.error(`❌ Erreur de validation: ${error.message}`);
  } else if (error instanceof OCRFactureAPIError) {
    console.error(`❌ Erreur API: ${error.message}`);
  }
}
```

### Idempotence

```typescript
import { randomUUID } from 'crypto';

// Utiliser une clé d'idempotence pour éviter les doublons
const idempotencyKey = randomUUID();
const result = await api.extractFromFile('facture.pdf', {
  idempotencyKey
});

// Réutiliser la même clé retourne le même résultat sans retraitement
const result2 = await api.extractFromFile('facture.pdf', {
  idempotencyKey
}); // Résultat instantané depuis le cache
```

## 📚 API Reference

### Méthodes principales

- `extractFromFile(filePath, options?)` - Extraction depuis fichier
- `extractFromBase64(base64String, options?)` - Extraction depuis base64
- `batchExtract(files, options?)` - Traitement par lot (max 10 fichiers)
- `checkCompliance(invoiceData)` - Validation conformité FR
- `validateVAT(invoiceData)` - Validation TVA
- `enrichSIRET(siret)` - Enrichissement SIRET
- `validateVIES(vatNumber)` - Validation VIES
- `generateFacturX(invoiceData)` - Génération XML Factur-X
- `parseFacturX(filePath)` - Extraction XML depuis PDF/A-3
- `validateFacturXXML(xmlContent)` - Validation XML Factur-X
- `getSupportedLanguages()` - Liste des langues supportées
- `getQuota()` - Informations sur quota restant
- `healthCheck()` - État de santé de l'API

## 🌍 Langues supportées

- `fra` - Français (défaut)
- `eng` - Anglais
- `deu` - Allemand
- `spa` - Espagnol
- `ita` - Italien
- `por` - Portugais

## 📝 Exemples complets

### Exemple 1 : Traitement automatique de factures

```typescript
import { OCRFactureAPI } from 'ocr-facture-api';
import * as fs from 'fs';
import * as path from 'path';

const api = new OCRFactureAPI(process.env.OCR_FACTURE_API_KEY!);

// Traiter toutes les factures d'un dossier
const facturesDir = './factures';
const files = fs.readdirSync(facturesDir);

for (const filename of files) {
  if (filename.match(/\.(pdf|jpg|png)$/i)) {
    const filepath = path.join(facturesDir, filename);
    try {
      const result = await api.extractFromFile(filepath, {
        checkCompliance: true
      });

      const invoiceData = result.extracted_data;
      console.log(`\n📄 ${filename}`);
      console.log(`  Numéro: ${invoiceData?.invoice_number}`);
      console.log(`  Date: ${invoiceData?.date}`);
      console.log(`  Total TTC: ${invoiceData?.total_ttc}€`);

      // Vérifier conformité
      if (result.compliance?.compliance_check?.compliant) {
        console.log('  ✅ Conforme');
      } else {
        console.log(`  ⚠️ Non conforme: ${result.compliance?.compliance_check?.missing_fields}`);
      }
    } catch (error) {
      console.error(`❌ Erreur pour ${filename}:`, error);
    }
  }
}
```

### Exemple 2 : Export vers CSV

```typescript
import { OCRFactureAPI } from 'ocr-facture-api';
import * as fs from 'fs';

const api = new OCRFactureAPI('votre_cle');

// Traiter plusieurs factures
const files = ['facture1.pdf', 'facture2.pdf', 'facture3.pdf'];
const batchResult = await api.batchExtract(files);

// Exporter vers CSV
const csvLines = ['Numéro,Date,Vendeur,Total TTC,Confiance'];

batchResult.results.forEach((result) => {
  if (result.success && result.extracted_data) {
    const data = result.extracted_data;
    csvLines.push([
      data.invoice_number || '',
      data.date || '',
      data.vendor || '',
      data.total_ttc?.toString() || '',
      result.confidence_scores?.total_ttc?.toString() || '0',
    ].join(','));
  }
});

fs.writeFileSync('factures_export.csv', csvLines.join('\n'), 'utf-8');
```

## 🔗 Liens utiles

- [Documentation API complète](https://github.com/RailsNft/OCR-Facture-API)
- [RapidAPI Marketplace](https://rapidapi.com/)
- [Issues GitHub](https://github.com/RailsNft/OCR-Facture-API/issues)

## 📄 Licence

MIT License

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.
