# Comment tester l'OCR avec une image de facture

## Méthode 1: Avec le script Python

```bash
python test_ocr_invoice.py chemin/vers/votre/facture.jpg fra
```

**Exemple:**
```bash
python test_ocr_invoice.py ~/Downloads/facture.jpg fra
```

## Méthode 2: Avec curl (depuis le terminal)

### Test avec image locale

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd" \
  -F "file=@/chemin/vers/votre/facture.jpg" \
  -F "language=fra"
```

**Exemple concret:**
```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd" \
  -F "file=@~/Downloads/facture.jpg" \
  -F "language=fra" | python3 -m json.tool
```

### Test avec image base64

Si vous avez une image en base64:

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/base64" \
  -H "X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "image_base64=data:image/jpeg;base64,VOTRE_IMAGE_BASE64_ICI" \
  -d "language=fra" | python3 -m json.tool
```

## Méthode 3: Depuis l'interface RapidAPI

1. Allez sur votre API dans RapidAPI Provider Dashboard
2. Cliquez sur "Testing"
3. Sélectionnez l'endpoint `/ocr/upload`
4. Uploadez votre image de facture
5. Sélectionnez la langue
6. Cliquez sur "Run" ou "Test Endpoint"

## Méthode 4: Depuis la documentation Swagger

1. Allez sur: https://ocr-facture-api-production.up.railway.app/docs
2. Trouvez l'endpoint `POST /ocr/upload`
3. Cliquez sur "Try it out"
4. Uploadez votre fichier image
5. Entrez la langue (fra, eng, etc.)
6. Cliquez sur "Execute"

## Langues supportées

- `fra` - Français (défaut)
- `eng` - English
- `deu` - Deutsch
- `spa` - Español
- `ita` - Italiano
- `por` - Português

## Formats d'image supportés

- JPEG (.jpg, .jpeg)
- PNG (.png)
- PDF (.pdf) - peut nécessiter conversion

## Exemple de réponse attendue

```json
{
  "success": true,
  "data": {
    "text": "FACTURE\nNuméro: FAC-2024-001\n...",
    "language": "fra"
  },
  "extracted_data": {
    "text": "...",
    "lines": ["FACTURE", "Numéro: FAC-2024-001", ...],
    "total": 1250.50,
    "total_ht": 1042.08,
    "total_ttc": 1250.50,
    "tva": 208.42,
    "date": "15/03/2024",
    "invoice_number": "FAC-2024-001",
    "vendor": "Société Example SARL",
    "client": "Client ABC",
    "currency": "EUR"
  }
}
```

## Conseils pour de meilleurs résultats

1. **Qualité de l'image**: Utilisez des images claires et bien éclairées
2. **Résolution**: Minimum 300 DPI recommandé
3. **Format**: JPEG ou PNG de bonne qualité
4. **Orientation**: L'image doit être droite (pas de rotation)
5. **Langue**: Sélectionnez la bonne langue pour de meilleurs résultats

## Dépannage

### Erreur 401 Unauthorized
- Vérifiez que le header `X-RapidAPI-Proxy-Secret` est correct
- Vérifiez que le secret est configuré dans Railway

### Erreur 400 Bad Request
- Vérifiez que le fichier est bien une image (JPEG, PNG)
- Vérifiez la taille du fichier (max recommandé: 10MB)

### Erreur 500 Internal Server Error
- Vérifiez les logs Railway pour plus de détails
- Vérifiez que Tesseract est bien installé

### Résultats vides ou incorrects
- Essayez avec une meilleure qualité d'image
- Vérifiez que la langue sélectionnée correspond à la langue de la facture
- Les factures manuscrites peuvent donner de moins bons résultats

