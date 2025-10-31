#!/usr/bin/env python3
"""
Script de test pour l'API OCR Facture
Utilisez ce script pour tester votre API avant de la déployer
"""

import requests
import json
import sys
import os

BASE_URL = os.getenv("API_URL", "http://localhost:8000")
DEBUG_MODE = os.getenv("DEBUG_MODE", "True").lower() == "true"

def test_health():
    """Test l'endpoint /health"""
    print("🔍 Test de l'endpoint /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_languages():
    """Test l'endpoint /languages"""
    print("\n🔍 Test de l'endpoint /languages...")
    try:
        response = requests.get(f"{BASE_URL}/languages")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {json.dumps(response.json(), indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_ocr_upload(image_path):
    """Test l'endpoint /ocr/upload"""
    print(f"\n🔍 Test de l'endpoint /ocr/upload avec {image_path}...")
    
    if not os.path.exists(image_path):
        print(f"❌ Fichier non trouvé: {image_path}")
        return False
    
    try:
        headers = {}
        if not DEBUG_MODE:
            secret = os.getenv("RAPIDAPI_PROXY_SECRET")
            if secret:
                headers["X-RapidAPI-Proxy-Secret"] = secret
        
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
            data = {'language': 'fra'}
            response = requests.post(
                f"{BASE_URL}/ocr/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        print(f"✅ Status: {response.status_code}")
        result = response.json()
        
        if result.get("success"):
            print("✅ OCR réussi!")
            extracted = result.get("extracted_data", {})
            print(f"\n📄 Données extraites:")
            print(f"  - Total: {extracted.get('total')}")
            print(f"  - Date: {extracted.get('date')}")
            print(f"  - Numéro facture: {extracted.get('invoice_number')}")
            print(f"  - Vendeur: {extracted.get('vendor')}")
            print(f"  - Client: {extracted.get('client')}")
        else:
            print(f"❌ Erreur: {result.get('error')}")
        
        return result.get("success", False)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("🚀 Test de l'API OCR Facture\n")
    print(f"📍 URL de base: {BASE_URL}")
    print(f"🔧 Mode debug: {DEBUG_MODE}\n")
    
    # Tests de base
    health_ok = test_health()
    languages_ok = test_languages()
    
    # Test OCR si une image est fournie
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        ocr_ok = test_ocr_upload(image_path)
    else:
        print("\n⚠️  Aucune image fournie pour tester l'OCR")
        print("   Usage: python test_api.py <chemin_vers_image.jpg>")
        ocr_ok = True
    
    # Résumé
    print("\n" + "="*50)
    print("📊 Résumé des tests:")
    print(f"  Health: {'✅' if health_ok else '❌'}")
    print(f"  Languages: {'✅' if languages_ok else '❌'}")
    if len(sys.argv) > 1:
        print(f"  OCR Upload: {'✅' if ocr_ok else '❌'}")
    print("="*50)
    
    if health_ok and languages_ok and ocr_ok:
        print("\n🎉 Tous les tests sont passés!")
        return 0
    else:
        print("\n⚠️  Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    sys.exit(main())

