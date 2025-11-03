# 📚 Tutoriels RapidAPI - Contenu prêt à utiliser

## 🎯 Tutoriel 1 : Test rapide avec l'interface de démo

### Titre
```
Testez l'API avec l'interface de démo interactive
```

### URL
```
https://ocr-facture-api-production.up.railway.app/demo/
```

### Image URL (optionnel)
```
https://raw.githubusercontent.com/RailsNft/OCR-Facture-API/main/docs/images/demo-interface-screenshot.png
```

**Note** : Utilisez l'URL GitHub Raw ci-dessus. Elle fonctionne immédiatement après avoir commité l'image dans Git. Si l'image n'est pas encore dans le repo, utilisez temporairement Imgur ou attendez le commit.

### Contenu
```markdown
# Testez l'API avec l'interface de démo interactive

## 🚀 Démarrage rapide

L'interface de démo vous permet de tester l'API OCR Facture en quelques clics, sans écrire une seule ligne de code !

## 📋 Prérequis

- Un compte RapidAPI (gratuit)
- Une clé API (obtenue après abonnement à un plan)
- Une facture en image (JPEG, PNG) ou PDF

## 🎯 Étapes

### 1. Accéder à l'interface de démo

Visitez : **https://ocr-facture-api-production.up.railway.app/demo/**

### 2. Obtenir votre clé API

1. Allez sur [RapidAPI](https://rapidapi.com)
2. Abonnez-vous à l'API OCR Facture (plan BASIC gratuit disponible)
3. Dans le dashboard, copiez votre `X-RapidAPI-Proxy-Secret`

### 3. Entrer votre clé API

Dans l'interface de démo, collez votre clé API dans le champ prévu en haut de la page.

### 4. Uploader une facture

- **Glissez-déposez** votre facture directement
- Ou cliquez sur **"Parcourir les fichiers"**
- Formats supportés : JPEG, PNG, PDF (max 10 MB)

### 5. Configurer les options

- **Langue** : Sélectionnez la langue de votre facture (Français, Anglais, Allemand, Espagnol, Italien, Portugais)
- **Validation conformité FR** : Cochez si vous voulez vérifier la conformité française (TVA, SIREN/SIRET)

### 6. Traiter la facture

Cliquez sur **"🚀 Traiter la facture"** et attendez quelques secondes.

### 7. Visualiser les résultats

Vous verrez :
- ✅ **Données extraites** : Numéro, date, vendeur, client, montants HT/TTC, TVA
- 📊 **Scores de confiance** : Pourcentage de fiabilité pour chaque champ
- ✅ **Conformité** : Statut de conformité avec détails des champs manquants
- 📦 **Lignes de facture** : Tableau avec description, quantité, prix unitaire, total

### 8. Exporter les résultats

- **Export JSON** : Téléchargez les résultats complets au format JSON
- **Export CSV** : Téléchargez un tableau CSV pour Excel/Google Sheets

## 💡 Astuces

- Utilisez des factures de bonne qualité pour de meilleurs résultats
- Les factures en français sont optimisées (meilleure précision)
- La validation de conformité vérifie les mentions légales obligatoires françaises

## 🎓 Prochaines étapes

Une fois testé avec l'interface de démo, intégrez l'API dans votre application avec les SDKs Python ou JavaScript disponibles.
```

---

## 🎯 Tutoriel 2 : Intégration Python rapide

### Titre
```
Intégrer l'API avec Python en 5 minutes
```

### URL
```
https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/python
```

### Image URL (optionnel)
```
https://ocr-facture-api-production.up.railway.app/docs
```

### Contenu
```markdown
# Intégrer l'API avec Python en 5 minutes

## 📦 Installation

```bash
pip install ocr-facture-api
```

Ou depuis le repository GitHub :
```bash
pip install git+https://github.com/RailsNft/OCR-Facture-API.git#subdirectory=sdk/python
```

## 🔑 Configuration

```python
from ocr_facture_api import OCRFactureAPI

# Initialiser le client
api = OCRFactureAPI(
    api_secret="votre_cle_rapidapi_ici",
    base_url="https://ocr-facture-api-production.up.railway.app"
)
```

## 📄 Exemple 1 : Upload d'une facture

```python
# Traiter une facture depuis un fichier
result = api.upload_invoice(
    file_path="facture.jpg",
    language="fra"
)

# Afficher les résultats
print(f"Numéro de facture : {result['extracted_data']['invoice_number']}")
print(f"Date : {result['extracted_data']['date']}")
print(f"Total HT : {result['extracted_data']['total_ht']} €")
print(f"TVA : {result['extracted_data']['tva']} €")
print(f"Total TTC : {result['extracted_data']['total_ttc']} €")
```

## 📄 Exemple 2 : Traitement par lot (Batch)

```python
# Traiter plusieurs factures en une seule requête
files = ["facture1.pdf", "facture2.jpg", "facture3.png"]

