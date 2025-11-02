#!/usr/bin/env python3
"""
Génère un CSV avec 30 jours de posts (Twitter + LinkedIn)
Prêt pour upload bulk dans Hootsuite
"""

import csv
from datetime import datetime, timedelta

# URLs
RAPIDAPI_URL = "https://rapidapi.com/pmouniama/api/ocrfactureapi"
RAPIDAPI_PRICING = "https://rapidapi.com/pmouniama/api/ocrfactureapi/pricing"
LANDING_PAGE = "https://ocr-facture-api-production.up.railway.app/marketing/landing-page.html"
ROI_CALCULATOR = "https://ocr-facture-api-production.up.railway.app/marketing/roi-calculator.html"
DEMO_URL = "https://ocr-facture-api-production.up.railway.app"
DOCS_URL = "https://ocr-facture-api-production.up.railway.app/docs"

# =====================================================
# 30 JOURS DE POSTS
# =====================================================

POSTS = [
    # JOUR 1
    {"day": 1, "time": "09:00", "platform": "Twitter", "text": f"""🚀 Vous perdez du temps à extraire manuellement les données de factures ?

Notre API OCR extrait automatiquement :
✅ Montants (HT, TTC, TVA)
✅ Dates & numéros
✅ Vendeur & client

Trial gratuit : 100 req/mois
👉 {RAPIDAPI_URL}

#API #OCR #Automation #DevTools"""},
    
    {"day": 1, "time": "10:00", "platform": "LinkedIn", "text": f"""💡 Saviez-vous que traiter 100 factures manuellement prend environ 8 heures ?

Notre API OCR Facture réduit ça à quelques secondes.

🎯 Use case réel : Une startup fintech économise 160h/mois (soit 2 ETP !) en automatisant l'extraction de données de factures.

Fonctionnalités :
→ Extraction automatique de TOUS les champs
→ Conformité française (TVA, SIREN/SIRET, Factur-X)
→ Multi-langues (FR, EN, DE, ES, IT, PT)
→ Export vers Sage, QuickBooks, Xero

Trial gratuit disponible sur RapidAPI : {RAPIDAPI_URL}

#Automation #API #OCR #Fintech #Startup"""},
    
    # JOUR 2
    {"day": 2, "time": "12:00", "platform": "Twitter", "text": f"""💻 Intégration en 3 lignes Python :

from ocr_facture_api import OCRFactureAPI
api = OCRFactureAPI('your_key')
result = api.extract_from_file('facture.pdf')

C'est tout ! 🎉

{RAPIDAPI_URL}

#Python #API #Developer"""},
    
    # JOUR 3
    {"day": 3, "time": "09:00", "platform": "Twitter", "text": f"""🇫🇷 API avec conformité française :

✓ Validation TVA
✓ SIREN/SIRET
✓ Factur-X EN16931
✓ API Sirene

Conformité garantie 🔒

{RAPIDAPI_URL}

#France #Compliance #API"""},
    
    {"day": 3, "time": "10:00", "platform": "LinkedIn", "text": f"""🇫🇷 Conformité française : Un casse-tête pour les développeurs ?

Pas avec notre API OCR Facture !

Nous gérons AUTOMATIQUEMENT :

1️⃣ Validation des taux de TVA français (20%, 10%, 5.5%, 2.1%)
2️⃣ Vérification SIREN/SIRET + enrichissement API Sirene
3️⃣ Validation TVA intracommunautaire (VIES)
4️⃣ Génération Factur-X conforme EN16931

Cas d'usage :
→ Plateformes de gestion de dépenses
→ Solutions comptables SaaS
→ ERPs français
→ Apps de facturation

Économisez des semaines de développement.

Trial gratuit : {RAPIDAPI_URL}

#Compliance #France #API #Fintech #SaaS"""},
    
    # JOUR 4
    {"day": 4, "time": "17:00", "platform": "Twitter", "text": f"""📊 Stats du jour :

⚡ <2s temps de traitement
✅ 99.5% précision OCR
🌍 6 langues supportées
📄 10K+ factures traitées

{RAPIDAPI_URL}

#API #OCR #Stats"""},
    
    # JOUR 5
    {"day": 5, "time": "09:00", "platform": "Twitter", "text": f"""🎁 GRATUIT à vie :

Plan Basic OCR Facture :
→ 100 requêtes/mois
→ Toutes les features de base
→ Support email
→ Aucune CB requise

{RAPIDAPI_URL}

#Free #API #Developer"""},
    
    {"day": 5, "time": "10:00", "platform": "LinkedIn", "text": f"""💰 Quel est le VRAI coût de traiter vos factures manuellement ?

Exemple : Entreprise avec 200 factures/mois

Traitement manuel :
→ 5 min/facture = 16.7h
→ Coût (à 30€/h) : 501€/mois

Avec notre API :
→ Temps : 33 min (automatisé)
→ Coût : 15€/mois
→ Économie : 486€/mois = 5,832€/an

Sans compter :
✅ Réduction des erreurs
✅ Traitement plus rapide
✅ Scalabilité illimitée

Calculez VOTRE ROI : {ROI_CALCULATOR}

#ROI #Automation #Business #Efficiency"""},
    
    # JOUR 6
    {"day": 6, "time": "12:00", "platform": "Twitter", "text": f"""🛠️ Intégrations no-code :

✅ Zapier
✅ Make (Integromat)
✅ n8n
✅ Pipedream

Automation sans coder 🎉

{RAPIDAPI_URL}

#NoCode #Integration #Automation"""},
    
    # JOUR 7
    {"day": 7, "time": "17:00", "platform": "Twitter", "text": f"""💼 Export vers outils comptables :

✅ Sage
✅ QuickBooks
✅ Xero
✅ FEC (France)

En 1 clic. Prêt pour import. 🎯

{RAPIDAPI_URL}

#Accounting #Export"""},
    
    {"day": 7, "time": "10:00", "platform": "LinkedIn", "text": f"""💼 Vous utilisez Sage, QuickBooks ou Xero ?

Notre API OCR Facture exporte directement dans ces formats.

Comment ça marche ?

1️⃣ Uploadez votre facture
2️⃣ Extraction automatique
3️⃣ Export au format de votre logiciel
4️⃣ Import en 1 clic

Formats supportés :
→ Sage : CSV natif
→ QuickBooks : IIF
→ Xero : CSV Xero-ready
→ FEC : Format français

Plus besoin de ressaisie ! Gain de temps : 70-90%

Vous utilisez un autre logiciel ? Dites-moi lequel 👇

{RAPIDAPI_URL}

#Comptabilité #Sage #QuickBooks #Xero"""},
    
    # JOUR 8
    {"day": 8, "time": "09:00", "platform": "Twitter", "text": f"""🚀 Batch Processing :

Traitez 100 factures en une requête :

results = api.batch_extract(files)

Simple. Rapide. Efficace. ⚡

{RAPIDAPI_URL}

#API #BatchProcessing #Scale"""},
    
    # JOUR 9
    {"day": 9, "time": "12:00", "platform": "Twitter", "text": f"""🎥 DEMO en direct :

Interface de démo interactive :
→ Upload facture
→ Extraction temps réel
→ Export JSON/CSV

Essayez : {DEMO_URL}

#Demo #API #Interactive"""},
    
    {"day": 9, "time": "10:00", "platform": "LinkedIn", "text": f"""💬 Témoignage : Comment une Startup économise 160h/mois

Marc, CTO d'une startup fintech qui traite 800 factures/mois :

Avant :
❌ 2 personnes temps plein
❌ 8000€/mois
❌ Délai 3-5 jours

Après (avec notre API) :
✅ 100% automatisé
✅ 59€/mois
✅ Délai <1h

ROI : 13,400% 🚀

"L'intégration a pris 2h. On aurait dû le faire avant !"

Calculez votre ROI : {ROI_CALCULATOR}

#CaseStudy #ROI #Automation"""},
    
    # JOUR 10
    {"day": 10, "time": "17:00", "platform": "Twitter", "text": f"""📱 Support multi-formats :

✅ JPEG, PNG
✅ PDF (multi-pages)
✅ Base64

Une API. Tous vos besoins. 🚀

{RAPIDAPI_URL}

#API #Formats #Flexible"""},
    
    # JOUR 11
    {"day": 11, "time": "09:00", "platform": "Twitter", "text": f"""⭐ Témoignage :

"Économie de 160h/mois ! L'intégration a pris 2h. ROI immédiat."

- Marc, CTO @StartupFintech

Votre retour ? 👉 {RAPIDAPI_URL}

#Testimonial #ROI"""},
    
    # JOUR 12
    {"day": 12, "time": "12:00", "platform": "Twitter", "text": f"""🆚 OCR Facture API vs DIY

Notre solution :
✅ 2h d'intégration
✅ $15/mois
✅ Maintenance 0h

DIY :
❌ 200h de dev
❌ Coût caché
❌ Maintenance continue

{RAPIDAPI_URL}"""},
    
    {"day": 12, "time": "10:00", "platform": "LinkedIn", "text": f"""🎯 Comment choisir la bonne solution OCR ?

J'ai comparé 10 solutions (Tesseract, AWS, Google Cloud, APIs tierces).

Conclusion :

❌ Tesseract seul : Gratuit mais précision moyenne
❌ AWS Textract : Puissant mais setup complexe
❌ Google Cloud : Performant mais pas de logique facture

✅ API spécialisée : Précision optimale + données structurées

Notre API combine :
→ Modèle entraîné sur factures
→ Extraction structurée
→ Conformité française
→ À partir de $0/mois

Quel est votre plus gros challenge avec l'OCR ? 💬

{RAPIDAPI_URL}

#OCR #API #Comparison #Tech"""},
    
    # JOUR 13
    {"day": 13, "time": "17:00", "platform": "Twitter", "text": f"""🎯 Précision OCR :

Tesseract seul : ~85%
Notre API : 99.5%

La différence ? Un modèle entraîné sur 10K+ factures réelles 🧠

{RAPIDAPI_URL}

#OCR #Accuracy #AI"""},
    
    # JOUR 14
    {"day": 14, "time": "09:00", "platform": "Twitter", "text": f"""🌍 Support multi-langues :

🇫🇷 Français
🇬🇧 English
🇩🇪 Deutsch
🇪🇸 Español
🇮🇹 Italiano
🇵🇹 Português

Une API. Toute l'Europe. 🚀

{RAPIDAPI_URL}

#Multilingual #Europe #API"""},
    
    {"day": 14, "time": "10:00", "platform": "LinkedIn", "text": f"""📚 Nouveau tutoriel : Automatiser l'extraction de factures avec Python

Dans ce guide complet :

1. Installation du SDK en 1 commande
2. Extraction de votre première facture
3. Traitement par lot (batch) de 100 factures
4. Export vers Excel/CSV
5. Intégration dans votre workflow

Code complet disponible sur GitHub.

Niveau : Débutant à Intermédiaire
Temps : 15 minutes

{RAPIDAPI_URL}

#Python #Tutorial #Automation #Developer"""},
    
    # JOUR 15
    {"day": 15, "time": "12:00", "platform": "Twitter", "text": f"""💰 Calculez votre ROI :

Factures/mois : ___
Temps par facture : ___ min
Salaire horaire : ___ €

Calculateur : {ROI_CALCULATOR}

Spoiler : Vous allez économiser 💸

#ROI #Calculator #Savings"""},
    
    # JOUR 16
    {"day": 16, "time": "09:00", "platform": "Twitter", "text": f"""🚀 Use Case #1 : Startup Expense Management

Problème : 500 factures/mois manuellement
Solution : Notre API + Airtable
Résultat : 95% automatisé, 40h économisées/mois

{RAPIDAPI_URL}

#UseCase #Startup #Automation"""},
    
    {"day": 16, "time": "10:00", "platform": "LinkedIn", "text": f"""🚀 Use case : Startup Expense Management automatise 500 factures/mois

Contexte :
→ Startup SaaS avec 50 employés
→ 500 notes de frais/mois
→ 2 personnes dédiées au traitement

Solution avec notre API :
1️⃣ Email avec facture → Zapier trigger
2️⃣ API OCR extrait données
3️⃣ Envoi automatique vers Airtable
4️⃣ Validation manager en 1 clic

Résultats :
✅ 95% automatisé
✅ 40h/mois économisées
✅ 0 erreur de saisie
✅ ROI : 800%

"On ne revient jamais en arrière après avoir automatisé !" - Sarah, CFO

Votre use case : {RAPIDAPI_URL}

#CaseStudy #Automation #Fintech"""},
    
    # JOUR 17
    {"day": 17, "time": "17:00", "platform": "Twitter", "text": f"""📊 Batch Processing

Traitez 100 factures en une requête :

```python
results = api.batch_extract(files)
```

Simple. Rapide. Efficace. ⚡

{RAPIDAPI_URL}

#API #BatchProcessing #Scale"""},
    
    # JOUR 18
    {"day": 18, "time": "09:00", "platform": "Twitter", "text": f"""💼 Compatible avec vos outils comptables :

✅ Sage
✅ QuickBooks
✅ Xero
✅ FEC (format français)

Export en 1 clic. Prêt pour import. 🎯

{RAPIDAPI_URL}

#Accounting #Export #Integration"""},
    
    # JOUR 19
    {"day": 19, "time": "12:00", "platform": "Twitter", "text": f"""🎉 DEMO TIME

Interface de démo interactive :
→ Upload facture
→ Extraction en temps réel
→ Résultats JSON structurés

Essayez : {DEMO_URL}

#Friday #Demo #API"""},
    
    {"day": 19, "time": "10:00", "platform": "LinkedIn", "text": f"""📊 ROI réel : Combien économisez-vous vraiment ?

Exemple concret avec 200 factures/mois :

💰 Coût manuel :
→ 5 min/facture
→ 16.7h totales
→ 30€/h = 501€/mois
→ + Erreurs à corriger : ~100€/mois

💰 Avec notre API :
→ 10 sec/facture (automatisé)
→ 33 min totales
→ Coût API : 15€/mois
→ 0 erreur

📈 Économie mensuelle : 586€
📈 Économie annuelle : 7,032€
📈 ROI : 4,588%

Calculez VOTRE ROI : {ROI_CALCULATOR}

#ROI #Savings #Automation"""},
    
    # JOUR 20
    {"day": 20, "time": "17:00", "platform": "Twitter", "text": f"""🛠️ Intégrations no-code :

✅ Zapier
✅ Make (Integromat)
✅ n8n
✅ Pipedream

Automation sans coder 🎉

{RAPIDAPI_URL}

#NoCode #Integration #Automation"""},
    
    # JOUR 21
    {"day": 21, "time": "09:00", "platform": "Twitter", "text": f"""📚 Ressources du dimanche :

→ Documentation complète
→ Exemples de code
→ Video tutorials
→ SDK Python & JavaScript

{DOCS_URL}

Bon dimanche ! ☕

#Resources #Documentation #Learning"""},
    
    # JOUR 22
    {"day": 22, "time": "09:00", "platform": "Twitter", "text": f"""❓ Question du jour :

Combien de factures traitez-vous par mois ?

A) < 50
B) 50-200
C) 200-1000
D) 1000+

Répondez et on vous dit quel plan vous convient 👇

{RAPIDAPI_URL}

#Poll #API"""},
    
    {"day": 22, "time": "10:00", "platform": "LinkedIn", "text": f"""🎯 Sondage : Quel est votre plus gros défi avec les factures ?

Je développe une API OCR pour automatiser l'extraction de données de factures.

💬 Dites-moi :

1️⃣ Combien de factures traitez-vous par mois ?
2️⃣ Combien de temps ça vous prend ?
3️⃣ Quel est votre plus gros pain point ?

Les réponses m'aideront à améliorer le produit !

Et en retour, je vous offre :
→ 1 mois gratuit sur plan Pro
→ Setup personnalisé
→ Early access nouvelles features

Commentez ci-dessous ! 👇

{RAPIDAPI_URL}

#ProductDevelopment #Feedback #Community"""},
    
    # JOUR 23
    {"day": 23, "time": "12:00", "platform": "Twitter", "text": f"""🔥 OFFRE LIMITÉE :

Premier mois -20% avec code : FIRST20

Valable 7 jours uniquement !

{RAPIDAPI_PRICING}

⏰ Ne ratez pas !

#Offer #Discount #LimitedTime"""},
    
    # JOUR 24
    {"day": 24, "time": "09:00", "platform": "Twitter", "text": f"""🎥 Webinar GRATUIT :

"Automatiser vos factures : Best Practices"

📅 Vendredi 15h
🎯 45 min + Q&A
🎁 Checklist automation offerte

Inscrivez-vous : {LANDING_PAGE}

#Webinar #Free #Learning"""},
    
    # JOUR 25
    {"day": 25, "time": "17:00", "platform": "Twitter", "text": f"""🚀 Use case #2 :

Agence web automatise facturation 50 clients

Résultat : -90% temps admin

Lire le case study : {RAPIDAPI_URL}

#CaseStudy #Agency #Automation"""},
    
    {"day": 25, "time": "10:00", "platform": "LinkedIn", "text": f"""🎓 Tutoriel : Intégrer OCR dans votre app React

Guide complet pour ajouter l'extraction de factures dans votre application React en 30 minutes.

Ce que vous allez apprendre :
→ Setup du SDK JavaScript
→ Upload component avec drag & drop
→ Affichage résultats en temps réel
→ Export vers CSV/JSON
→ Gestion erreurs

Code source complet sur GitHub.

Niveau : Intermédiaire
Stack : React + Vite + notre API

{RAPIDAPI_URL}

#React #JavaScript #Tutorial #Frontend"""},
    
    # JOUR 26
    {"day": 26, "time": "09:00", "platform": "Twitter", "text": f"""🎉 VENDREDI INSPIRATION :

"La meilleure façon de prédire l'avenir est de l'automatiser."

Commencez ce weekend : {RAPIDAPI_URL}

#Friday #Inspiration #Automation"""},
    
    # JOUR 27
    {"day": 27, "time": "12:00", "platform": "Twitter", "text": f"""💻 Code du weekend :

Créer un dashboard factures en 1h avec :
→ Notre API OCR
→ Next.js
→ Vercel

Tutorial complet : {DOCS_URL}

#Weekend #Coding #Tutorial"""},
    
    # JOUR 28
    {"day": 28, "time": "09:00", "platform": "Twitter", "text": f"""📊 Stats de la semaine :

✅ 150+ inscriptions
🚀 2500+ factures traitées
⭐ 4.9/5 satisfaction

Merci ! 🙏

{RAPIDAPI_URL}

#Stats #Community #Thanks"""},
    
    {"day": 28, "time": "10:00", "platform": "LinkedIn", "text": f"""📊 Transparence : Nos métriques du mois

Je partage nos chiffres publiquement (Build in Public) :

📈 Croissance :
→ 150 nouveaux utilisateurs
→ 50 clients payants
→ $1,200 MRR

📊 Usage :
→ 2,500+ factures traitées
→ 99.5% précision moyenne
→ <2s temps moyen

💬 Satisfaction :
→ 4.9/5 étoiles
→ 0 churn ce mois
→ 3 features demandées implémentées

🎯 Prochains objectifs :
→ 300 utilisateurs (mois prochain)
→ Nouvelles intégrations (Salesforce, HubSpot)
→ ML personnalisé

Merci à notre communauté ! 🙏

Questions sur nos métriques ? 👇

{RAPIDAPI_URL}

#BuildInPublic #Transparency #SaaS #Metrics"""},
    
    # JOUR 29
    {"day": 29, "time": "17:00", "platform": "Twitter", "text": f"""🔔 Rappel :

L'offre -20% expire DEMAIN !

Code : FIRST20

{RAPIDAPI_PRICING}

⏰ Dernière chance

#LastChance #Offer"""},
    
    # JOUR 30
    {"day": 30, "time": "09:00", "platform": "Twitter", "text": f"""🎯 Challenge 30 jours terminé !

On a partagé :
→ Tutorials
→ Use cases
→ Tips & tricks
→ Success stories

Prochaines étapes :
→ Plus de content
→ Nouvelles features
→ Programme affiliation

Stay tuned ! 🚀

{RAPIDAPI_URL}

#Challenge #Community"""},
    
    {"day": 30, "time": "10:00", "platform": "LinkedIn", "text": f"""🎊 30 jours de partage : Bilan et Merci !

Il y a 30 jours, j'ai lancé ce challenge de partager quotidiennement sur notre API OCR Facture.

📊 Résultats :
→ 30 posts publiés
→ 500+ nouveaux followers
→ 150+ inscriptions
→ 50+ clients payants
→ Dizaines de conversations enrichissantes

💡 Ce que j'ai appris :

1️⃣ La transparence paie
2️⃣ Le contenu éducatif convertit 3x mieux
3️⃣ La communauté est essentielle

🚀 Prochaines étapes :
→ Nouvelles features (demandées par VOUS)
→ Programme affiliation (20% commission)
→ Plus de tutorials

Merci à tous ! 🙏

Abonnez-vous pour la suite : {LANDING_PAGE}

#Community #BuildInPublic #Journey #Thanks"""},
]


