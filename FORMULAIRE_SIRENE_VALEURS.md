# 📝 Valeurs à remplir - Formulaire création application API Sirene

## ✅ Guide rapide - Que mettre dans chaque champ

### 🔐 Types de droits autorisés pour le client

**Que cocher ?**

✅ **COCHER UNIQUEMENT** :
- ☑️ **Client Credentials** (obligatoire)

❌ **NE PAS COCHER** (si non nécessaires) :
- ☐ Authorization Code
- ☐ Implicit
- ☐ Refresh Token
- ☐ Autres types

**Pourquoi ?**
- Votre API backend utilise l'authentification machine-to-machine (pas d'utilisateur final)
- "Client Credentials" est le seul type nécessaire pour ce cas d'usage
- Ne cocher que ce dont vous avez besoin = meilleure sécurité (principe de moindre privilège)

---

### 📋 Add Client Metadata (optionnel)

**Que mettre ?**

**Option 1 : Laisser vide** (si vous n'avez pas besoin de métadonnées)
- Ne rien remplir
- Cliquer sur "Suivant" ou "Créer"

**Option 2 : Ajouter des métadonnées** (pour organisation)

**Exemple 1 - Environnement** :
- **Metadata key** : `environment`
- **Metadata value** : `production`
- (ou `development`, `staging`, etc.)

**Exemple 2 - Projet** :
- **Metadata key** : `project`
- **Metadata value** : `ocr-facture-api`

**Exemple 3 - Les deux** :
- Première métadonnée :
  - **Metadata key** : `environment`
  - **Metadata value** : `production`
- Deuxième métadonnée (cliquer "Add" ou "+") :
  - **Metadata key** : `project`
  - **Metadata value** : `ocr-facture-api`

**Autres exemples de clés utiles** :
- `service` → `ocr-api`
- `team` → `backend`
- `version` → `3.0.0`
- `purpose` → `invoice-enrichment`

**Note** : Les métadonnées sont optionnelles et servent uniquement à organiser vos applications. Vous pouvez laisser vide si vous n'en avez pas besoin.

---

### 🔒 Client Certificate (PEM)

**Que faire ?**

✅ **Laisser tel quel** - Le certificat sera généré automatiquement

**Ce qui se passe** :
1. Le certificat PEM est généré automatiquement lors de la création de l'application
2. Vous pourrez le télécharger **après** la création
3. Pas besoin de remplir quoi que ce soit dans ce champ maintenant

**Après la création** :
- Allez dans les détails de votre application
- Cliquez sur "Télécharger le certificat" ou équivalent
- Sauvegardez le fichier `.pem` dans un endroit sécurisé
- Vous l'utiliserez ensuite dans votre `.env` avec `SIRENE_CLIENT_CERTIFICATE`

---

## 📝 Récapitulatif - Formulaire complet

### Champs à remplir :

1. **Nom de l'application** :
   ```
   OCR Facture API
   ```
   (ou le nom que vous préférez)

2. **Type** :
   ```
   web
   ```
   (ou sélectionner dans la liste déroulante)

3. **Description** (optionnel) :
   ```
   API pour extraction et enrichissement de données de factures françaises
   ```

4. **Types de droits autorisés** :
   ☑️ **Client Credentials** uniquement

5. **Client Metadata** (optionnel) :
   - Laisser vide OU
   - Ajouter :
     - Key: `environment` → Value: `production`
     - Key: `project` → Value: `ocr-facture-api`

6. **Client Certificate (PEM)** :
   - Laisser vide (généré automatiquement)

7. **Valider/Créer** :
   - Cliquer sur "Créer" ou "Valider"

---

## ✅ Après la création

Une fois l'application créée, vous obtiendrez :

1. **Client ID** → À noter et mettre dans `.env` :
   ```env
   SIRENE_CLIENT_ID=votre_client_id_ici
   ```

2. **Client Certificate (PEM)** → À télécharger et sauvegarder :
   - Télécharger le fichier `.pem`
   - Sauvegarder dans un dossier sécurisé (ex: `certs/sirene-cert.pem`)
   - Ajouter dans `.env` :
     ```env
     SIRENE_CLIENT_CERTIFICATE=/chemin/vers/certificat.pem
     ```

---

## 🎯 Exemple complet de formulaire rempli

```
┌─────────────────────────────────────────┐
│ Créer une application                   │
├─────────────────────────────────────────┤
│ Nom* : OCR Facture API                  │
│ Type* : web                             │
│ Description : API extraction factures   │
│                                         │
│ Types de droits autorisés :             │
│ ☑️ Client Credentials                    │
│ ☐ Authorization Code                    │
│ ☐ Implicit                              │
│ ☐ Refresh Token                         │
│                                         │
│ Client Metadata (optionnel) :           │
│ Key: environment                        │
│ Value: production                       │
│                                         │
│ Client Certificate (PEM) :              │
│ [Généré automatiquement]                │
│                                         │
│ [Créer] [Annuler]                       │
└─────────────────────────────────────────┘
```

---

## ⚠️ Erreurs courantes à éviter

❌ **Ne PAS cocher plusieurs types** si vous n'en avez pas besoin
- Exemple : Ne pas cocher "Authorization Code" si vous utilisez seulement "Client Credentials"
- Raison : Sécurité (moindre privilège)

❌ **Ne PAS oublier de cocher "Client Credentials"**
- Si non coché, l'authentification OAuth2 ne fonctionnera pas
- Vous aurez une erreur "Invalid grant type"

✅ **OK de laisser Client Metadata vide**
- C'est optionnel
- Vous pouvez toujours l'ajouter plus tard

✅ **OK de laisser Client Certificate vide**
- Il sera généré automatiquement
- Vous le téléchargerez après création

---

**Une fois le formulaire rempli, cliquez sur "Créer" et notez votre Client ID !** 🎉



