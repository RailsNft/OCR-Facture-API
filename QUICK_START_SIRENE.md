# ⚡ Démarrage rapide - Configuration API Sirene

## 🎯 Configuration en 3 étapes

### Étape 1 : Obtenir vos identifiants

Récupérez vos identifiants depuis https://portail-api.insee.fr/ :
- **Client ID / Consumer Key** : UUID obtenu depuis le portail
- **Consumer Secret** : Secret obtenu depuis le portail

### Étape 2 : Configurer `.env`

Créez ou modifiez votre fichier `.env` à la racine du projet :

```env
# API Sirene - Consumer Key/Secret (ancien système)
SIRENE_API_KEY=votre_consumer_key_ici
SIRENE_API_SECRET=votre_consumer_secret_ici

# Si vous avez aussi un certificat PEM (nouveau système OAuth2)
# SIRENE_CLIENT_ID=votre_client_id_ici
# SIRENE_CLIENT_CERTIFICATE=/chemin/vers/certificat.pem
```

### Étape 3 : Vérifier la configuration

```python
from config import settings

# Vérifier que les variables sont chargées
print(f"Consumer Key: {settings.sirene_api_key}")
print(f"Consumer Secret: {'Configuré ✅' if settings.sirene_api_secret else 'Non configuré ❌'}")
```

## ✅ Test rapide

```python
from compliance import enrich_siren_siret
from config import settings

# Tester avec un SIRET (exemple)
result = enrich_siren_siret(
    "12345678901234",  # SIRET de test
    siren_api_key=settings.sirene_api_key,
    siren_api_secret=settings.sirene_api_secret
)

print(result)
# Devrait afficher la méthode d'authentification détectée
```

## 📋 Checklist

- [x] Identifiants obtenus ✅
- [ ] Variables ajoutées dans `.env`
- [ ] Vérification de la configuration
- [ ] Test de la fonction
- [ ] (Optionnel) Télécharger le certificat PEM pour OAuth2

## 🔒 Sécurité

⚠️ **Ne commitez JAMAIS** :
- Le fichier `.env`
- Les certificats `.pem`
- Ces fichiers sont déjà dans `.gitignore`

---

**Configuration prête !** Une fois l'intégration OAuth2 complète implémentée, vous pourrez enrichir automatiquement les données SIREN/SIRET. 🚀

