#!/usr/bin/env python3
"""
Script pour créer une facture de test en image PNG
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_test_invoice():
    """Crée une facture de test en PNG"""
    
    # Dimensions de l'image
    width = 800
    height = 1000
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Couleurs
    black = (0, 0, 0)
    dark_gray = (50, 50, 50)
    blue = (0, 102, 204)
    
    # Position initiale
    y = 50
    x_left = 50
    x_right = 400
    
    # Essayer d'utiliser une police système, sinon utiliser la police par défaut
    try:
        # Pour macOS
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        header_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        normal_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        try:
            # Pour Linux
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
            normal_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            # Police par défaut
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
    
    # En-tête - Titre
    draw.text((width//2, y), "FACTURE", fill=blue, font=title_font, anchor="mt")
    y += 50
    
    # Numéro de facture
    draw.text((x_left, y), "Facture N°: FAC-2024-001", fill=black, font=header_font)
    y += 30
    
    # Date
    draw.text((x_left, y), "Date: 15/03/2024", fill=black, font=normal_font)
    y += 40
    
    # Séparateur
    draw.line([(x_left, y), (width - x_left, y)], fill=dark_gray, width=2)
    y += 30
    
    # Informations vendeur
    draw.text((x_left, y), "Vendeur:", fill=dark_gray, font=header_font)
    y += 25
    draw.text((x_left + 20, y), "Société Example SARL", fill=black, font=normal_font)
    y += 20
    draw.text((x_left + 20, y), "123 Rue de l'Exemple", fill=black, font=normal_font)
    y += 20
    draw.text((x_left + 20, y), "75001 Paris, France", fill=black, font=normal_font)
    y += 30
    
    # Informations client
    draw.text((x_left, y), "Client:", fill=dark_gray, font=header_font)
    y += 25
    draw.text((x_left + 20, y), "Client ABC", fill=black, font=normal_font)
    y += 20
    draw.text((x_left + 20, y), "456 Avenue du Client", fill=black, font=normal_font)
    y += 20
    draw.text((x_left + 20, y), "69000 Lyon, France", fill=black, font=normal_font)
    y += 40
    
    # Séparateur
    draw.line([(x_left, y), (width - x_left, y)], fill=dark_gray, width=1)
    y += 20
    
    # En-tête tableau
    draw.text((x_left, y), "Description", fill=dark_gray, font=header_font)
    draw.text((x_right, y), "Montant HT", fill=dark_gray, font=header_font)
    y += 25
    
    # Ligne de séparation
    draw.line([(x_left, y), (width - x_left, y)], fill=dark_gray, width=1)
    y += 20
    
    # Articles
    items = [
        ("Consultation technique", "500.00"),
        ("Installation système", "350.00"),
        ("Formation équipe", "192.08"),
    ]
    
    for desc, amount in items:
        draw.text((x_left, y), desc, fill=black, font=normal_font)
        draw.text((x_right, y), f"{amount} €", fill=black, font=normal_font)
        y += 25
    
    y += 20
    
    # Totaux
    draw.line([(x_left, y), (width - x_left, y)], fill=dark_gray, width=1)
    y += 25
    
    draw.text((x_left, y), "Total HT:", fill=dark_gray, font=header_font)
    draw.text((x_right, y), "1042.08 €", fill=black, font=header_font)
    y += 25
    
    draw.text((x_left, y), "TVA (20%):", fill=dark_gray, font=normal_font)
    draw.text((x_right, y), "208.42 €", fill=black, font=normal_font)
    y += 25
    
    draw.line([(x_left, y), (width - x_left, y)], fill=dark_gray, width=2)
    y += 25
    
    draw.text((x_left, y), "Total TTC:", fill=blue, font=header_font)
    draw.text((x_right, y), "1250.50 €", fill=blue, font=header_font)
    y += 40
    
    # Conditions de paiement
    draw.text((x_left, y), "Conditions de paiement:", fill=dark_gray, font=normal_font)
    y += 20
    draw.text((x_left + 20, y), "Paiement à 30 jours", fill=black, font=normal_font)
    y += 20
    draw.text((x_left + 20, y), "Merci de votre confiance !", fill=black, font=normal_font)
    
    # Sauvegarder l'image
    output_file = "facture_test.png"
    image.save(output_file, "PNG")
    print(f"✅ Facture de test créée: {output_file}")
    print(f"\n📄 Contenu de la facture:")
    print("   - Numéro: FAC-2024-001")
    print("   - Date: 15/03/2024")
    print("   - Vendeur: Société Example SARL")
    print("   - Client: Client ABC")
    print("   - Total HT: 1042.08 €")
    print("   - TVA: 208.42 €")
    print("   - Total TTC: 1250.50 €")
    print(f"\n🧪 Pour tester avec l'API:")
    print(f"   python test_ocr_invoice.py {output_file} fra")
    print(f"\n   ou avec curl:")
    print(f"   curl -X POST 'https://ocr-facture-api-production.up.railway.app/ocr/upload' \\")
    print(f"     -H 'X-RapidAPI-Proxy-Secret: f67eb770-b6b9-11f0-9b0e-0f41c7e962fd' \\")
    print(f"     -F 'file=@{output_file}' \\")
    print(f"     -F 'language=fra' | python3 -m json.tool")
    
    return output_file

if __name__ == "__main__":
    create_test_invoice()

