# 💰 Tarifs et Limites - OCR Facture API

## 📊 Plans de tarification RapidAPI

### Plan BASIC (Gratuit)
- **Prix** : $0 / mois
- **Quota** : 100 requêtes / mois
- **Limite quotidienne** : ~3-4 requêtes / jour (moyenne)
- **Factures max** : 100 factures / mois (batch désactivé)
- **Fonctionnalités** : OCR basique uniquement (pas de compliance FR, pas de Factur-X)
- **Idéal pour** : Tests, développement, évaluation de l'API
- **Support** : Documentation uniquement
- **⚠️ Limitation** : Batch processing désactivé (1 facture = 1 requête obligatoire)
- **🏆 Positionnement** : Suffisant pour tester, pas pour production (force upgrade pour usage réel)

---

### Plan PRO
- **Prix** : $15 / mois
- **Quota** : 20 000 requêtes / mois
- **Limite quotidienne** : ~666 requêtes / jour (moyenne)
- **Factures max** : ~200 000 factures / mois (avec batch 10 fichiers)
- **Fonctionnalités** : OCR complet + Compliance FR + Factur-X + Batch activé
- **Idéal pour** : Startups, petites entreprises, projets pilotes, PME
- **Support** : Email (réponse sous 48h)
- **🏆 Positionnement** : **-24% moins cher** que Microsoft OCR ($19.90) avec **+33% plus de requêtes** (20k vs 15k) + fonctionnalités françaises uniques

---

### Plan ULTRA
- **Prix** : $59 / mois
- **Quota** : 80 000 requêtes / mois
- **Limite quotidienne** : ~2 666 requêtes / jour (moyenne)
- **Factures max** : ~800 000 factures / mois (avec batch 10 fichiers)
- **Fonctionnalités** : OCR complet + Compliance FR + Factur-X + Batch activé
- **Idéal pour** : PME, cabinets comptables moyens, intégrations ERP, volumes moyens
- **Support** : Email prioritaire (réponse sous 24h)
- **🏆 Positionnement** : **-21% moins cher** que Microsoft OCR ($74.90) avec **+14% plus de requêtes** (80k vs 70k) + fonctionnalités françaises uniques

---

### Plan MEGA
- **Prix** : $149 / mois
- **Quota** : 250 000 requêtes / mois
- **Limite quotidienne** : ~8 333 requêtes / jour (moyenne)
- **Factures max** : ~2 500 000 factures / mois (avec batch 10 fichiers)
- **Fonctionnalités** : OCR complet + Compliance FR + Factur-X + Batch activé
- **Idéal pour** : Grandes entreprises, gros volumes, besoins intensifs
- **Support** : Email prioritaire (réponse sous 24h)
- **🏆 Positionnement** : **-25% moins cher** que Microsoft OCR ($199.90) avec **+25% plus de requêtes** (250k vs 200k) + fonctionnalités françaises uniques

---

## ⚙️ Limites techniques

### Limites par requête

| Type de limite | BASIC (Gratuit) | PRO / ULTRA / MEGA | Description |
|----------------|-----------------|-------------------|-------------|
| **Taille fichier** | 10 Mo | 10 Mo | Maximum par fichier uploadé |
| **Traitement batch** | ❌ **Désactivé** | ✅ **10 fichiers max** | Plan BASIC : 1 facture = 1 requête obligatoire |
| **Format fichiers** | JPEG, PNG, PDF | JPEG, PNG, PDF | Formats supportés |
| **Pages PDF** | Illimité | Illimité | Support PDF multi-pages (toutes les pages traitées) |
| **Timeout OCR** | 30 secondes | 30 secondes | Timeout pour traitement OCR (fichiers très volumineux) |
| **Compliance FR** | ❌ Désactivé | ✅ Activé | Validation TVA, SIREN/SIRET, mentions légales |
| **Factur-X** | ❌ Désactivé | ✅ Activé | Génération, parsing, validation Factur-X EN16931 |

### Limites de débit (Rate Limiting)

| Plan | Limite requêtes/jour | Factures max/jour | Description |
|------|---------------------|-------------------|-------------|
| **BASIC** | ~3-4 req/jour | ~3-4 factures/jour | Batch désactivé (1 facture = 1 requête) |
| **PRO** | ~666 req/jour | ~6 666 factures/jour | Batch activé (10 factures/requête) |
| **ULTRA** | ~2 666 req/jour | ~26 666 factures/jour | Batch activé (10 factures/requête) |
| **MEGA** | ~8 333 req/jour | ~83 333 factures/jour | Batch activé (10 factures/requête) |