result = api.batch_process(
    files=files,
    language="fra",
    check_compliance=True
)

# Parcourir les résultats
for i, invoice_result in enumerate(result['results']):
    print(f"Facture {i+1}:")
    print(f"  Total TTC: {invoice_result['extracted_data']['total_ttc']} €")
```

## ✅ Exemple 3 : Validation de conformité

```python
# Valider la conformité d'une facture française
validation = api.validate_compliance(
    invoice_data=result['extracted_data']
)

if validation['compliance_check']['compliant']:
    print("✅ Facture conforme")
else:
    print("❌ Facture non conforme")
    print(f"Champs manquants: {validation['compliance_check']['missing_fields']}")
```

## 🎯 Cas d'usage complet

```python
import os
from ocr_facture_api import OCRFactureAPI

# Configuration
api = OCRFactureAPI(api_secret=os.getenv("RAPIDAPI_SECRET"))

# Traiter toutes les factures d'un dossier
invoice_folder = "./factures/"
results = []

for filename in os.listdir(invoice_folder):
    if filename.endswith(('.jpg', '.png', '.pdf')):
        file_path = os.path.join(invoice_folder, filename)
        
        try:
            result = api.upload_invoice(
                file_path=file_path,
                language="fra",
                check_compliance=True
            )
            
            results.append({
                'file': filename,
                'invoice_number': result['extracted_data']['invoice_number'],
                'total_ttc': result['extracted_data']['total_ttc'],
                'compliant': result.get('compliance', {}).get('compliance_check', {}).get('compliant', False)
            })
            
        except Exception as e:
            print(f"Erreur pour {filename}: {e}")

# Exporter en CSV
import csv
with open('resultats.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Fichier', 'Numéro', 'Total TTC', 'Conforme'])
    for r in results:
        writer.writerow([r['file'], r['invoice_number'], r['total_ttc'], r['compliant']])
```

## 📚 Documentation complète

Consultez la documentation complète : https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/python
```

---

## 🎯 Tutoriel 3 : Intégration JavaScript/Node.js

### Titre
```
Intégrer l'API avec JavaScript/Node.js
```

### URL
```
https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/javascript
```

### Image URL (optionnel)
```
https://ocr-facture-api-production.up.railway.app/docs
```

### Contenu
```markdown
# Intégrer l'API avec JavaScript/Node.js

## 📦 Installation

```bash
npm install ocr-facture-api
```

## 🔑 Configuration

```javascript
import { OCRFactureAPI } from 'ocr-facture-api';

// Initialiser le client
const api = new OCRFactureAPI({
  apiSecret: 'votre_cle_rapidapi_ici',
  baseUrl: 'https://ocr-facture-api-production.up.railway.app'
});
```

## 📄 Exemple 1 : Upload d'une facture

```javascript
import fs from 'fs';

// Traiter une facture depuis un fichier
const result = await api.uploadInvoice({
  file: fs.createReadStream('facture.jpg'),
  language: 'fra'
});

// Afficher les résultats
console.log(`Numéro de facture : ${result.extracted_data.invoice_number}`);
console.log(`Date : ${result.extracted_data.date}`);
console.log(`Total HT : ${result.extracted_data.total_ht} €`);
console.log(`TVA : ${result.extracted_data.tva} €`);
console.log(`Total TTC : ${result.extracted_data.total_ttc} €`);
```

## 📄 Exemple 2 : Traitement par lot (Batch)

```javascript
// Traiter plusieurs factures en une seule requête
const files = [
  fs.createReadStream('facture1.pdf'),
  fs.createReadStream('facture2.jpg'),
  fs.createReadStream('facture3.png')
];

const result = await api.batchProcess({
  files: files,
  language: 'fra',
  checkCompliance: true
});

// Parcourir les résultats
result.results.forEach((invoiceResult, index) => {
  console.log(`Facture ${index + 1}:`);
  console.log(`  Total TTC: ${invoiceResult.extracted_data.total_ttc} €`);
});
```

## ✅ Exemple 3 : Validation de conformité

```javascript
// Valider la conformité d'une facture française
const validation = await api.validateCompliance({
  invoiceData: result.extracted_data
});

if (validation.compliance_check.compliant) {
  console.log('✅ Facture conforme');
} else {
  console.log('❌ Facture non conforme');
  console.log(`Champs manquants: ${validation.compliance_check.missing_fields.join(', ')}`);
}
```

## 🌐 Exemple 4 : Frontend (React/Vue)

```javascript
// Dans un composant React
import { OCRFactureAPI } from 'ocr-facture-api';

