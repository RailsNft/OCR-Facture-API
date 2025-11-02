# 🔑 Comment Obtenir vos Tokens API pour Automatisation

## 🎯 Pourquoi des tokens ?

Pour que je puisse publier automatiquement sur Hootsuite/Twitter/LinkedIn, j'ai besoin de vos **tokens d'accès API**.

**C'est sécurisé** : Les tokens donnent accès uniquement à poster (pas supprimer, pas lire DM privés).

---

## 🚀 OPTION 1 : API Twitter Directe (RECOMMANDÉ)

### Pourquoi Twitter direct ?
- ✅ **GRATUIT illimité** (plan Free and Hobby)
- ✅ Plus simple que Hootsuite API
- ✅ Contrôle total

### Étapes pour obtenir votre token :

#### 1. Créer une App Twitter (5 min)

1. Allez sur : https://developer.twitter.com/en/portal/dashboard
2. Cliquez **"Sign up"** ou **"Create App"**
3. Créez un projet :
   - **Name** : OCR Facture Marketing Bot
   - **Use case** : Making a bot
   - **Description** : Automated marketing posts for OCR Facture API

4. Créez votre App :
   - **App name** : ocr-facture-bot
   - **Description** : Marketing automation
   - **Website** : https://rapidapi.com/pmouniama/api/ocrfactureapi

#### 2. Obtenir vos clés (2 min)

Une fois l'app créée :

1. Cliquez sur **"Keys and Tokens"**
2. Vous verrez :
   - ✅ **API Key** (Consumer Key)
   - ✅ **API Secret** (Consumer Secret)
   - ✅ **Bearer Token**

3. Cliquez **"Generate"** pour :
   - ✅ **Access Token**
   - ✅ **Access Token Secret**

**⚠️ NOTEZ CES 4 VALEURS QUELQUE PART (elles ne s'afficheront qu'une fois)**

#### 3. Configurer les permissions (Important !)

1. Dans l'onglet **"Settings"**
2. Sous **"App permissions"**, cliquez **"Edit"**
3. Sélectionnez **"Read and Write"** (pas "Read only")
4. Sauvegardez

#### 4. Configuration dans votre système

Créez un fichier `.env` dans `/marketing/` :

```bash
# Twitter API v2
TWITTER_API_KEY=votre_api_key_ici
TWITTER_API_SECRET=votre_api_secret_ici
TWITTER_ACCESS_TOKEN=votre_access_token_ici
TWITTER_ACCESS_SECRET=votre_access_secret_ici
TWITTER_BEARER_TOKEN=votre_bearer_token_ici
```

#### 5. Tester l'automatisation

```bash
cd marketing/
pip install tweepy
python auto-publish-all.py
```

**Boom ! Tous vos posts Twitter seront programmés automatiquement ! 🚀**

---

## 🔷 OPTION 2 : API LinkedIn

### Étapes (un peu plus complexe) :

1. Créer une App LinkedIn : https://www.linkedin.com/developers/apps/new
2. Obtenir les permissions :
   - `w_member_social` (poster)
   - `r_basicprofile` (lire profil)
3. OAuth2 flow pour obtenir token
4. Token valide 60 jours (à renouveler)

**💡 Plus simple : Utiliser Hootsuite pour LinkedIn**

---

## 🟢 OPTION 3 : API Hootsuite (Multi-plateforme)

### Avantages :
- ✅ Gère Twitter + LinkedIn depuis un seul endroit
- ✅ Pas besoin de gérer plusieurs APIs

### Inconvénients :
- ❌ Nécessite App Hootsuite (complexe)
- ❌ Limites du plan gratuit

### Étapes :

1. **Créer une Hootsuite App** : https://hootsuite.com/developers
2. S'inscrire au programme développeur
3. Créer une application
4. Obtenir Access Token
5. Configurer OAuth2

**📚 Doc** : https://developer.hootsuite.com/docs/getting-started

---

## 💡 RECOMMANDATION

### Pour démarrer RAPIDEMENT (5 minutes) :

**Option A : Twitter API directe**
- Simple, gratuit, rapide
- Seulement pour Twitter
- LinkedIn à faire manuellement (ou via Hootsuite interface)

**Option B : Bulk CSV Hootsuite** ⭐ **LE PLUS SIMPLE**
- Pas besoin de token API !
- Générez CSV avec le script
- Uploadez dans Hootsuite interface
- TOUS vos posts programmés en 1 clic

---

## 🚀 MÉTHODE ULTRA-RAPIDE (Sans Token - 5 min)

### Utilisez le Bulk CSV !

```bash
cd marketing/
python auto-publish-all.py
# Choisissez option 1 : Générer CSV
```

**Résultat** : Fichier `hootsuite_posts.csv` créé

**Ensuite** :
1. Ouvrez Hootsuite
2. Publisher → Bulk Composer
3. Upload CSV
4. Cliquez "Schedule All"

**BOOM ! 30 posts programmés en 30 secondes ! 🎉**

---

## ✅ CONCLUSION

### Vous avez 3 choix :

1. **CSV Bulk Upload** (5 min, pas de token) ⭐ **RECOMMANDÉ**
2. **Twitter API** (15 min, gratuit, automatique)
3. **Manuel Hootsuite** (30 min, copier-coller)

**Je recommande CSV Bulk Upload pour démarrer rapidement !**

---

## 🎯 PROCHAINE ÉTAPE

**Exécutez maintenant** :

```bash
cd marketing/
python auto-publish-all.py
```

Choisissez option 1, uploadez le CSV dans Hootsuite, et c'est FAIT ! 🚀

