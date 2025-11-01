# ✅ Checklist - Configuration API Sirene

## 📋 Configuration complète étape par étape

### Étape 1 : Créer un compte

- [ ] Aller sur https://portail-api.insee.fr/
- [ ] Cliquer sur "Créer un compte" ou "S'inscrire"
- [ ] Remplir le formulaire d'inscription
- [ ] Confirmer l'email reçu
- [ ] Se connecter au portail

### Étape 2 : Créer une application

- [ ] Aller dans "Mes applications" ou "Applications"
- [ ] Cliquer sur "Créer une application"
- [ ] Remplir le formulaire :
  - [ ] **Nom** : Ex: "OCR Facture API"
  - [ ] **Type** : `web` (ou sélectionner le type approprié)
  - [ ] **Description** : Description de votre utilisation

### Étape 3 : Configurer les droits ⚠️ CRITIQUE

- [ ] Dans "Types de droits autorisés pour le client" :
  - [ ] ✅ **COCHER "Client Credentials"** (obligatoire)
  - [ ] ⚠️ **NE PAS COCHER** les autres types si non nécessaires (sécurité)
  - [ ] Vérifier que seul "Client Credentials" est coché

**Valeurs exactes** :
- ☑️ Client Credentials (COCHER)
- ☐ Authorization Code (NE PAS COCHER)
- ☐ Implicit (NE PAS COCHER)
- ☐ Refresh Token (NE PAS COCHER)

**⚠️ Important sécurité** : Ne cocher QUE les types dont vous avez besoin (principe de moindre privilège).

### Étape 4 : Client Metadata (optionnel)

**Option A : Laisser vide** (recommandé si pas besoin)
- [ ] Ne rien remplir dans "Add Client Metadata"
- [ ] Passer à l'étape suivante

**Option B : Ajouter des métadonnées** (pour organisation)
- [ ] Cliquer sur "Add Client Metadata" ou "+"
- [ ] Metadata key : `environment`
- [ ] Metadata value : `production` (ou `development`, `staging`)
- [ ] (Optionnel) Ajouter une deuxième métadonnée :
  - [ ] Metadata key : `project`
  - [ ] Metadata value : `ocr-facture-api`

### Étape 5 : Client Certificate (PEM)

- [ ] **LAISSER VIDE** - Le certificat sera généré automatiquement
- [ ] Ne rien remplir dans ce champ maintenant
- [ ] Après création de l'application :
  - [ ] Aller dans les détails de l'application
  - [ ] **Télécharger le certificat PEM**
  - [ ] Sauvegarder le certificat dans un endroit sécurisé (ex: `certs/sirene-cert.pem`)
  - [ ] Noter le chemin du certificat pour `.env`

### Étape 6 : Valider la création

- [ ] Cliquer sur "Créer" ou "Valider"
- [ ] Vérifier que l'application apparaît dans la liste
- [ ] Noter le **Client ID** affiché

### Étape 7 : Souscrire à l'API Sirene

- [ ] Rechercher "API Sirene" dans le catalogue
- [ ] Cliquer sur l'API Sirene
- [ ] Cliquer sur "Souscrire" ou "S'abonner"
- [ ] Sélectionner votre application créée
- [ ] Accepter les conditions d'utilisation
- [ ] Confirmer la souscription

### Étape 8 : Configurer dans votre projet

- [ ] Créer/modifier le fichier `.env`
- [ ] Ajouter les variables :

```env
# Client ID (obtenu dans les détails de l'application)
SIRENE_CLIENT_ID=votre_client_id_ici

# Chemin vers le certificat PEM téléchargé
SIRENE_CLIENT_CERTIFICATE=/chemin/vers/certificat.pem
```

- [ ] Vérifier que le chemin du certificat est correct
- [ ] Vérifier les permissions du fichier certificat (chmod 600 recommandé)

### Étape 9 : Sécurité

- [ ] Ajouter `*.pem` dans `.gitignore`
- [ ] Vérifier que le certificat n'est pas dans Git
- [ ] En production, utiliser des variables d'environnement sécurisées
- [ ] Limiter les permissions du fichier certificat

### Étape 10 : Test

- [ ] Vérifier que les variables sont chargées :
  ```python
  from config import settings
  print(settings.sirene_client_id)
  print(settings.sirene_client_certificate)
  ```

- [ ] Tester la fonction (actuellement retourne une structure prête) :
  ```python
  from compliance import enrich_siren_siret
  result = enrich_siren_siret(
      "12345678901234",
      siren_client_id=settings.sirene_client_id,
      siren_client_certificate=settings.sirene_client_certificate
  )
  print(result)
  ```

## 📝 Informations à noter

Après configuration, vous devriez avoir :

- ✅ **Client ID** : `...` (à sauvegarder)
- ✅ **Client Certificate** : `/chemin/vers/certificat.pem` (fichier téléchargé)
- ✅ **Application créée** : Nom visible dans le portail
- ✅ **Souscription API Sirene** : Confirmée

## 🔒 Sécurité - Checklist

- [ ] Certificat PEM sauvegardé de manière sécurisée
- [ ] Certificat ajouté à `.gitignore`
- [ ] Certificat non commité dans Git
- [ ] Permissions du fichier limitées (chmod 600)
- [ ] Variables d'environnement utilisées (pas de valeurs en dur)
- [ ] Client ID et certificat non partagés publiquement

## ✅ Vérification finale

- [ ] Application créée sur le portail
- [ ] Type de droits : "Client Credentials" coché
- [ ] API Sirene souscrite
- [ ] Client ID noté
- [ ] Certificat PEM téléchargé et sauvegardé
- [ ] Variables configurées dans `.env`
- [ ] Code mis à jour pour utiliser les nouvelles variables
- [ ] Tests de configuration effectués

---

**Une fois toutes ces étapes complétées, votre configuration API Sirene sera prête !** 🎉