const handleUpload = async (file) => {
  const api = new OCRFactureAPI({
    apiSecret: process.env.REACT_APP_RAPIDAPI_SECRET
  });
  
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const result = await api.uploadInvoice({
      file: file,
      language: 'fra'
    });
    
    setResults(result.extracted_data);
  } catch (error) {
    console.error('Erreur:', error);
  }
};
```

## 📚 Documentation complète

Consultez la documentation complète : https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/javascript
```

---

## 🎯 Tutoriel 4 : Utilisation avec cURL

### Titre
```
Tester l'API avec cURL (exemples pratiques)
```

### URL
```
https://ocr-facture-api-production.up.railway.app/docs
```

### Image URL (optionnel)
```
https://ocr-facture-api-production.up.railway.app/docs
```

### Contenu
```markdown
# Tester l'API avec cURL (exemples pratiques)

## 🔑 Configuration

Remplacez `VOTRE_CLE_API` par votre clé RapidAPI (`X-RapidAPI-Proxy-Secret`).

## 📄 Exemple 1 : Upload d'une facture

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API" \
  -F "file=@facture.jpg" \
  -F "language=fra"
```

## 📄 Exemple 2 : Upload avec validation de conformité

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API" \
  -F "file=@facture.pdf" \
  -F "language=fra" \
  -F "check_compliance=true"
```

## 📄 Exemple 3 : Traitement par lot (Batch)

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/batch" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API" \
  -F "files=@facture1.pdf" \
  -F "files=@facture2.jpg" \
  -F "files=@facture3.png" \
  -F "language=fra" \
  -F "check_compliance=true"
```

## ✅ Exemple 4 : Validation de conformité

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/compliance/check" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "total_ht": 1042.08,
      "total_ttc": 1250.50,
      "tva": 208.42,
      "date": "15/03/2024",
      "invoice_number": "FAC-2024-001"
    }
  }'
```

## 📄 Exemple 5 : Génération Factur-X

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/facturx/generate" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_data": {
      "invoice_number": "FAC-2024-001",
      "date": "2024-03-15",
      "vendor": "Société Example",
      "client": "Client ABC",
      "total_ht": 1042.08,
      "total_ttc": 1250.50,
      "tva": 208.42
    }
  }'
```

## 📊 Formater la réponse JSON

Pour une meilleure lisibilité, pipez vers `jq` :

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API" \
  -F "file=@facture.jpg" \
  -F "language=fra" | jq '.'
```

## 🔍 Vérifier le quota restant

```bash
curl -X GET "https://ocr-facture-api-production.up.railway.app/v1/quota" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_API"
```

## 📚 Documentation complète

Consultez la documentation Swagger : https://ocr-facture-api-production.up.railway.app/docs
```

---

## 🎯 Tutoriel 5 : Automatisation comptable complète

### Titre
```
Automatiser le traitement de factures avec Python
```

### URL
```
https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/python
```

### Image URL (optionnel)
```
https://ocr-facture-api-production.up.railway.app/demo/
```

### Contenu
```markdown
# Automatiser le traitement de factures avec Python

## 🎯 Objectif

Créer un système complet d'automatisation pour traiter des factures, valider leur conformité, et exporter les résultats.

## 📋 Prérequis

```bash
pip install ocr-facture-api pandas openpyxl
```

## 🚀 Code complet

```python
import os
import pandas as pd
from datetime import datetime
from ocr_facture_api import OCRFactureAPI

# Configuration
api = OCRFactureAPI(api_secret=os.getenv("RAPIDAPI_SECRET"))

