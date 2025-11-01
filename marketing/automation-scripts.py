"""
Scripts d'automatisation marketing pour OCR Facture API
Poster automatiquement sur Twitter, LinkedIn, envoyer emails, tracker analytics
"""

import os
import time
import json
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Optional

# =====================================================
# CONFIGURATION
# =====================================================

# Variables d'environnement à configurer
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET", "")

LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN", "")

MAILCHIMP_API_KEY = os.getenv("MAILCHIMP_API_KEY", "")
MAILCHIMP_LIST_ID = os.getenv("MAILCHIMP_LIST_ID", "")

RAPIDAPI_URL = "https://rapidapi.com/api/ocr-facture-api"
LANDING_PAGE_URL = "https://ocr-facture-api-production.up.railway.app"

# =====================================================
# TWITTER AUTOMATION
# =====================================================

class TwitterBot:
    """Automatisation Twitter"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        
        # Alternative : Utiliser tweepy
        try:
            import tweepy
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_secret)
            self.api = tweepy.API(auth)
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )
        except ImportError:
            print("❌ Tweepy non installé. Installez avec: pip install tweepy")
            self.api = None
            self.client = None
    
    def post_tweet(self, text: str) -> bool:
        """Poster un tweet"""
        if not self.client:
            print(f"🔧 [SIMULATION] Tweet posté: {text[:50]}...")
            return True
        
        try:
            response = self.client.create_tweet(text=text)
            print(f"✅ Tweet posté: {text[:50]}...")
            return True
        except Exception as e:
            print(f"❌ Erreur Twitter: {e}")
            return False
    
    def schedule_tweets(self, tweets: List[str], interval_hours: int = 24):
        """Programmer une série de tweets"""
        print(f"📅 Planning {len(tweets)} tweets (intervalle: {interval_hours}h)")
        
        for i, tweet in enumerate(tweets):
            print(f"\n[{i+1}/{len(tweets)}] Scheduled for: {datetime.now() + timedelta(hours=i*interval_hours)}")
            # En production, utiliser un scheduler comme Celery ou APScheduler
            print(f"Tweet: {tweet}")


# =====================================================
# LINKEDIN AUTOMATION
# =====================================================

class LinkedInBot:
    """Automatisation LinkedIn"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.api_url = "https://api.linkedin.com/v2"
    
    def post_update(self, text: str, url: Optional[str] = None) -> bool:
        """Poster une mise à jour LinkedIn"""
        if not self.access_token:
            print(f"🔧 [SIMULATION] LinkedIn post: {text[:50]}...")
            return True
        
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        # Get user ID first
        try:
            me_response = requests.get(
                f"{self.api_url}/me",
                headers=headers
            )
            user_id = me_response.json().get("id")
            
            # Create post
            post_data = {
                "author": f"urn:li:person:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "ARTICLE" if url else "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            if url:
                post_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "originalUrl": url
                }]
            
            response = requests.post(
                f"{self.api_url}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            if response.status_code == 201:
                print(f"✅ LinkedIn post publié")
                return True
            else:
                print(f"❌ Erreur LinkedIn: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur LinkedIn: {e}")
            return False


# =====================================================
# EMAIL AUTOMATION (Mailchimp)
# =====================================================

class EmailAutomation:
    """Automatisation email avec Mailchimp"""
    
    def __init__(self, api_key: str, list_id: str):
        self.api_key = api_key
        self.list_id = list_id
        self.dc = api_key.split('-')[-1] if api_key else "us1"
        self.api_url = f"https://{self.dc}.api.mailchimp.com/3.0"
    
    def add_subscriber(self, email: str, first_name: str = "", last_name: str = "") -> bool:
        """Ajouter un abonné à la newsletter"""
        if not self.api_key:
            print(f"🔧 [SIMULATION] Ajout subscriber: {email}")
            return True
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "email_address": email,
            "status": "subscribed",
            "merge_fields": {
                "FNAME": first_name,
                "LNAME": last_name
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/lists/{self.list_id}/members",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                print(f"✅ Subscriber ajouté: {email}")
                return True
            else:
                print(f"❌ Erreur Mailchimp: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            return False
    
    def send_welcome_email(self, email: str):
        """Envoyer email de bienvenue (via automation Mailchimp)"""
        print(f"📧 Email de bienvenue envoyé à {email}")
        # En production, configuré via interface Mailchimp
    
    def send_drip_campaign(self, email: str, campaign_id: str):
        """Démarrer une campagne drip pour un utilisateur"""
        print(f"📧 Drip campaign démarrée pour {email}")
        # En production, configuré via automations Mailchimp


# =====================================================
# ANALYTICS TRACKER
# =====================================================

class AnalyticsTracker:
    """Tracker les conversions et analytics"""
    
    def __init__(self):
        self.events = []
    
    def track_signup(self, source: str, plan: str = "free"):
        """Tracker une inscription"""
        event = {
            "type": "signup",
            "source": source,
            "plan": plan,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        print(f"📊 Signup tracked: {source} -> {plan}")
        
        # En production, envoyer à Google Analytics, Mixpanel, etc.
        # ga('send', 'event', 'Signup', source, plan)
    
    def track_conversion(self, user_email: str, plan: str, amount: float):
        """Tracker une conversion payante"""
        event = {
            "type": "conversion",
            "user": user_email,
            "plan": plan,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        print(f"💰 Conversion tracked: {plan} - ${amount}")
    
    def get_stats(self) -> Dict:
        """Obtenir les statistiques"""
        signups = [e for e in self.events if e["type"] == "signup"]
        conversions = [e for e in self.events if e["type"] == "conversion"]
        
        return {
            "total_signups": len(signups),
            "total_conversions": len(conversions),
            "conversion_rate": len(conversions) / len(signups) * 100 if signups else 0,
            "total_revenue": sum(e["amount"] for e in conversions),
            "avg_revenue_per_conversion": sum(e["amount"] for e in conversions) / len(conversions) if conversions else 0
        }


# =====================================================
# CONTENT SCHEDULER
# =====================================================

class ContentScheduler:
    """Planifier et publier du contenu automatiquement"""
    
    def __init__(self, twitter_bot: TwitterBot, linkedin_bot: LinkedInBot):
        self.twitter = twitter_bot
        self.linkedin = linkedin_bot
        self.schedule = []
    
    def load_content_calendar(self, filepath: str):
        """Charger le calendrier de contenu depuis un fichier"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = json.load(f)
                self.schedule = content
                print(f"✅ {len(self.schedule)} posts chargés")
        except Exception as e:
            print(f"❌ Erreur chargement: {e}")
    
    def publish_next(self):
        """Publier le prochain post planifié"""
        if not self.schedule:
            print("📭 Aucun post en attente")
            return
        
        next_post = self.schedule.pop(0)
        
        if next_post.get("platform") == "twitter":
            self.twitter.post_tweet(next_post["content"])
        elif next_post.get("platform") == "linkedin":
            self.linkedin.post_update(next_post["content"], next_post.get("url"))
        
        print(f"✅ Post publié ({next_post['platform']})")
    
    def run_daily(self):
        """Exécuter quotidiennement (via cron job)"""
        print(f"🚀 Running daily automation - {datetime.now()}")
        
        # Publier sur Twitter
        self.publish_next()
        
        # Attendre 2h et publier sur LinkedIn
        # time.sleep(7200)
        # self.publish_next()


# =====================================================
# LEAD MAGNET AUTOMATION
# =====================================================

class LeadMagnetAutomation:
    """Automatiser la distribution de lead magnets"""
    
    def __init__(self, email_automation: EmailAutomation):
        self.email = email_automation
    
    def send_ebook(self, user_email: str):
        """Envoyer l'ebook gratuit après inscription"""
        print(f"📚 Ebook envoyé à {user_email}")
        # En production, envoyer email avec lien téléchargement
    
    def send_checklist(self, user_email: str):
        """Envoyer la checklist automation"""
        print(f"✅ Checklist envoyée à {user_email}")
    
    def send_roi_calculator(self, user_email: str):
        """Envoyer le lien du calculateur ROI"""
        print(f"💰 Calculateur ROI envoyé à {user_email}")


# =====================================================
# EXEMPLE D'UTILISATION
# =====================================================

def main():
    """Exemple d'utilisation des scripts d'automatisation"""
    
    print("=" * 60)
    print("🤖 AUTOMATION MARKETING - OCR Facture API")
    print("=" * 60)
    
    # Initialiser les bots
    twitter = TwitterBot(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )
    
    linkedin = LinkedInBot(LINKEDIN_ACCESS_TOKEN)
    
    email_automation = EmailAutomation(MAILCHIMP_API_KEY, MAILCHIMP_LIST_ID)
    
    analytics = AnalyticsTracker()
    
    # 1. Poster sur Twitter
    print("\n📱 TWITTER")
    print("-" * 60)
    twitter.post_tweet(
        "🚀 Extrayez les données de vos factures en 3 lignes de Python ! "
        "Trial gratuit 100 req/mois. #API #OCR #Python\n"
        f"{RAPIDAPI_URL}"
    )
    
    # 2. Poster sur LinkedIn
    print("\n💼 LINKEDIN")
    print("-" * 60)
    linkedin.post_update(
        "💡 Comment notre API OCR Facture aide les startups fintech à économiser 160h/mois.\n\n"
        "Use case concret + ROI détaillé dans cet article.",
        url=LANDING_PAGE_URL
    )
    
    # 3. Ajouter un subscriber
    print("\n📧 EMAIL")
    print("-" * 60)
    email_automation.add_subscriber(
        "nouveau.client@example.com",
        "Nouveau",
        "Client"
    )
    
    # 4. Tracker analytics
    print("\n📊 ANALYTICS")
    print("-" * 60)
    analytics.track_signup("twitter", "free")
    analytics.track_signup("linkedin", "free")
    analytics.track_conversion("client@example.com", "pro", 15.0)
    
    stats = analytics.get_stats()
    print(f"\nStatistiques:")
    print(f"  - Signups: {stats['total_signups']}")
    print(f"  - Conversions: {stats['total_conversions']}")
    print(f"  - Taux conversion: {stats['conversion_rate']:.1f}%")
    print(f"  - Revenue total: ${stats['total_revenue']:.2f}")
    
    # 5. Scheduler de contenu
    print("\n📅 CONTENT SCHEDULER")
    print("-" * 60)
    scheduler = ContentScheduler(twitter, linkedin)
    
    # Example content calendar
    sample_schedule = [
        {
            "platform": "twitter",
            "content": "💻 Nouveau tutorial : Intégration OCR en Python en 10 minutes",
            "scheduled_for": "2024-01-15 09:00"
        },
        {
            "platform": "linkedin",
            "content": "📊 Case study : Comment une startup économise 160h/mois",
            "url": LANDING_PAGE_URL,
            "scheduled_for": "2024-01-15 12:00"
        }
    ]
    
    # Sauvegarder le calendrier
    with open('content_schedule.json', 'w') as f:
        json.dump(sample_schedule, f, indent=2)
    
    print("✅ Calendrier de contenu créé : content_schedule.json")
    
    print("\n" + "=" * 60)
    print("✅ Automation terminée !")
    print("=" * 60)
    
    print("\n📝 PROCHAINES ÉTAPES:")
    print("  1. Configurer les variables d'environnement (Twitter, LinkedIn, Mailchimp)")
    print("  2. Installer les dépendances : pip install tweepy requests")
    print("  3. Configurer un cron job pour exécuter quotidiennement")
    print("  4. Personnaliser les messages selon votre audience")
    print("\n🔗 Documentation:")
    print("  - Twitter API: https://developer.twitter.com/")
    print("  - LinkedIn API: https://docs.microsoft.com/linkedin/")
    print("  - Mailchimp API: https://mailchimp.com/developer/")


if __name__ == "__main__":
    main()


# =====================================================
# CONFIGURATION CRON (Linux/Mac)
# =====================================================
"""
Pour exécuter automatiquement tous les jours à 9h :

1. Ouvrir crontab :
   crontab -e

2. Ajouter cette ligne :
   0 9 * * * cd /path/to/marketing && python automation-scripts.py

3. Sauvegarder et quitter

Le script s'exécutera automatiquement chaque jour à 9h.
"""


# =====================================================
# CONFIGURATION WINDOWS TASK SCHEDULER
# =====================================================
"""
1. Ouvrir "Task Scheduler"
2. Créer une tâche basique
3. Déclencheur : Quotidien à 9h
4. Action : Démarrer un programme
5. Programme : python.exe
6. Arguments : C:\\path\\to\\automation-scripts.py
7. Sauvegarder
"""

