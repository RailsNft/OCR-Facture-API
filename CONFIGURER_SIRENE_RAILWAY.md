# 🔧 Configurer API Sirene sur Railway

## ✅ Oui, vous devez ajouter les variables Sirene sur Railway !

Pour que l'enrichissement Sirene fonctionne en production, vous devez configurer les variables d'environnement sur Railway.

---

## 📋 Méthode 1 : OAuth2 avec Client ID + Certificate (RECOMMANDÉ)

Si vous avez créé une application avec **Client ID** et **certificat PEM** :

### Étapes sur Railway :

1. **Allez sur votre projet Railway** : https://railway.app/project/[votre-projet]

2. **Cliquez sur votre service** (ex: `ocr-facture-api-production`)

3. **Allez dans l'onglet "Variables"**

4. **Ajoutez ces 2 variables** :

   ```
   SIRENE_CLIENT_ID=votre_client_id_ici
   ```

   **Pour le certificat, vous avez 2 options :**

   **Option A : Contenu du certificat directement** (RECOMMANDÉ pour Railway)
   ```
   SIRENE_CLIENT_CERTIFICATE=-----BEGIN CERTIFICATE-----
   MIIFbTCCA1WgAwIBAgIJAK...
   [contenu complet du certificat]
   -----END CERTIFICATE-----
   ```

   **Option B : Chemin vers le fichier** (si vous avez uploadé le certificat)
   ```
   SIRENE_CLIENT_CERTIFICATE=/app/certs/sirene-cert.pem
   ```

5. **Sauvegardez** - Railway redéploiera automatiquement

---

## 📋 Méthode 2 : Consumer Key/Secret (Ancien système)

Si vous utilisez l'ancien système avec **Consumer Key** et **Consumer Secret** :

### Étapes sur Railway :

1. **Allez sur votre projet Railway** : https://railway.app/project/[votre-projet]

2. **Cliquez sur votre service**

3. **Allez dans l'onglet "Variables"**

4. **Ajoutez ces 2 variables** :

   ```
   SIRENE_API_KEY=votre_consumer_key_ici
   SIRENE_API_SECRET=votre_consumer_secret_ici
   ```

5. **Sauvegardez** - Railway redéploiera automatiquement

---

## 🎯 Quelle méthode utiliser ?

- **Si vous avez créé une nouvelle application récemment** → Utilisez **Méthode 1** (OAuth2 avec Client ID + Certificate)
- **Si vous avez une ancienne application** → Utilisez **Méthode 2** (Consumer Key/Secret)

---

## ⚠️ Important pour le certificat PEM

### Option recommandée : Contenu du certificat dans la variable

Copiez-collez **tout le contenu** du fichier `.pem` dans la variable `SIRENE_CLIENT_CERTIFICATE` :

```
SIRENE_CLIENT_CERTIFICATE=-----BEGIN CERTIFICATE-----
MIIFbTCCA1WgAwIBAgIJAK...
[plusieurs lignes]
-----END CERTIFICATE-----
```

**Note** : Les sauts de ligne seront préservés automatiquement par Railway.

### Alternative : Upload du fichier (avancé)

Si vous préférez uploader le fichier :

1. Créez un dossier `certs/` dans votre projet
2. Ajoutez le certificat : `certs/sirene-cert.pem`
3. Dans Railway, configurez : `SIRENE_CLIENT_CERTIFICATE=/app/certs/sirene-cert.pem`
4. Assurez-vous que le fichier est bien commité dans Git

---

## ✅ Vérification

Une fois configuré, testez l'enrichissement :

```bash
curl -X POST "https://ocr-facture-api-production.up.railway.app/compliance/enrich-siret" \
  -H "X-RapidAPI-Proxy-Secret: votre-secret" \
  -H "Content-Type: application/json" \
  -d '{"siret": "47945319300043"}'
```

**Réponse attendue** :
```json
{
  "success": true,
  "enrichment": {
    "success": true,
    "siret": "47945319300043",
    "raison_sociale": "Nom de l'entreprise",
    "adresse_complete": "123 Rue Example, 75001 Paris",
    ...
  }
}
```

---

## 🔒 Sécurité

- ✅ Les variables d'environnement sur Railway sont **chiffrées**
- ✅ Ne commitez **jamais** vos credentials dans Git
- ✅ Utilisez uniquement les variables d'environnement Railway

---

## 📝 Checklist

- [ ] Variables Sirene ajoutées sur Railway
- [ ] Railway a redéployé (vérifier les logs)
- [ ] Test de l'endpoint `/compliance/enrich-siret` fonctionne
- [ ] L'enrichissement fonctionne automatiquement lors de l'OCR avec `check_compliance=true`

---

**Une fois configuré, l'enrichissement Sirene fonctionnera automatiquement !** 🎉

