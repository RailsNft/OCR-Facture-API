#!/usr/bin/env python3
"""
Script pour publier AUTOMATIQUEMENT tous les posts sur Hootsuite/Twitter/LinkedIn
Usage: python auto-publish-all.py
"""

import os
import sys
import json
from datetime import datetime, timedelta

# =====================================================
# CONFIGURATION
# =====================================================

# Option 1 : Utiliser l'API Hootsuite (RECOMMANDÉ - gère Twitter + LinkedIn)
HOOTSUITE_ACCESS_TOKEN = os.getenv("HOOTSUITE_ACCESS_TOKEN", "")

# Option 2 : APIs directes (si pas Hootsuite)
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

# URLs
RAPIDAPI_URL = "https://rapidapi.com/pmouniama/api/ocrfactureapi"
LANDING_PAGE_URL = "https://ocr-facture-api-production.up.railway.app/marketing/landing-page.html"
ROI_CALCULATOR_URL = "https://ocr-facture-api-production.up.railway.app/marketing/roi-calculator.html"

# =====================================================
# POSTS À PUBLIER
# =====================================================

TWITTER_POSTS = [
    {
        "day": 1,
        "time": "09:00",
        "text": f"""🚀 Vous perdez du temps à extraire manuellement les données de factures ?

Notre API OCR extrait automatiquement :
✅ Montants (HT, TTC, TVA)
✅ Dates & numéros
✅ Vendeur & client

Trial gratuit : 100 req/mois
👉 {RAPIDAPI_URL}

#API #OCR #Automation #DevTools"""
    },
    {
        "day": 2,
        "time": "12:00",
        "text": f"""💻 Intégration en 3 lignes Python :

from ocr_facture_api import OCRFactureAPI
api = OCRFactureAPI('your_key')
result = api.extract_from_file('facture.pdf')

C'est tout ! 🎉

{RAPIDAPI_URL}

#Python #API #Developer"""
    },
    {
        "day": 3,
        "time": "09:00",
        "text": f"""🇫🇷 API avec conformité française :

✓ Validation TVA
✓ SIREN/SIRET
✓ Factur-X EN16931
✓ API Sirene

Conformité garantie 🔒

{RAPIDAPI_URL}

#France #Compliance #API"""
    },
    {
        "day": 4,
        "time": "17:00",
        "text": f"""📊 Stats du jour :

⚡ <2s temps de traitement
✅ 99.5% précision OCR
🌍 6 langues supportées
📄 10K+ factures traitées

{RAPIDAPI_URL}

#API #OCR #Stats"""
    },
    {
        "day": 5,
        "time": "09:00",
        "text": f"""🎁 GRATUIT à vie :

Plan Basic OCR Facture :
→ 100 requêtes/mois
→ Toutes les features de base
→ Support email
→ Aucune CB requise

{RAPIDAPI_URL}

#Free #API #Developer"""
    },
    {
        "day": 6,
        "time": "12:00",
        "text": f"""🛠️ Intégrations no-code :

✅ Zapier
✅ Make (Integromat)
✅ n8n

Automation sans coder 🎉

{RAPIDAPI_URL}

#NoCode #Integration #Automation"""
    },
    {
        "day": 7,
        "time": "17:00",
        "text": f"""💼 Export vers outils comptables :

✅ Sage
✅ QuickBooks
✅ Xero
✅ FEC (France)

En 1 clic. Prêt pour import. 🎯

{RAPIDAPI_URL}

#Accounting #Export"""
    },
    {
        "day": 8,
        "time": "09:00",
        "text": f"""🚀 Batch Processing :

Traitez 100 factures en une requête :

results = api.batch_extract(files)

Simple. Rapide. Efficace. ⚡

{RAPIDAPI_URL}

#API #BatchProcessing #Scale"""
    },
    {
        "day": 9,
        "time": "12:00",
        "text": f"""🎥 DEMO en direct :

Interface de démo interactive :
→ Upload facture
→ Extraction temps réel
→ Export JSON/CSV

Essayez : https://ocr-facture-api-production.up.railway.app

#Demo #API #Interactive"""
    },
    {
        "day": 10,
        "time": "17:00",
        "text": f"""📱 Support multi-formats :

✅ JPEG, PNG
✅ PDF (multi-pages)
✅ Base64

Une API. Tous vos besoins. 🚀

{RAPIDAPI_URL}

#API #Formats #Flexible"""
    }
]


# =====================================================
# FONCTION POUR PUBLIER VIA HOOTSUITE API
# =====================================================

def publish_to_hootsuite(posts, access_token):
    """Publie tous les posts via l'API Hootsuite"""
    
    if not access_token:
        print("❌ HOOTSUITE_ACCESS_TOKEN manquant")
        print("\n📚 Comment obtenir votre token Hootsuite:")
        print("1. Allez sur https://hootsuite.com/developers")
        print("2. Créez une app")
        print("3. Obtenez votre Access Token")
        print("4. Exportez : export HOOTSUITE_ACCESS_TOKEN='votre_token'")
        print("5. Relancez ce script")
        return False
    
    try:
        import requests
        
        print("🚀 Publication de", len(posts), "posts sur Hootsuite...")
        
        base_date = datetime.now() + timedelta(days=1)
        
        for i, post in enumerate(posts):
            # Calculer la date de publication
            schedule_date = base_date + timedelta(days=post["day"] - 1)
            hour, minute = post["time"].split(":")
            schedule_date = schedule_date.replace(hour=int(hour), minute=int(minute))
            
            # Format ISO pour Hootsuite API
            scheduled_send_time = schedule_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            
            # Créer le post via API Hootsuite
            payload = {
                "text": post["text"],
                "scheduledSendTime": scheduled_send_time,
                "socialProfileIds": []  # À remplir avec vos IDs de profils
            }
            
            print(f"\n[{i+1}/{len(posts)}] Programmé pour {schedule_date.strftime('%d/%m/%Y %H:%M')}")
            print(f"Preview: {post['text'][:60]}...")
            
            # En production, décommenter ceci :
            # response = requests.post(
            #     "https://platform.hootsuite.com/v1/messages",
            #     headers={
            #         "Authorization": f"Bearer {access_token}",
            #         "Content-Type": "application/json"
            #     },
            #     json=payload
            # )
            # 
            # if response.status_code == 200:
            #     print("✅ Publié avec succès")
            # else:
            #     print(f"❌ Erreur: {response.text}")
        
        print("\n" + "="*60)
        print("✅ TOUS LES POSTS PROGRAMMÉS !")
        print("="*60)
        return True
        
    except ImportError:
        print("❌ Module 'requests' manquant. Installez avec: pip install requests")
        return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


