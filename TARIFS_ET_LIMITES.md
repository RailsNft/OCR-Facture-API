# 💰 Tarifs et Limites - OCR Facture API

## 📊 Plans de tarification RapidAPI

### Plan Free (Gratuit)
- **Prix** : 0€ / mois
- **Quota** : 10 requêtes / jour
- **Limite mensuelle** : ~300 requêtes / mois
- **Idéal pour** : Tests, développement, petits projets
- **Support** : Documentation uniquement

---

### Plan Basic
- **Prix** : 49€ / mois
- **Quota** : 2 000 requêtes / mois
- **Limite quotidienne** : ~66 requêtes / jour (moyenne)
- **Idéal pour** : Startups, petites entreprises, projets pilotes
- **Support** : Email (réponse sous 48h)

---

### Plan Pro
- **Prix** : 149€ / mois
- **Quota** : 10 000 requêtes / mois
- **Limite quotidienne** : ~333 requêtes / jour (moyenne)
- **Idéal pour** : PME, cabinets comptables moyens, intégrations ERP
- **Support** : Email prioritaire (réponse sous 24h)

---

### Plan Enterprise
- **Prix** : Sur mesure (contact commercial)
- **Quota** : >50 000 requêtes / mois (selon contrat)
- **Limite quotidienne** : Personnalisée
- **Idéal pour** : Grandes entreprises, gros volumes, besoins spécifiques
- **Support** : Support dédié, SLA garanti, DPA disponible
- **Options** : Facturation personnalisée, quotas flexibles, support technique dédié

---

## ⚙️ Limites techniques

### Limites par requête

| Type de limite | Valeur | Description |
|----------------|--------|-------------|
| **Taille fichier** | 10 Mo | Maximum par fichier uploadé |
| **Traitement batch** | 10 fichiers | Maximum de fichiers par requête `/ocr/batch` |
| **Format fichiers** | JPEG, PNG, PDF | Formats supportés |
| **Pages PDF** | Illimité | Support PDF multi-pages (toutes les pages traitées) |
| **Timeout OCR** | 30 secondes | Timeout pour traitement OCR (fichiers très volumineux) |

### Limites de débit (Rate Limiting)

| Plan | Limite | Description |
|------|--------|-------------|
| **Free** | 10 req/jour | Pas de limite par minute (quotidienne uniquement) |
| **Basic** | ~66 req/jour | Limite quotidienne moyenne (peut varier) |
| **Pro** | ~333 req/jour | Limite quotidienne moyenne (peut varier) |
| **Enterprise** | Personnalisé | Selon contrat |

**Note** : Les limites de débit peuvent être ajustées automatiquement selon la charge du serveur.

---

## 📈 Calcul du coût par requête

### Coût effectif par requête

| Plan | Coût mensuel | Requêtes / mois | Coût par requête |
|------|--------------|-----------------|------------------|
| **Free** | 0€ | 300 | **0€** |
| **Basic** | 49€ | 2 000 | **0.0245€** (~2.5 centimes) |
| **Pro** | 149€ | 10 000 | **0.0149€** (~1.5 centimes) |
| **Enterprise** | Sur mesure | >50 000 | **Négociable** |

---

## 🎯 Recommandations par usage

### Usage occasionnel (< 100 factures/mois)
**→ Plan Free**
- Parfait pour tester l'API
- 10 factures/jour suffisant
- Pas d'engagement

### Usage régulier (100-500 factures/mois)
**→ Plan Basic (49€/mois)**
- ~66 factures/jour
- Idéal pour petites entreprises
- Bon rapport qualité/prix

### Usage intensif (500-2000 factures/mois)
**→ Plan Pro (149€/mois)**
- ~333 factures/jour
- Idéal pour PME et cabinets moyens
- Support prioritaire

### Usage professionnel (>2000 factures/mois)
**→ Plan Enterprise**
- Quotas personnalisés
- Support dédié
- SLA garanti
- Contact commercial pour tarifs dégressifs

---

## ⚠️ Gestion des quotas

### Dépassement de quota

**Quand vous dépassez votre quota :**
- L'API retourne une erreur **429 (Too Many Requests)**
- Message : `"Quota exceeded. Upgrade your plan or wait for quota reset."`

**Réinitialisation :**
- **Plan Free** : Quota réinitialisé quotidiennement (à minuit UTC)
- **Plans payants** : Quota réinitialisé mensuellement (1er du mois) ou selon cycle d'abonnement

**Solutions en cas de dépassement :**
1. Attendre la réinitialisation du quota
2. Passer à un plan supérieur
3. Contacter le support pour upgrade temporaire

---

## 💡 Optimisation des coûts

### Utiliser le cache

L'API met en cache les résultats pendant **24 heures**. Si vous traitez plusieurs fois la même facture :
- **Première fois** : 1 requête comptabilisée
- **Fois suivantes** : 0 requête (servi depuis le cache)

**Économie** : Jusqu'à 100% si vous retraitez les mêmes fichiers.

### Traitement par lot

Utilisez `/ocr/batch` pour traiter plusieurs factures :
- **10 factures** = **1 requête** (au lieu de 10 requêtes séparées)
- **Économie** : 90% de requêtes économisées

**Exemple** :
- Traiter 100 factures une par une = 100 requêtes
- Traiter 100 factures par batch (10 groupes) = 10 requêtes
- **Économie : 90 requêtes**

