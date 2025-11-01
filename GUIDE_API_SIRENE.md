# 🔐 Guide complet - Configuration API Sirene (Insee)

## 📋 Étape par étape

### 1. Créer un compte sur le portail

1. Allez sur **https://portail-api.insee.fr/**
2. Cliquez sur "Créer un compte" ou "S'inscrire"
3. Remplissez le formulaire
4. Confirmez votre email

### 2. Créer une application

1. Une fois connecté, allez dans "Mes applications" ou "Applications"
2. Cliquez sur "Créer une application"
3. Remplissez les informations :
   - **Nom de l'application** : Ex: "OCR Facture API"
   - **Type** : `web` (ou autre selon votre besoin)
   - **Description** : Description de votre utilisation

4. **Configurer les types de droits autorisés** ⚠️ **IMPORTANT** :
   - ✅ Cochez **"Client Credentials"** (nécessaire pour OAuth2)
   - ⚠️ Ne cochez **QUE** les types dont vous avez besoin (sécurité)
   - Laissez les autres non cochés si non nécessaires

5. **Add Client Metadata** (optionnel) :
   - Vous pouvez ajouter des métadonnées personnalisées
   - Exemple : `environment=production`, `project=ocr-facture-api`
   - Format : Clé-valeur

6. **Client Certificate (PEM)** :
   - Le certificat sera généré automatiquement lors de la création
   - Vous pourrez le télécharger après création
   - Format : Fichier `.pem`

7. Validez la création

### 3. Souscrire à l'API Sirene

1. Recherchez "API Sirene" dans le catalogue
2. Cliquez sur l'API Sirene
3. Cliquez sur "Souscrire" ou "S'abonner"
4. Sélectionnez votre application créée précédemment
5. Acceptez les conditions d'utilisation

### 4. Obtenir vos identifiants

Après souscription, vous obtiendrez :

#### Pour OAuth2 (recommandé) :

- **Client ID** : Identifiant unique de votre application
  - Format : Chaîne de caractères
  - **Obligatoire** pour plans OAuth2/JWT
  - Visible dans les détails de votre application
  - Généré automatiquement lors de la création

- **Types de droits autorisés** :
  - ✅ **Client Credentials** : **OBLIGATOIRE** - Cochez cette option
  - ⚠️ **Important** : Ne cochez QUE les types dont vous avez besoin (principe de moindre privilège)
  - Les autres types (Authorization Code, etc.) ne sont généralement pas nécessaires pour une API backend

- **Client Certificate (PEM)** : Certificat client
  - Format : Fichier `.pem` ou `.crt`
  - **Obligatoire** pour authentification mutual TLS
  - Généré automatiquement lors de la création de l'application
  - Téléchargeable depuis le portail après création
  - Contient la clé privée et le certificat
  - ⚠️ **Sécurité** : Ne partagez jamais ce certificat

- **Client Metadata** (optionnel) :
  - Métadonnées personnalisées sous forme clé-valeur
  - Utile pour organiser vos applications
  - Exemples : `environment=production`, `project=ocr-facture-api`

#### Pour Consumer Key/Secret (ancien système) :

- **Consumer Key** : Clé API
- **Consumer Secret** : Secret API

## 🔧 Configuration dans votre projet

### Option 1 : Client ID + Certificate (PEM) ⭐ Recommandé

#### Étape 1 : Télécharger le certificat

1. Dans le portail, allez dans les détails de votre application
2. Téléchargez le certificat PEM
3. Sauvegardez-le dans un endroit sécurisé (ex: `certs/sirene-cert.pem`)

#### Étape 2 : Configurer dans `.env`

```env
# Client ID (obtenu sur le portail)
SIRENE_CLIENT_ID=votre_client_id_ici

# Chemin vers le certificat PEM
SIRENE_CLIENT_CERTIFICATE=/chemin/absolu/vers/certificat.pem
# Ou chemin relatif depuis la racine du projet
# SIRENE_CLIENT_CERTIFICATE=./certs/sirene-cert.pem
```

#### Étape 3 : Sécuriser le certificat

⚠️ **Important** : Le certificat contient des informations sensibles. 

- ✅ Ne jamais commiter le certificat dans Git
- ✅ Ajouter `*.pem` dans `.gitignore`
- ✅ Utiliser des variables d'environnement en production
- ✅ Limiter les permissions du fichier (chmod 600)

### Option 2 : Consumer Key/Secret (ancien système)