**Note** : Les limites de débit peuvent être ajustées automatiquement selon la charge du serveur.

---

## 📈 Calcul du coût par requête

### Coût effectif par requête

| Plan | Coût mensuel | Requêtes / mois | Factures max/mois | Coût par requête | Coût par facture |
|------|--------------|-----------------|-------------------|------------------|-----------------|
| **BASIC** | $0 | 100 | **100** (batch désactivé) | **$0** | **$0** |
| **PRO** | $15 | 20 000 | **~200 000** (batch 10) | **$0.00075** | **$0.000075** (~0.0075 centimes) |
| **ULTRA** | $59 | 80 000 | **~800 000** (batch 10) | **$0.00074** | **$0.000074** (~0.0074 centimes) |
| **MEGA** | $149 | 250 000 | **~2 500 000** (batch 10) | **$0.00060** | **$0.000060** (~0.006 centimes) |

**Note** : Les plans payants (PRO+) permettent le batch processing (10 factures par requête), ce qui multiplie le nombre de factures traitées par 10. Le plan BASIC limite à 1 facture par requête.

**Comparaison avec Microsoft OCR (concurrence principale) :**
- Microsoft PRO : $19.90 pour 15k → **$0.00133/req**
- **Votre PRO** : $15 pour 20k → **$0.00075/req** → **-44% moins cher par requête** 🏆

---

## 🎯 Recommandations par usage

### Usage test / développement (< 100 factures/mois)
**→ Plan BASIC (Gratuit)**
- 100 requêtes/mois = ~3-4 factures/jour
- **Batch désactivé** (1 facture = 1 requête)
- OCR basique uniquement (pas de compliance, pas de Factur-X)
- Parfait pour tester et évaluer l'API
- Pas d'engagement
- **⚠️ Limité : pas suffisant pour production**

### Usage régulier (500-2 000 factures/mois)
**→ Plan PRO ($15/mois)**
- 20 000 requêtes/mois = ~666 factures/jour
- Idéal pour petites entreprises et startups
- **Meilleur rapport qualité/prix du marché**
- **-24% moins cher que Microsoft OCR**

### Usage intensif (2 000-10 000 factures/mois)
**→ Plan ULTRA ($59/mois)**
- 80 000 requêtes/mois = ~2 666 factures/jour
- Idéal pour PME et cabinets comptables moyens
- Support prioritaire
- **-21% moins cher que Microsoft OCR avec +14% de requêtes**

### Usage professionnel (>10 000 factures/mois)
**→ Plan MEGA ($149/mois)**
- 250 000 requêtes/mois = ~8 333 factures/jour
- Pour grandes entreprises et gros volumes
- **-25% moins cher que Microsoft OCR avec +25% de requêtes**

---

## ⚠️ Gestion des quotas

### Dépassement de quota

**Quand vous dépassez votre quota :**
- L'API retourne une erreur **429 (Too Many Requests)**
- Message : `"Quota exceeded. Upgrade your plan or wait for quota reset."`

**Réinitialisation :**
- **Plan BASIC** : Quota réinitialisé mensuellement (1er du mois)
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

### Traitement par lot (Plans PRO+ uniquement)

⚠️ **Le batch processing est désactivé sur le plan BASIC gratuit.**

Sur les plans payants (PRO, ULTRA, MEGA), utilisez `/ocr/batch` pour traiter plusieurs factures :
- **10 factures** = **1 requête** (au lieu de 10 requêtes séparées)
- **Économie** : 90% de requêtes économisées

**Exemple** :
- Plan BASIC : Traiter 100 factures = 100 requêtes (batch désactivé)
- Plan PRO+ : Traiter 100 factures par batch (10 groupes) = 10 requêtes
- **Économie : 90 requêtes avec les plans payants**

### Planification intelligente

Pour le plan BASIC (100 req/mois) :
- ⚠️ **Batch désactivé** : Traitez les factures une par une
- Utilisez le cache pour éviter les retraitements
- Priorisez les factures importantes (100 factures max/mois)

Pour les plans payants (PRO+) :
- Groupez les factures non urgentes pour traitement batch (économie 90%)
- Utilisez le cache pour éviter les retraitements
- Traitez jusqu'à 10 factures par requête batch