def process_invoice_folder(folder_path, output_file="resultats_factures.xlsx"):
    """
    Traite toutes les factures d'un dossier et exporte les résultats
    """
    results = []
    errors = []
    
    # Parcourir tous les fichiers
    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.pdf')):
            continue
            
        file_path = os.path.join(folder_path, filename)
        print(f"Traitement de {filename}...")
        
        try:
            # Traiter la facture
            result = api.upload_invoice(
                file_path=file_path,
                language="fra",
                check_compliance=True
            )
            
            extracted = result['extracted_data']
            compliance = result.get('compliance', {})
            
            # Extraire les informations
            invoice_data = {
                'Fichier': filename,
                'Numéro': extracted.get('invoice_number', 'N/A'),
                'Date': extracted.get('date', 'N/A'),
                'Vendeur': extracted.get('vendor', 'N/A'),
                'Client': extracted.get('client', 'N/A'),
                'Total HT': extracted.get('total_ht', 0),
                'TVA': extracted.get('tva', 0),
                'Total TTC': extracted.get('total_ttc', 0),
                'Conforme': compliance.get('compliance_check', {}).get('compliant', False),
                'Score conformité': compliance.get('compliance_check', {}).get('score', 0),
                'Confiance moyenne': sum(result.get('confidence_scores', {}).values()) / len(result.get('confidence_scores', {})) if result.get('confidence_scores') else 0,
                'Date traitement': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            results.append(invoice_data)
            print(f"  ✅ Traité avec succès")
            
        except Exception as e:
            errors.append({'Fichier': filename, 'Erreur': str(e)})
            print(f"  ❌ Erreur: {e}")
    
    # Créer un DataFrame
    df = pd.DataFrame(results)
    
    # Exporter vers Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Factures', index=False)
        
        # Ajouter un résumé
        summary = pd.DataFrame({
            'Métrique': ['Total factures', 'Total HT', 'Total TVA', 'Total TTC', 'Factures conformes', 'Taux conformité'],
            'Valeur': [
                len(results),
                df['Total HT'].sum(),
                df['TVA'].sum(),
                df['Total TTC'].sum(),
                df['Conforme'].sum(),
                f"{(df['Conforme'].sum() / len(results) * 100):.1f}%" if results else "0%"
            ]
        })
        summary.to_excel(writer, sheet_name='Résumé', index=False)
        
        # Ajouter les erreurs si présentes
        if errors:
            errors_df = pd.DataFrame(errors)
            errors_df.to_excel(writer, sheet_name='Erreurs', index=False)
    
    print(f"\n✅ Traitement terminé !")
    print(f"📊 {len(results)} factures traitées")
    print(f"📁 Résultats exportés dans {output_file}")
    
    if errors:
        print(f"⚠️  {len(errors)} erreurs (voir onglet 'Erreurs')")
    
    return df

# Utilisation
if __name__ == "__main__":
    # Traiter toutes les factures du dossier
    results = process_invoice_folder("./factures/", "rapport_factures.xlsx")
    
    # Afficher un résumé
    print("\n📊 Résumé:")
    print(f"Total HT: {results['Total HT'].sum():.2f} €")
    print(f"Total TVA: {results['TVA'].sum():.2f} €")
    print(f"Total TTC: {results['Total TTC'].sum():.2f} €")
    print(f"Factures conformes: {results['Conforme'].sum()}/{len(results)}")
```

## 🔄 Intégration avec un système de fichiers

```python
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InvoiceHandler(FileSystemEventHandler):
    def __init__(self, api):
        self.api = api
        
    def on_created(self, event):
        if event.is_directory:
            return
            
        if event.src_path.lower().endswith(('.jpg', '.png', '.pdf')):
            print(f"Nouvelle facture détectée: {event.src_path}")
            try:
                result = self.api.upload_invoice(
                    file_path=event.src_path,
                    language="fra",
                    check_compliance=True
                )
                print(f"✅ Traitée: {result['extracted_data']['invoice_number']}")
            except Exception as e:
                print(f"❌ Erreur: {e}")

# Surveiller un dossier
api = OCRFactureAPI(api_secret=os.getenv("RAPIDAPI_SECRET"))
event_handler = InvoiceHandler(api)
observer = Observer()
observer.schedule(event_handler, "./factures/", recursive=False)
observer.start()

print("Surveillance du dossier 'factures/'... Appuyez sur Ctrl+C pour arrêter.")
try:
    observer.join()
except KeyboardInterrupt:
    observer.stop()
```

## 📚 Documentation complète

Consultez la documentation : https://github.com/RailsNft/OCR-Facture-API/tree/main/sdk/python
```

---

## 📋 Résumé des tutoriels à créer

| # | Titre | URL | Type |
|---|-------|-----|------|
| 1 | Testez l'API avec l'interface de démo interactive | `/demo/` | Débutant |
| 2 | Intégrer l'API avec Python en 5 minutes | GitHub Python SDK | Intermédiaire |
| 3 | Intégrer l'API avec JavaScript/Node.js | GitHub JS SDK | Intermédiaire |
| 4 | Tester l'API avec cURL (exemples pratiques) | `/docs` | Débutant |
| 5 | Automatiser le traitement de factures avec Python | GitHub Python SDK | Avancé |

## 🎯 Ordre recommandé de création

1. **Tutoriel 1** (Démo) - Le plus accessible
2. **Tutoriel 4** (cURL) - Pour les développeurs qui veulent tester rapidement
3. **Tutoriel 2** (Python) - Le SDK le plus utilisé
4. **Tutoriel 3** (JavaScript) - Pour les développeurs web
5. **Tutoriel 5** (Automatisation) - Cas d'usage avancé

---

## 💡 Conseils

- **Ajoutez des screenshots** de l'interface de démo pour le tutoriel 1
- **Ajoutez des exemples de résultats** JSON pour montrer la structure
- **Mettez à jour régulièrement** selon les retours utilisateurs
- **Créez d'abord les 2-3 premiers** tutoriels, puis ajoutez les autres progressivement

