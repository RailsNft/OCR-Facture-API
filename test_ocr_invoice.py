#!/usr/bin/env python3
"""
Script de test pour l'endpoint OCR avec une vraie image de facture
"""

import requests
import json
import sys
import os
from pathlib import Path

BASE_URL = "https://ocr-facture-api-production.up.railway.app"
RAPIDAPI_SECRET = "f67eb770-b6b9-11f0-9b0e-0f41c7e962fd"

def test_ocr_upload(image_path, language="fra"):
    """Test l'endpoint /ocr/upload avec une vraie image"""
    print(f"\n🔍 Test OCR avec l'image: {image_path}")
    print("=" * 60)
    
    if not os.path.exists(image_path):
        print(f"❌ Erreur: Fichier non trouvé: {image_path}")
        return False
    
    # Vérifier le type de fichier
    file_ext = Path(image_path).suffix.lower()
    if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
        print(f"⚠️  Avertissement: Format de fichier ({file_ext}) peut ne pas être supporté")
    
    try:
        headers = {
            "X-RapidAPI-Proxy-Secret": RAPIDAPI_SECRET
        }
        
        with open(image_path, 'rb') as f:
            files = {
                'file': (os.path.basename(image_path), f, f'image/{file_ext[1:]}')
            }
            data = {
                'language': language
            }
            
            print(f"📤 Envoi de la requête...")
            print(f"   URL: {BASE_URL}/ocr/upload")
            print(f"   Langue: {language}")
            print(f"   Fichier: {os.path.basename(image_path)}")
            
            response = requests.post(
                f"{BASE_URL}/ocr/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=60  # OCR peut prendre du temps
            )
        
        print(f"\n📥 Réponse reçue:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("success"):
                print("\n✅ OCR réussi!")
                print("\n" + "=" * 60)
                print("📄 DONNÉES EXTRAITES:")
                print("=" * 60)
                
                extracted = result.get("extracted_data", {})
                
                # Afficher les informations principales
                print(f"\n📋 Informations de la facture:")
                print(f"   • Date: {extracted.get('date', 'Non détectée')}")
                print(f"   • Numéro de facture: {extracted.get('invoice_number', 'Non détecté')}")
                print(f"   • Vendeur: {extracted.get('vendor', 'Non détecté')}")
                print(f"   • Client: {extracted.get('client', 'Non détecté')}")
                
                print(f"\n💰 Montants:")
                if extracted.get('total'):
                    print(f"   • Total: {extracted.get('total')} {extracted.get('currency', 'EUR')}")
                if extracted.get('total_ht'):
                    print(f"   • Total HT: {extracted.get('total_ht')} {extracted.get('currency', 'EUR')}")
                if extracted.get('total_ttc'):
                    print(f"   • Total TTC: {extracted.get('total_ttc')} {extracted.get('currency', 'EUR')}")
                if extracted.get('tva'):
                    print(f"   • TVA: {extracted.get('tva')} {extracted.get('currency', 'EUR')}")
                
                # Afficher un extrait du texte
                text = extracted.get('text', '')
                if text:
                    lines = text.split('\n')[:10]  # Premières 10 lignes
                    print(f"\n📝 Extrait du texte extrait (10 premières lignes):")
                    for i, line in enumerate(lines, 1):
                        if line.strip():
                            print(f"   {i}. {line[:80]}")  # Limiter à 80 caractères
                
                # Afficher le nombre de lignes
                all_lines = extracted.get('lines', [])
                print(f"\n📊 Statistiques:")
                print(f"   • Nombre de lignes extraites: {len(all_lines)}")
                print(f"   • Longueur du texte: {len(text)} caractères")
                
                print("\n" + "=" * 60)
                print("✅ Test réussi!")
                print("=" * 60)
                
                # Sauvegarder la réponse complète dans un fichier JSON
                output_file = f"ocr_result_{Path(image_path).stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Résultat complet sauvegardé dans: {output_file}")
                
                return True
            else:
                print(f"\n❌ Erreur dans la réponse:")
                print(f"   {result.get('error', 'Erreur inconnue')}")
                return False
        else:
            print(f"\n❌ Erreur HTTP {response.status_code}")
            try:
                error_data = response.json()
                print(f"   {json.dumps(error_data, indent=2)}")
            except:
                print(f"   {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ Timeout: La requête a pris trop de temps (>60s)")
        return False
    except Exception as e:
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    print("🚀 Test OCR Facture API avec image réelle")
    print("=" * 60)
    
    if len(sys.argv) < 2:
        print("\n❌ Usage: python test_ocr_invoice.py <chemin_vers_image> [langue]")
        print("\nExemples:")
        print("  python test_ocr_invoice.py facture.jpg")
        print("  python test_ocr_invoice.py facture.png fra")
        print("  python test_ocr_invoice.py invoice.jpg eng")
        print("\nLangues supportées: fra, eng, deu, spa, ita, por")
        sys.exit(1)
    
    image_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else "fra"
    
    success = test_ocr_upload(image_path, language)
    
    if success:
        print("\n🎉 Test terminé avec succès!")
        sys.exit(0)
    else:
        print("\n⚠️  Test terminé avec des erreurs")
        sys.exit(1)


if __name__ == "__main__":
    main()