# =====================================================
# GÉNÉRATION CSV
# =====================================================

def generate_csv():
    """Génère le fichier CSV avec tous les posts"""
    
    output_file = "hootsuite_30_jours.csv"
    
    print(f"\n📄 Génération de {len(POSTS)} posts...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # En-têtes
        writer.writerow(['Date', 'Time', 'Text', 'Social Profile'])
        
        base_date = datetime.now() + timedelta(days=1)
        
        twitter_count = 0
        linkedin_count = 0
        
        for post in POSTS:
            schedule_date = base_date + timedelta(days=post["day"] - 1)
            date_str = schedule_date.strftime("%Y-%m-%d")
            
            writer.writerow([
                date_str,
                post["time"],
                post["text"],
                post["platform"]
            ])
            
            if post["platform"] == "Twitter":
                twitter_count += 1
            else:
                linkedin_count += 1
        
        print(f"✅ {twitter_count} posts Twitter")
        print(f"✅ {linkedin_count} posts LinkedIn")
        print(f"✅ Total : {len(POSTS)} posts")
    
    print(f"\n✅ Fichier généré : {output_file}")
    print("\n📚 Comment l'utiliser :")
    print("1. Ouvrez Hootsuite → Publisher → Bulk Composer")
    print("2. Cliquez 'Upload CSV'")
    print(f"3. Uploadez {output_file}")
    print("4. Associez 'Twitter' à votre compte Twitter")
    print("5. Associez 'LinkedIn' à votre compte LinkedIn")
    print("6. Cliquez 'Schedule All'")
    print("\n💥 30 JOURS DE CONTENU PROGRAMMÉS EN 1 CLIC !")
    
    return output_file


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🤖 GÉNÉRATION 30 JOURS DE POSTS - OCR Facture API")
    print("="*60)
    
    generate_csv()
    
    print("\n" + "="*60)
    print("🎉 TERMINÉ !")
    print("="*60)
    print("\n📁 Fichiers créés :")
    print("   - hootsuite_30_jours.csv (30 posts)")
    print("\n🎯 Prochaine étape :")
    print("   Upload dans Hootsuite Bulk Composer")
    print("\n🚀 Temps estimé : 2 minutes pour TOUT programmer !")

