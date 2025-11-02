# 📧 Séquences Email Automatisées - OCR Facture API

## Vue d'ensemble

5 séquences email automatisées pour :
1. Convertir les trials en clients payants
2. Onboarder les nouveaux utilisateurs
3. Réactiver les clients inactifs
4. Upsell vers plans supérieurs
5. Recueillir des témoignages

---

## SÉQUENCE 1 : Trial → Client Payant (7 jours)

### Email 1 : Bienvenue (Immédiat après inscription)

**Sujet** : 🎉 Bienvenue ! Votre API OCR est prête

```
Bonjour {Prénom},

Bienvenue dans OCR Facture API ! 🚀

Votre clé API est activée et vos 100 requêtes gratuites vous attendent.

📚 Pour bien démarrer :

→ Documentation complète : https://rapidapi.com/pmouniama/api/ocrfactureapi
→ Quick Start (5 min) : https://rapidapi.com/pmouniama/api/ocrfactureapi
→ Exemples de code Python/JS : https://rapidapi.com/pmouniama/api/ocrfactureapi

💡 Votre première facture en 3 étapes :

1. Installez le SDK : pip install ocr-facture-api
2. Copiez ce code :
   ```python
   from ocr_facture_api import OCRFactureAPI
   api = OCRFactureAPI('votre_cle')
   result = api.extract_from_file('facture.pdf')
   ```
3. C'est tout ! 🎉

Besoin d'aide ? Répondez à cet email, je réponds en <24h.

À tout de suite,
Philippe
Founder, OCR Facture API

P.S. Voici une facture de test pour commencer : https://rapidapi.com/pmouniama/api/ocrfactureapi
```

---

### Email 2 : Astuce d'utilisation (Jour 2)

**Sujet** : 💡 Astuce : Traiter plusieurs factures en une fois

```
Bonjour {Prénom},

J'espère que vous avez pu tester l'API hier !

Aujourd'hui, je vous partage une fonctionnalité très demandée : le batch processing.

🚀 Traitez 100 factures en une seule requête :

```python
files = ['facture1.pdf', 'facture2.pdf', ...]
results = api.batch_extract(files)
```

Cas d'usage réels :
→ Import mensuel de toutes vos factures
→ Migration depuis votre ancien système
→ Traitement de fin de mois

📊 Benchmark : 100 factures traitées en ~30 secondes

Tutorial complet : https://rapidapi.com/pmouniama/api/ocrfactureapi

Questions ? Répondez à cet email.

Philippe

P.S. Vous avez déjà utilisé {X} requêtes sur 100. Il vous reste {100-X} requêtes gratuites.
```

---

### Email 3 : Case Study (Jour 4)

**Sujet** : 📊 Comment Marc économise 160h/mois avec notre API

```
Bonjour {Prénom},

Je voulais partager avec vous l'histoire de Marc, CTO d'une startup fintech.

❌ AVANT :
- 800 factures/mois à traiter
- 2 personnes à temps plein
- Coût : 8000€/mois
- Délai : 3-5 jours

✅ APRÈS (avec notre API) :
- 100% automatisé
- 0 erreur de saisie
- Coût : 59€/mois
- Délai : <1 heure

ROI : 13,400% 🚀

"L'intégration a pris 2 heures. On aurait dû le faire avant !" - Marc

Lire le case study complet : https://rapidapi.com/pmouniama/api/ocrfactureapi

Votre situation ressemble à celle de Marc ?
Calculez votre ROI : [lien calculateur]

Philippe
```

---

### Email 4 : Rappel fin trial (Jour 6 - avant fin)

**Sujet** : ⏰ Votre trial gratuit se termine demain

```
Bonjour {Prénom},

Votre plan gratuit (100 req/mois) se termine demain.

📊 Votre utilisation :
- Requêtes utilisées : {X}/100
- Factures traitées : {Y}
- Précision moyenne : 99.5%

Pour continuer sans interruption, passez au plan Pro :

✅ 20,000 requêtes/mois
✅ Toutes les fonctionnalités
✅ Support prioritaire
✅ 15$/mois seulement

🎁 OFFRE SPÉCIALE : -20% avec code FIRST20
Soit 12$/mois au lieu de 15$ (premier mois)

Passer au plan Pro : https://rapidapi.com/pmouniama/api/ocrfactureapi

Questions sur les plans ? Répondez à cet email.

Philippe

P.S. Vous préférez rester sur le plan gratuit ? Pas de problème ! Vous gardez 100 req/mois à vie.
```

