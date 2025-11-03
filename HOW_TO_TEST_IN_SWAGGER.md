# Comment tester dans Swagger avec authentification

## Problème

Quand vous testez depuis `/docs` (Swagger UI), vous obtenez une erreur 401 car le header `X-RapidAPI-Proxy-Secret` n'est pas inclus automatiquement.

## Solution 1: Ajouter le header dans Swagger

### Étapes :

1. Allez sur : https://ocr-facture-api-production.up.railway.app/docs
2. Trouvez l'endpoint `POST /ocr/upload`
3. Cliquez sur "Try it out"
4. **AVANT de remplir les paramètres**, cherchez la section **"Authorize"** ou **"🔓 Authorize"** en haut de la page Swagger
5. Cliquez sur "Authorize"
6. Si vous voyez un champ pour `X-RapidAPI-Proxy-Secret`, entrez :
   ```
   f67eb770-b6b9-11f0-9b0e-0f41c7e962fd
   ```
7. Cliquez sur "Authorize" puis "Close"
8. Maintenant remplissez les paramètres :
   - `file`: Uploadez votre PDF/image
   - `language`: `fra`
9. Cliquez sur "Execute"

## Solution 2: Utiliser curl (Plus simple)

Copiez cette commande et remplacez le chemin du fichier :

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd" \
  -H "accept: application/json" \
  -F "file=@/chemin/vers/votre/devis-crm-nuisipro-final.pdf" \
  -F "language=fra" | python3 -m json.tool
```

**Exemple avec votre fichier :**
```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd" \
  -H "accept: application/json" \
  -F "file=@devis-crm-nuisipro-final.pdf" \
  -F "language=fra" | python3 -m json.tool
```

## Solution 3: Utiliser le script Python

```bash
python test_ocr_invoice.py devis-crm-nuisipro-final.pdf fra
```

## Solution 4: Modifier Swagger pour inclure le header par défaut

Si vous voulez que Swagger inclue automatiquement le header, vous pouvez modifier le code pour ajouter un bouton "Authorize" dans Swagger UI. Mais pour l'instant, la méthode curl est la plus simple.

## Note importante

- Les endpoints `/docs`, `/redoc`, `/openapi.json`, `/health`, `/` sont accessibles sans authentification
- Tous les autres endpoints nécessitent le header `X-RapidAPI-Proxy-Secret`
- C'est normal et sécurisé pour la production

## Test rapide avec votre PDF

Depuis le terminal, dans le dossier où se trouve votre PDF :

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd" \
  -F "file=@devis-crm-nuisipro-final.pdf" \
  -F "language=fra" | python3 -m json.tool
```

Cela devrait fonctionner ! 🚀

