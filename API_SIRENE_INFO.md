# 📚 Informations API Sirene (Insee)

## ✅ API Sirene est GRATUITE

L'API Sirene de l'Insee est **entièrement gratuite** et accessible à tous.

## 🔗 Portail officiel

**Nouvelle URL** : https://portail-api.insee.fr/

⚠️ **Note** : L'ancienne URL `https://api.insee.fr/` est dépréciée. Utilisez le nouveau portail.

## 📋 Comment obtenir l'accès

### 1. Créer un compte

1. Allez sur https://portail-api.insee.fr/
2. Cliquez sur "Créer un compte" ou "S'inscrire"
3. Remplissez le formulaire d'inscription
4. Confirmez votre email

### 2. Souscrire à l'API Sirene

1. Une fois connecté, recherchez "API Sirene" dans le catalogue
2. Cliquez sur "Souscrire" ou "S'abonner"
3. Acceptez les conditions d'utilisation
4. Une clé API vous sera fournie

### 3. Obtenir vos identifiants

Après souscription, vous obtiendrez :

**Pour OAuth2 (recommandé)** :
- **Type** : `web` (ou autre selon votre application)
- **Client ID** (identifiant de l'application) - **Obligatoire** pour plans OAuth2/JWT
- **Types de droits autorisés** : **Client Credentials** - **OBLIGATOIRE** (cocher lors de la création)
- **Client Certificate (PEM)** (certificat client au format PEM) - **Obligatoire** pour authentification mutual TLS
- **Client Metadata** (optionnel) - Métadonnées personnalisées clé-valeur

**Ancien système (Consumer Key/Secret)** :
- **Consumer Key** (clé API)
- **Consumer Secret** (secret API)

⚠️ **Note** : Le nouveau système OAuth2 avec Client ID et Client Certificate (PEM) est **obligatoire** pour certains plans API (OAuth2, JWT). Le système Consumer Key/Secret peut être encore disponible pour certains plans plus anciens.

Ces identifiants sont nécessaires pour l'authentification OAuth2.

## 📊 Données disponibles

L'API Sirene donne accès à :
- **25 millions d'entreprises** enregistrées
- **36 millions d'établissements**
- Données mises à jour **quotidiennement**
- Historique depuis **1973**

### Informations pour chaque SIRET/SIREN

- Raison sociale
- Adresse complète
- Forme juridique (SARL, SAS, SA, etc.)
- Date de création
- Activité principale (code APE/NAF)
- Statut (actif/inactif)
- Effectifs
- Capital social
- Date de cessation d'activité (si applicable)
- Et plus...

## 🔐 Authentification

L'API Sirene utilise **OAuth2** avec deux méthodes possibles :

### Méthode 1 : Client ID + Client Certificate (PEM) ⭐ Recommandé

1. Obtenir un token d'accès avec :
   - **Client ID** (Type: web)
   - **Client Certificate (PEM)** (certificat au format PEM)
2. Utiliser le token pour les requêtes API
3. Le token expire (généralement après 1 heure)
4. Renouveler le token si nécessaire

### Méthode 2 : Consumer Key/Secret (ancien système)

1. Obtenir un token d'accès avec Consumer Key/Secret
2. Utiliser le token pour les requêtes API
3. Le token expire
4. Renouveler le token si nécessaire

**Note** : Certains plans API nécessitent obligatoirement le Client ID + Client Certificate.

## 📝 Limites

- ✅ **Gratuit** pour usage standard
- ✅ Pas de limite de volume pour usage raisonnable
- ⚠️ Rate limiting modéré (détails sur le portail)
- ✅ Clé API valide **indéfiniment** (pas d'expiration)

## 🔧 Configuration dans votre API

Dans votre fichier `.env` :

**Option 1 : OAuth2 avec Client ID + Certificate (recommandé)** :
```env
# Client ID obtenu sur le portail (Type: web)
SIRENE_CLIENT_ID=votre_client_id_ici

# Chemin vers le certificat PEM téléchargé depuis le portail
SIRENE_CLIENT_CERTIFICATE=/chemin/vers/certificat.pem
# Ou contenu du certificat directement (pour certains déploiements)
# SIRENE_CLIENT_CERTIFICATE_CONTENT="-----BEGIN CERTIFICATE-----\n..."
```

**Note** : Le certificat PEM est téléchargé depuis le portail lors de la création de votre application.

**Option 2 : Consumer Key/Secret (ancien système)** :
```env
SIRENE_API_KEY=votre_consumer_key_ici
SIRENE_API_SECRET=votre_consumer_secret_ici
```

**Note** : Vérifiez sur le portail quel type d'authentification est requis pour votre plan API.

## 📚 Documentation

- **Portail API** : https://portail-api.insee.fr/
- **Documentation Sirene** : https://www.sirene.fr/
- **Guide de connexion** : Disponible sur le portail après inscription

## 💡 Note technique

✅ **L'intégration API Sirene est maintenant complètement implémentée** dans `compliance.py`.

La fonction `enrich_siren_siret()` :
- ✅ Obtient automatiquement le token OAuth2 (avec cache pour éviter les requêtes répétées)
- ✅ Fait les requêtes vers l'API Sirene v3
- ✅ Parse et structure les données retournées
- ✅ Gère les erreurs et les cas limites
- ✅ Supporte les deux méthodes d'authentification (Client ID + Certificate et Consumer Key/Secret)

### Méthode d'authentification OAuth2 (Client ID + Certificate)

L'implémentation actuelle :
1. **Obtient le token OAuth2** automatiquement :
   - Endpoint : `https://portail-api.insee.fr/token`
   - Méthode : POST avec certificat client (mutual TLS)
   - Cache le token pour éviter les requêtes répétées
   - Renouvelle automatiquement le token si expiré

2. **Utilise le token** pour les requêtes :
   - Header : `Authorization: Bearer {access_token}`
   - Requêtes vers l'API Sirene v3

3. **Requête API Sirene** :
   - Endpoint : `https://api.insee.fr/entreprises/sirene/v3/siret/{siret}`
   - Méthode : GET
   - Header : `Authorization: Bearer {access_token}`

4. **Parse la réponse JSON** et extrait automatiquement :
   - Raison sociale
   - Adresse complète
   - Code postal et ville
   - Activité principale (code APE/NAF)
   - Forme juridique
   - Statut (Actif/Inactif)
   - Date de création
   - Date de cessation (si applicable)
   - Tranche d'effectifs

### Méthode Consumer Key/Secret (ancien système)

L'implémentation actuelle :
1. ✅ Obtient le token OAuth2 avec Consumer Key/Secret (Basic Auth)
2. ✅ Cache le token pour optimiser les performances
3. ✅ Fait les requêtes vers l'API Sirene
4. ✅ Parse les réponses JSON
5. ✅ Gère les erreurs et le refresh des tokens

## ✅ Résumé

- ✅ **Gratuit** : Pas de coût
- ✅ **Officiel** : API publique de l'Insee
- ✅ **Complet** : Données exhaustives sur les entreprises françaises
- ✅ **À jour** : Mises à jour quotidiennes
- ✅ **Simple** : Inscription gratuite sur le portail

**Portail** : https://portail-api.insee.fr/

