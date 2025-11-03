# 📍 Où ajouter l'URL de démo sur RapidAPI

## ✅ URL de l'interface de démo

**`https://ocr-facture-api-production.up.railway.app/demo/`**

---

## 🎯 Endroits où l'ajouter dans RapidAPI Dashboard

### 1. **Long Description / API Details** (PRIORITÉ HAUTE)

Dans la section "Long Description" ou "API Details", ajoutez une section "Try It Now" :

```markdown
## 🚀 Try It Now - Interactive Demo

Test the API instantly with our interactive demo interface:

**👉 [Try Demo Interface](https://ocr-facture-api-production.up.railway.app/demo/)**

Upload an invoice image, see the extraction results in real-time, and export as JSON or CSV. No API key required for testing!
```

**Où trouver :**
- RapidAPI Provider Dashboard → Votre API → "Edit" → Section "Description" ou "API Details"

---

### 2. **Tutorials Section** (RECOMMANDÉ)

Créez un tutoriel court avec un lien vers la démo :

**Titre du tutoriel :**
```
Test the API with Interactive Demo
```

**Contenu :**
```markdown
# Test OCR Facture API - Interactive Demo

The easiest way to test our API is using our interactive demo interface.

## Step 1: Access the Demo

Visit: https://ocr-facture-api-production.up.railway.app/demo/

## Step 2: Enter Your API Key

1. Get your API key from RapidAPI (click "Subscribe" to any plan)
2. Copy your `X-RapidAPI-Proxy-Secret` from the API details page
3. Paste it in the API key field at the top of the demo page

## Step 3: Upload an Invoice

1. Drag and drop an invoice image (JPEG, PNG) or PDF
2. Select the language (French, English, German, Spanish, Italian, Portuguese)
3. Optionally enable compliance checking for French invoices
4. Click "Process Invoice"

## Step 4: View Results

- See extracted data: invoice number, date, amounts, vendor, client
- Check confidence scores for each field
- View compliance status (if enabled)
- Export results as JSON or CSV

## Next Steps

Once you've tested the demo, integrate the API into your application using the code examples in the API documentation.
```

**Où trouver :**
- RapidAPI Provider Dashboard → Votre API → "Tutorials" → "Add Tutorial"

---

### 3. **Code Examples** (OPTIONNEL)

Dans les exemples de code, ajoutez un commentaire :

```javascript
// Quick test: Try the interactive demo at https://ocr-facture-api-production.up.railway.app/demo/

const axios = require('axios');
// ... reste du code
```

---

### 4. **External Links** (SI DISPONIBLE)

Si RapidAPI a une section "External Links" ou "Resources" :

- **Label**: `Interactive Demo`
- **URL**: `https://ocr-facture-api-production.up.railway.app/demo/`
- **Description**: `Test the API instantly with our interactive web interface`

---

### 5. **README / Documentation Files** (SI UPLOAD DE FICHIERS)

Si vous pouvez uploader des fichiers de documentation, créez un fichier `DEMO.md` :

```markdown
# Interactive Demo

Try our API instantly: https://ocr-facture-api-production.up.railway.app/demo/

No installation required. Just upload an invoice and see the results!
```

---

## 📋 Checklist

- [ ] Ajouté dans "Long Description" avec un lien visible
- [ ] Créé un tutoriel "Test with Interactive Demo"
- [ ] Mentionné dans les exemples de code (commentaires)
- [ ] Ajouté dans "External Links" si disponible
- [ ] Testé le lien (doit fonctionner sans erreur 401)

---

## 💡 Conseils

1. **Mettez le lien en évidence** : Utilisez un bouton/lien visible en haut de la description
2. **Créez un tutoriel** : Les tutoriels augmentent le taux de conversion
3. **Mentionnez "No API key required"** : Pour tester, les utilisateurs peuvent utiliser leur propre clé
4. **Screenshots** : Prenez des captures d'écran de l'interface et ajoutez-les dans la description

---

## 🎨 Exemple de texte pour la description

```markdown
## 🎮 Interactive Demo - Try It Now!

**No coding required!** Test our API instantly with our web-based demo interface:

👉 **[Try Demo](https://ocr-facture-api-production.up.railway.app/demo/)**

Features:
- Upload invoice images or PDFs
- See extraction results in real-time
- View confidence scores
- Export as JSON or CSV
- Test compliance checking

Just enter your RapidAPI key and start testing!
```

---

## ✅ Résultat attendu

Une fois ajouté, les utilisateurs pourront :
1. Découvrir votre API sur RapidAPI
2. Cliquer sur "Try Demo" directement depuis la page
3. Tester sans installation ni code
4. Voir les résultats en temps réel
5. Comprendre mieux les capacités de l'API

Cela augmente significativement le taux de conversion (test → abonnement) ! 🚀