---

### Email 5 : Dernière chance (Jour 7 - jour de fin)

**Sujet** : 🎁 Dernière chance : -20% expire ce soir

```
Bonjour {Prénom},

Dernier rappel amical : votre offre -20% expire ce soir à minuit.

Code : FIRST20

Avec le plan Pro, vous débloquez :
→ 20,000 requêtes/mois (vs 100)
→ Batch processing
→ Export formats comptables
→ Support prioritaire

Prix : 12$/mois (au lieu de 15$) avec le code

Activer maintenant : https://rapidapi.com/pmouniama/api/ocrfactureapi

Cette offre ne reviendra pas.

Philippe

P.S. Même si vous ne passez pas au plan Pro, vous gardez votre plan gratuit à vie. Pas de stress ! 😊
```

---

## SÉQUENCE 2 : Onboarding Nouveaux Clients (14 jours)

### Email 1 : Merci + Next Steps (Immédiat après achat)

**Sujet** : 🎉 Merci ! Voici vos prochaines étapes

```
Bonjour {Prénom},

Merci d'avoir souscrit au plan {Plan} ! 🎉

Votre abonnement est actif. Voici comment tirer le meilleur parti :

📚 SEMAINE 1 : Maîtriser les bases
→ Jour 1-2 : Setup & première facture
→ Jour 3-4 : Batch processing
→ Jour 5-7 : Export vers votre logiciel comptable

🎯 OBJECTIF : Traiter vos 100 premières factures

📞 Besoin d'aide ?
- Documentation : https://rapidapi.com/pmouniama/api/ocrfactureapi
- Support prioritaire : support@ocr-facture-api.com
- Je réponds en <4h

Rendez-vous demain pour le premier tutoriel !

Philippe
```

---

### Email 2 : Tutorial #1 (Jour 2)

**Sujet** : 📚 Tutorial #1 : Setup en 5 minutes

```
Bonjour {Prénom},

Premier tutorial : Setup complet en 5 minutes chrono.

Étape 1 : Installation
pip install ocr-facture-api

Étape 2 : Configuration
```python
from ocr_facture_api import OCRFactureAPI
api = OCRFactureAPI('votre_cle_api')
```

Étape 3 : Premier test
```python
result = api.extract_from_file('facture.pdf')
print(result)
```

Vidéo complète (3 min) : [lien YouTube]

Bloquez-vous quelque part ? Répondez à cet email.

À demain pour le tutorial #2 !

Philippe
```

---

### Email 3-6 : Tutorials avancés (Jours 4, 7, 10, 14)

**Sujets** :
- Email 3 : Tutorial #2 : Batch processing
- Email 4 : Tutorial #3 : Export comptable
- Email 5 : Tutorial #4 : Conformité française
- Email 6 : Tutorial #5 : Webhooks & automation

---

## SÉQUENCE 3 : Réactivation Clients Inactifs (30 jours)

### Email 1 : Nous vous manquons ? (Après 30 jours inactivité)

**Sujet** : 😢 On ne se voit plus...

```
Bonjour {Prénom},

J'ai remarqué que vous n'avez pas utilisé l'API depuis {X} jours.

Tout va bien ? Vous bloquez quelque part ?

Problèmes fréquents et solutions :
→ "Je ne sais pas par où commencer" → [Quick Start 5 min]
→ "C'est trop technique" → [Vidéo tutorial]
→ "Pas le temps de tester" → [Démo interactive]

💬 Ou dites-moi directement ce qui vous bloque (répondez à cet email).

Je suis là pour vous aider.

Philippe
```

---

### Email 2 : Nouveautés (Jour 7)

**Sujet** : 🚀 Vous avez raté ces nouvelles fonctionnalités

```
Bonjour {Prénom},

Depuis votre dernière visite, nous avons ajouté :

✅ Export Sage/QuickBooks/Xero (très demandé !)
✅ Cache automatique (2x plus rapide)
✅ Nouveaux SDKs Python & JavaScript

Revenez tester : https://rapidapi.com/pmouniama/api/ocrfactureapi

Et toujours : votre plan {Plan} vous attend.

Philippe
```

---

### Email 3 : Offre réactivation (Jour 14)

**Sujet** : 🎁 Cadeau de bienvenue : 1 mois gratuit