---

## 📊 Comparaison des plans

| Fonctionnalité | BASIC | PRO | ULTRA | MEGA |
|----------------|-------|-----|-------|------|
| **Requêtes/mois** | 100 | 20 000 | 80 000 | 250 000 |
| **Factures max/mois** | 100 | ~200 000 | ~800 000 | ~2 500 000 |
| **Prix/mois** | $0 | $15 | $59 | $149 |
| **Batch processing** | ❌ Désactivé | ✅ 10 fichiers | ✅ 10 fichiers | ✅ 10 fichiers |
| **Compliance FR** | ❌ | ✅ | ✅ | ✅ |
| **Factur-X** | ❌ | ✅ | ✅ | ✅ |
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

### Scénario 1 : Test / Développement (< 100 factures/mois)

- **Factures à traiter** : 50-100/mois
- **Plan recommandé** : BASIC (100/mois)
- **Coût mensuel** : **$0**
- **Coût par facture** : **$0**
- **Limitation** : Batch désactivé, OCR basique uniquement

✅ **Gratuit pour tester ! Upgrade nécessaire pour production**

---

### Scénario 2 : PME moyenne (1 000 factures/mois)

- **Factures à traiter** : 1 000/mois
- **Plan recommandé** : PRO (20 000/mois)
- **Coût mensuel** : **$15**
- **Coût par facture** : **$0.015** (~1.5 centimes)

✅ **Meilleur prix du marché** (Microsoft : $19.90 pour moins de requêtes)

---

### Scénario 3 : Cabinet comptable moyen (5 000 factures/mois)

- **Factures à traiter** : 5 000/mois
- **Plan recommandé** : ULTRA (80 000/mois)
- **Coût mensuel** : **$59**
- **Coût par facture** : **$0.012** (~1.2 centimes)

✅ **-21% moins cher que Microsoft OCR** avec plus de requêtes

---

### Scénario 4 : Grande entreprise (20 000 factures/mois)

- **Factures à traiter** : 20 000/mois
- **Plan recommandé** : MEGA (250 000/mois)
- **Coût mensuel** : **$149**
- **Coût par facture** : **$0.0075** (~0.75 centimes)

✅ **-25% moins cher que Microsoft OCR** avec +25% de requêtes

---

## 🎯 Recommandations stratégiques

### Pour tester l'API
→ **Plan BASIC** ($0/mois)
- 100 requêtes/mois = 100 factures gratuites
- **Batch désactivé** (1 facture = 1 requête)
- OCR basique uniquement (pas de compliance, pas de Factur-X)
- Testez pendant 1-2 semaines
- Validez que l'API répond à vos besoins
- **⚠️ Upgrade nécessaire pour production** (plans payants avec batch + fonctionnalités avancées)

### Pour production légère
→ **Plan PRO** ($15/mois)
- Parfait pour démarrer en production
- 20 000 requêtes/mois = ~200 000 factures/mois avec batch
- **Batch activé** (10 factures par requête) = économie 90%
- **Compliance FR + Factur-X** inclus
- **Meilleur prix du marché** (-24% vs Microsoft OCR + fonctionnalités françaises)
- Upgrade facile vers ULTRA si besoin

### Pour production sérieuse
→ **Plan ULTRA** ($59/mois)
- Pour PME et cabinets comptables moyens
- 80 000 requêtes/mois = ~800 000 factures/mois avec batch
- **Batch activé** (10 factures par requête)
- **Compliance FR + Factur-X** inclus
- Support prioritaire inclus
- **-21% moins cher que Microsoft OCR + fonctionnalités françaises**

### Pour gros volumes
→ **Plan MEGA** ($149/mois)
- Pour grandes entreprises et volumes intensifs
- 250 000 requêtes/mois = ~2 500 000 factures/mois avec batch
- **Batch activé** (10 factures par requête)
- **Compliance FR + Factur-X** inclus
- **-25% moins cher que Microsoft OCR avec +25% de requêtes + fonctionnalités françaises**
- Support prioritaire

---

## 📞 Contact commercial

Pour les plans Enterprise ou questions tarifaires :
- Via RapidAPI : Support commercial
- Mentionnez "Plan Enterprise" ou "Tarifs personnalisés"

---

**Dernière mise à jour :** 2024-03-15  
**Tarifs en vigueur :** 2024-03-15