```env
SIRENE_API_KEY=votre_consumer_key_ici
SIRENE_API_SECRET=votre_consumer_secret_ici
```

## 🔐 Authentification OAuth2 avec Client Certificate

### Principe

L'authentification utilise **mutual TLS** (mTLS) avec **Client Credentials** :
- Le client présente son certificat au serveur
- Le serveur vérifie que le certificat correspond au Client ID
- Le serveur vérifie que "Client Credentials" est autorisé pour cette application
- Un token OAuth2 est émis si la vérification réussit

**Type de grant OAuth2** : `client_credentials` (machine-to-machine, pas d'utilisateur final)

### Flux d'authentification

```
1. Client fait POST vers https://portail-api.insee.fr/token
   - Avec certificat client (mutual TLS)
   - Body: grant_type=client_credentials
   
2. Serveur vérifie le certificat et le Client ID
   
3. Serveur retourne access_token
   
4. Client utilise access_token dans les requêtes API
   - Header: Authorization: Bearer {access_token}
```

## 📝 Exemple d'implémentation Python

```python
import requests
import os
from pathlib import Path

# Configuration
CLIENT_ID = os.getenv("SIRENE_CLIENT_ID")
CERTIFICATE_PATH = os.getenv("SIRENE_CLIENT_CERTIFICATE")

# 1. Obtenir le token OAuth2
token_url = "https://portail-api.insee.fr/token"
response = requests.post(
    token_url,
    data={"grant_type": "client_credentials"},
    cert=CERTIFICATE_PATH,  # Mutual TLS avec certificat
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

access_token = response.json()["access_token"]

# 2. Utiliser le token pour requête API Sirene
siret = "12345678901234"
api_url = f"https://api.insee.fr/entreprises/sirene/v3/siret/{siret}"

response = requests.get(
    api_url,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
)

data = response.json()
print(data)
```

## ✅ Vérification

Pour vérifier que votre configuration fonctionne :

1. Vérifiez que les variables d'environnement sont chargées :
   ```python
   from config import settings
   print(settings.sirene_client_id)
   print(settings.sirene_client_certificate)
   ```

2. Testez la fonction `enrich_siren_siret()` :
   ```python
   from compliance import enrich_siren_siret
   result = enrich_siren_siret(
       "12345678901234",
       siren_client_id=settings.sirene_client_id,
       siren_client_certificate=settings.sirene_client_certificate
   )
   print(result)
   ```

## 🚨 Dépannage

### Erreur : "Certificat non trouvé"

- Vérifiez que le chemin vers le certificat est correct
- Utilisez un chemin absolu plutôt que relatif
- Vérifiez les permissions du fichier
- Vérifiez que le fichier existe bien

### Erreur : "Client ID invalide"

- Vérifiez que le Client ID est correct
- Assurez-vous que l'application est bien souscrite à l'API Sirene
- Vérifiez que le Client ID correspond bien à l'application créée

### Erreur : "Mutual TLS failed"

- Vérifiez que le certificat PEM est valide
- Assurez-vous que le certificat correspond au Client ID
- Vérifiez que le certificat n'a pas expiré
- Vérifiez que le certificat est bien celui téléchargé depuis le portail

### Erreur : "Client Credentials not authorized" ou "Invalid grant type"

- ⚠️ **Vérifiez que "Client Credentials" est bien coché** dans les types de droits autorisés
- Retournez dans les détails de votre application sur le portail
- Vérifiez que "Client Credentials" est dans la liste des droits autorisés
- Si non, modifiez l'application pour ajouter ce droit

### Erreur : "Unauthorized" ou "401"

- Vérifiez que l'application est bien souscrite à l'API Sirene
- Vérifiez que la souscription est active
- Vérifiez que le token OAuth2 est valide et non expiré

## 📚 Ressources

- **Portail API** : https://portail-api.insee.fr/
- **Documentation API Sirene** : https://api.insee.fr/doc/entreprise/
- **Guide OAuth2 Insee** : Disponible sur le portail

## 🔒 Sécurité

- ✅ Utilisez HTTPS pour toutes les communications
- ✅ Stockez le certificat de manière sécurisée
- ✅ Ne partagez jamais votre Client ID ou certificat
- ✅ Utilisez des variables d'environnement en production
- ✅ Limitez les permissions du fichier certificat

---

**Note** : Ce guide sera mis à jour quand l'intégration complète OAuth2 sera implémentée dans le code.