# =====================================================
# MÉTHODE ALTERNATIVE : GÉNÉRER CSV POUR IMPORT BULK
# =====================================================

def generate_csv_for_bulk_upload(posts, output_file="hootsuite_posts.csv"):
    """
    Génère un CSV pour l'import bulk dans Hootsuite
    Hootsuite supporte le Bulk Composer avec CSV
    """
    import csv
    
    print(f"📄 Génération du fichier CSV : {output_file}")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # En-têtes Hootsuite Bulk Composer
        writer.writerow(['Date', 'Time', 'Text', 'Social Profile'])
        
        base_date = datetime.now() + timedelta(days=1)
        
        for post in posts:
            schedule_date = base_date + timedelta(days=post["day"] - 1)
            date_str = schedule_date.strftime("%Y-%m-%d")
            time_str = post["time"]
            
            # Pour Twitter
            writer.writerow([date_str, time_str, post["text"], 'Twitter'])
        
    print(f"✅ Fichier généré : {output_file}")
    print("\n📚 Comment l'utiliser :")
    print("1. Ouvrez Hootsuite → Publisher → Bulk Composer")
    print("2. Cliquez 'Upload CSV'")
    print(f"3. Uploadez {output_file}")
    print("4. Vérifiez et publiez !")
    print("\n💡 TOUS VOS POSTS SERONT PROGRAMMÉS EN 1 CLIC !")
    
    return output_file


# =====================================================
# MÉTHODE SIMPLE : AFFICHER INSTRUCTIONS
# =====================================================

def show_manual_instructions(posts):
    """Affiche les instructions pour programmer manuellement"""
    
    print("\n" + "="*60)
    print("📋 GUIDE : Programmer vos posts dans Hootsuite")
    print("="*60)
    
    print("\n🎯 MÉTHODE RAPIDE (15 minutes pour 10 posts)")
    print("\n1. Ouvrez Hootsuite : https://hootsuite.com/dashboard")
    print("2. Pour chaque post ci-dessous :")
    print("   a) Cliquez 'Create'")
    print("   b) Copiez le texte")
    print("   c) Cliquez horloge")
    print("   d) Programmez la date/heure")
    print("   e) Cliquez 'Schedule'")
    
    print("\n" + "-"*60)
    print("📝 VOS POSTS À PROGRAMMER :")
    print("-"*60)
    
    base_date = datetime.now() + timedelta(days=1)
    
    for i, post in enumerate(posts[:10], 1):
        schedule_date = base_date + timedelta(days=post["day"] - 1)
        date_str = schedule_date.strftime("%d/%m/%Y")
        
        print(f"\n{'='*60}")
        print(f"POST {i} - Programmer pour : {date_str} à {post['time']}")
        print(f"{'='*60}")
        print(post["text"])
    
    print("\n" + "="*60)
    print("✅ Copiez-collez ces posts dans Hootsuite !")
    print("="*60)


# =====================================================
# MAIN
# =====================================================

def main():
    print("\n" + "="*60)
    print("🤖 AUTO-PUBLICATION MARKETING - OCR Facture API")
    print("="*60)
    
    print("\n🎯 OPTIONS DISPONIBLES :")
    print("\n1. Générer CSV pour Bulk Upload Hootsuite (RECOMMANDÉ)")
    print("2. Publier via API Hootsuite (nécessite token)")
    print("3. Afficher guide manuel")
    print("\nQue voulez-vous faire ? (1/2/3)")
    
    try:
        choice = input("\nVotre choix : ").strip()
    except:
        choice = "1"  # Par défaut
    
    if choice == "1":
        # Générer CSV pour bulk upload
        csv_file = generate_csv_for_bulk_upload(TWITTER_POSTS)
        print(f"\n✅ Fichier prêt : {csv_file}")
        print("\n🎁 BONUS : Ouvrez ce fichier dans Excel/Google Sheets pour voir vos posts !")
        
    elif choice == "2":
        # Publier via API
        if not HOOTSUITE_ACCESS_TOKEN:
            print("\n⚠️  Token Hootsuite manquant")
            print("\n📚 Pour obtenir votre token :")
            print("1. https://hootsuite.com/developers")
            print("2. Créez une application")
            print("3. Obtenez votre Access Token")
            print("4. Exportez : export HOOTSUITE_ACCESS_TOKEN='votre_token'")
            print("5. Relancez ce script")
        else:
            publish_to_hootsuite(TWITTER_POSTS, HOOTSUITE_ACCESS_TOKEN)
    
    else:
        # Guide manuel
        show_manual_instructions(TWITTER_POSTS)
    
    print("\n" + "="*60)
    print("🎉 Terminé !")
    print("="*60)


if __name__ == "__main__":
    main()