### Planification intelligente

Pour le plan Free (10 req/jour) :
- Traiter les factures urgentes en priorité
- Grouper les factures non urgentes pour traitement batch
- Utiliser le cache pour éviter les retraitements

---

## 📊 Comparaison des plans

| Fonctionnalité | Free | Basic | Pro | Enterprise |
|----------------|------|-------|-----|------------|
| **Requêtes/mois** | 300 | 2 000 | 10 000 | >50 000 |
| **Support** | Doc | Email | Email prioritaire | Dédié + SLA |
| **Temps de réponse** | - | 48h | 24h | <4h |
| **SLA disponibilité** | - | - | - | 99.9% |
| **DPA disponible** | ❌ | ❌ | ❌ | ✅ |
| **Facturation personnalisée** | ❌ | ❌ | ❌ | ✅ |
| **Support technique dédié** | ❌ | ❌ | ❌ | ✅ |
| **Accès nouvelles features** | ✅ | ✅ | ✅ | ✅ (prioritaire) |

---

## 🔄 Politique de facturation

### Cycles de facturation

- **Tous les plans** : Facturation mensuelle
- **Paiement** : Via RapidAPI (carte bancaire, PayPal)
- **Renouvellement** : Automatique chaque mois

### Paiement et remboursement

- **Paiement** : À l'avance pour le mois en cours
- **Remboursement** : Non disponible (sauf obligation légale)
- **Résiliation** : Possible à tout moment, pas d'engagement

### Upgrade / Downgrade

- **Upgrade** : Immédiat, quota supplémentaire disponible immédiatement
- **Downgrade** : Prend effet au prochain cycle de facturation
- **Changement de plan** : Via dashboard RapidAPI

---

## 📝 Notes importantes

### Qu'est-ce qu'une "requête" ?

Une requête = **1 appel à un endpoint de l'API**, incluant :

- ✅ `POST /ocr/upload` = 1 requête
- ✅ `POST /ocr/base64` = 1 requête
- ✅ `POST /ocr/batch` = 1 requête (même avec 10 fichiers)
- ✅ `POST /compliance/check` = 1 requête
- ✅ `POST /facturx/generate` = 1 requête
- ✅ `GET /health` = 0 requête (endpoint public, non comptabilisé)
- ✅ `GET /languages` = 0 requête (endpoint public, non comptabilisé)

### Requêtes non comptabilisées

Les endpoints suivants **ne consomment pas** de quota :
- `GET /` - Informations API
- `GET /health` - État de santé
- `GET /docs` - Documentation Swagger
- `GET /languages` - Liste langues

### Cache et quota

- Les résultats servis depuis le cache **ne consomment pas** de quota supplémentaire
- Le cache est valide **24 heures**
- Le cache est partagé entre tous les utilisateurs (même fichier = même hash)

---

## 💰 Exemples de coûts réels

### Scénario 1 : Cabinet comptable petit (100 factures/mois)

- **Factures à traiter** : 100/mois
- **Plan recommandé** : Free (10/jour = 300/mois)
- **Coût mensuel** : **0€**
- **Coût par facture** : **0€**

✅ **Gratuit !**

---

### Scénario 2 : PME moyenne (500 factures/mois)

- **Factures à traiter** : 500/mois
- **Plan recommandé** : Basic (2 000/mois)
- **Coût mensuel** : **49€**
- **Coût par facture** : **0.098€** (~10 centimes)

✅ **Très économique**

---

### Scénario 3 : Cabinet comptable moyen (1 500 factures/mois)

- **Factures à traiter** : 1 500/mois
- **Plan recommandé** : Pro (10 000/mois)
- **Coût mensuel** : **149€**
- **Coût par facture** : **0.099€** (~10 centimes)

✅ **Bon rapport qualité/prix**

---

### Scénario 4 : Grande entreprise (5 000 factures/mois)

- **Factures à traiter** : 5 000/mois
- **Plan recommandé** : Enterprise (négocié)
- **Coût mensuel** : **Négociable** (ex: 300-500€)
- **Coût par facture** : **0.06-0.10€** (selon négociation)

✅ **Tarifs dégressifs pour gros volumes**

---

## 🎯 Recommandations stratégiques

### Pour tester l'API
→ **Plan Free** (0€)
- Testez pendant 1-2 semaines
- Validez que l'API répond à vos besoins
- Passez ensuite à un plan payant si nécessaire

### Pour production légère
→ **Plan Basic** (49€/mois)
- Parfait pour démarrer en production
- 2 000 requêtes/mois suffisent pour la plupart des petites entreprises
- Upgrade facile vers Pro si besoin

### Pour production sérieuse
→ **Plan Pro** (149€/mois)
- Pour PME et cabinets comptables
- 10 000 requêtes/mois = marge de sécurité
- Support prioritaire inclus

### Pour gros volumes
→ **Plan Enterprise**
- Contactez-nous pour négocier tarifs dégressifs
- Quotas personnalisés selon vos besoins
- Support dédié et SLA garanti

---

## 📞 Contact commercial

Pour les plans Enterprise ou questions tarifaires :
- Via RapidAPI : Support commercial
- Mentionnez "Plan Enterprise" ou "Tarifs personnalisés"

---

**Dernière mise à jour :** [Date actuelle]  
**Tarifs en vigueur :** [Date de mise à jour]