```
Bonjour {Prénom},

Dernière tentative 😊

Pour vous encourager à revenir, je vous offre :
→ 1 mois gratuit sur plan Pro
→ Support dédié (1h de consultation)
→ Setup personnalisé

Code : COMEBACK

Valable 7 jours.

Activer : https://rapidapi.com/pmouniama/api/ocrfactureapi

À bientôt ?

Philippe

P.S. Si vous ne revenez pas, pas de problème ! Mais dites-moi pourquoi (pour m'améliorer).
```

---

## SÉQUENCE 4 : Upsell Plan Supérieur (quand proche limite)

### Email : Vous approchez de votre limite

**Sujet** : ⚠️ Vous avez utilisé 80% de votre quota

```
Bonjour {Prénom},

Bonne nouvelle : votre utilisation explose ! 📈

Quota actuel : {X}/{Limite} requêtes utilisées ({%}%)

⚠️ Attention : Plus que {Limite-X} requêtes restantes ce mois.

Pour éviter toute interruption, passez au plan {Plan Supérieur} :

✅ {Limite Supérieure} requêtes/mois
✅ Pas de limite stricte (soft limit)
✅ Tarif dégressif

Prix : {Prix}$/mois

Upgrader maintenant : https://rapidapi.com/pmouniama/api/ocrfactureapi

Questions ? Appelez-moi : +33 X XX XX XX XX

Philippe
```

---

## SÉQUENCE 5 : Demande de Témoignage (Après 60 jours)

### Email : Partagez votre expérience

**Sujet** : 💬 Votre avis compte (2 minutes)

```
Bonjour {Prénom},

Ça fait 2 mois que vous utilisez notre API.

J'aimerais votre feedback !

📊 Mini-sondage (2 minutes) :
[lien formulaire]

Questions :
1. Que pensez-vous de l'API ? (1-10)
2. Qu'avez-vous automatisé avec ?
3. Combien de temps économisez-vous ?
4. Recommanderiez-vous à un ami ?
5. Quelles améliorations souhaitez-vous ?

🎁 En échange :
- 1 mois gratuit offert
- Badge "Early Adopter"
- Mention sur notre site (si vous voulez)

Merci d'avance !

Philippe

P.S. Les meilleurs témoignages seront publiés (avec votre accord).
```

---

## 🛠️ Configuration dans Mailchimp

### Étapes pour automatiser :

1. **Créer des listes segmentées**
   - Free users
   - Paid users (Pro, Ultra, Mega)
   - Inactive users
   - Power users (>80% quota)

2. **Configurer les automations**
   - Automation > Create > Email
   - Trigger : Tag ajouté / Date spécifique / Quota atteint
   - Ajouter les emails de la séquence
   - Définir les délais (immédiat, +2 jours, etc.)

3. **Personnaliser avec merge tags**
   - {Prénom} → *|FNAME|*
   - {Plan} → *|PLAN|*
   - {X} → *|USAGE|*

4. **A/B Testing**
   - Tester 2 sujets différents
   - Garder le meilleur

5. **Analytics**
   - Tracker : Open rate, Click rate, Conversion rate
   - Optimiser selon résultats

---

## 📊 KPIs à Suivre

### Par séquence :

**Séquence 1 (Trial → Payant)** :
- Objectif : 20-30% de conversion
- Tracker : Open rate, Click to upgrade, Conversion

**Séquence 2 (Onboarding)** :
- Objectif : 80% complètent l'onboarding
- Tracker : Tutorials complétés, First API call, Active users

**Séquence 3 (Réactivation)** :
- Objectif : 10-15% réactivés
- Tracker : Retour sur plateforme, Nouvelle API call

**Séquence 4 (Upsell)** :
- Objectif : 25-40% upgrade
- Tracker : Click upgrade, Conversion

**Séquence 5 (Témoignage)** :
- Objectif : 30% répondent
- Tracker : Formulaire complété, Reviews publiés

---

## 🎯 Optimisation Continue

### Chaque mois :

1. **Analyser les stats**
   - Quels emails ont le meilleur taux d'ouverture ?
   - Quels emails convertissent le mieux ?

2. **A/B tester**
   - Sujets
   - CTA (appels à l'action)
   - Timing

3. **Ajuster**
   - Remplacer emails sous-performants
   - Doubler sur ce qui marche

4. **Personnaliser davantage**
   - Segmenter par industrie
   - Adapter selon comportement

---

**Prêt à automatiser vos emails ? Configurez Mailchimp maintenant !** 🚀

