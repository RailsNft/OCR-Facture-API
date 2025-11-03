# 🔍 Test du header API

## Problème actuel

Le header `X-RapidAPI-Proxy-Secret` est configuré dans le code mais retourne 401.

## Vérifications à faire

### 1. Vérifier la clé dans Railway

1. Allez sur Railway → Variables d'environnement
2. Cherchez `RAPIDAPI_PROXY_SECRET`
3. Copiez EXACTEMENT cette valeur (sans espaces)

### 2. Vérifier dans la console du navigateur

Dans l'onglet **Network** :
1. Cliquez sur la requête vers `/v1/ocr/upload`
2. Onglet **Headers**
3. Section **Request Headers**
4. Cherchez `X-RapidAPI-Proxy-Secret`

**Si le header n'est PAS présent** :
- Le problème vient de l'envoi axios
- Rebuild nécessaire après les corrections

**Si le header EST présent** :
- Vérifiez que la valeur correspond EXACTEMENT à celle dans Railway
- Pas d'espaces avant/après
- Même casse (minuscules/majuscules)

### 3. Test avec curl (pour comparer)

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/v1/ocr/upload" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_CLE_ICI" \
  -F "file=@votre_facture.jpg" \
  -F "language=fra"
```

Si curl fonctionne mais pas l'interface, le problème vient de l'envoi axios.

### 4. Rebuild après corrections

```bash
cd demo
npm run build
cd ..
git add demo/dist/
git commit -m "Fix header sending"
git push
```



