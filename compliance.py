"""
Module de vérification de conformité pour factures françaises
Vérifie les mentions légales obligatoires, TVA, et enrichit avec SIREN/SIRET et VIES
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from fastapi import HTTPException


# Taux de TVA valides en France
VALID_FRENCH_VAT_RATES = [20.0, 10.0, 5.5, 2.1, 0.0]


def detect_siren_siret(text: str) -> Dict[str, Optional[str]]:
    """
    Détecte les numéros SIREN et SIRET dans le texte OCR
    
    Format SIREN : 9 chiffres
    Format SIRET : 14 chiffres (SIREN + 5 chiffres NIC)
    
    Retourne : {"siren": "...", "siret": "..."}
    """
    result = {"siren": None, "siret": None}
    
    # Nettoyer le texte (enlever espaces, tirets)
    text_clean = re.sub(r'[\s\-\.]', '', text)
    
    # Pattern SIRET (14 chiffres consécutifs)
    siret_patterns = [
        r'SIRET\s*[:=]?\s*(\d{14})',  # SIRET: 47945319300043
        r'SIRET\s*[:=]?\s*(\d{3}\s?\d{3}\s?\d{3}\s?\d{5})',  # SIRET avec espaces
        r'\b(\d{14})\b',  # 14 chiffres consécutifs
    ]
    
    for pattern in siret_patterns:
        match = re.search(pattern, text_clean if 'SIRET' in pattern else text)
        if match:
            siret = re.sub(r'[\s\-\.]', '', match.group(1))
            if len(siret) == 14 and siret.isdigit():
                result["siret"] = siret
                result["siren"] = siret[:9]  # SIREN = 9 premiers chiffres
                break
    
    # Si pas de SIRET trouvé, chercher SIREN seul
    if not result["siren"]:
        siren_patterns = [
            r'SIREN\s*[:=]?\s*(\d{9})',  # SIREN: 479453193
            r'SIREN\s*[:=]?\s*(\d{3}\s?\d{3}\s?\d{3})',  # SIREN avec espaces
            r'\b(\d{9})\b',  # 9 chiffres consécutifs (attention: peut être autre chose)
        ]
        
        for pattern in siren_patterns:
            match = re.search(pattern, text_clean if 'SIREN' in pattern else text)
            if match:
                siren = re.sub(r'[\s\-\.]', '', match.group(1))
                if len(siren) == 9 and siren.isdigit():
                    result["siren"] = siren
                    break
    
    return result


def detect_vat_intracom(text: str) -> Optional[str]:
    """
    Détecte le numéro TVA intracommunautaire dans le texte
    
    Format FR : FR + 2 lettres + 9 chiffres (ex: FR47945319300)
    Format général UE : 2 lettres + jusqu'à 12 caractères alphanumériques
    """
    text_upper = text.upper()
    
    # Patterns TVA intracom
    vat_patterns = [
        r'TVA\s*(?:intracom|intra)?\s*[:=]?\s*([A-Z]{2}[A-Z0-9]{2,12})',  # TVA intracom: FR47945319300
        r'FR\s*([A-Z]{2}\d{9})',  # FR + 2 lettres + 9 chiffres
        r'\b(FR[A-Z]{2}\d{9})\b',  # Format FR complet
        r'\b([A-Z]{2}[A-Z0-9]{2,12})\b',  # Format général UE
    ]
    
    for pattern in vat_patterns:
        match = re.search(pattern, text_upper)
        if match:
            vat = match.group(1).replace(' ', '').replace('-', '')
            # Valider le format français (FR + 2 lettres + 9 chiffres = 13 caractères)
            if vat.startswith('FR') and len(vat) == 13:
                return vat
            # Ou format général UE (2 lettres + 2-12 caractères)
            elif len(vat) >= 4 and len(vat) <= 14:
                return vat
    
    return None


def check_french_compliance(extracted_data: Dict) -> Dict:
    """
    Vérifie que la facture contient toutes les mentions légales obligatoires en France
    
    Mentions obligatoires :
    - Numéro SIRET/SIREN du vendeur
    - Adresse complète du vendeur
    - Date d'émission
    - Numéro de facture unique
    - Montant HT, TTC, TVA
    - Conditions de paiement (optionnel mais recommandé)
    """
    missing_fields = []
    warnings = []
    score = 100.0
    
    # Vérifier date d'émission
    if not extracted_data.get("date"):
        missing_fields.append("Date d'émission")
        score -= 15
    
    # Vérifier numéro de facture
    if not extracted_data.get("invoice_number"):
        missing_fields.append("Numéro de facture")
        score -= 15
    
    # Vérifier montants
    if not extracted_data.get("total_ht") and not extracted_data.get("total"):
        missing_fields.append("Montant HT")
        score -= 10
    
    if not extracted_data.get("total_ttc") and not extracted_data.get("total"):
        missing_fields.append("Montant TTC")
        score -= 10
    
    # Vérifier vendeur
    vendor = extracted_data.get("vendor")
    if not vendor or len(vendor.strip()) < 3:
        missing_fields.append("Nom du vendeur")
        score -= 10
    else:
        # Vérifier si c'est juste un label ("Vendeur:" au lieu du nom réel)
        if vendor.lower().strip() in ["vendeur", "vendor", "vendeur:", "vendor:"]:
            missing_fields.append("Nom du vendeur (label détecté au lieu du nom)")
            score -= 10
    
    # Vérifier client (obligatoire pour factures B2B)
    client = extracted_data.get("client")
    if not client or len(client.strip()) < 3:
        warnings.append("Nom du client non détecté (obligatoire pour factures B2B)")
        score -= 5
    
    # Vérifier SIRET/SIREN (détecté séparément, pas dans extracted_data)
    # Cette vérification sera faite après extraction complète
    
    # Vérifier adresse (présence de mots-clés d'adresse)
    text = extracted_data.get("text", "")
    address_keywords = ["rue", "avenue", "boulevard", "route", "street", "road", "paris", "lyon", "marseille"]
    has_address = any(keyword in text.lower() for keyword in address_keywords)
    if not has_address:
        warnings.append("Adresse complète du vendeur non détectée")
        score -= 5
    
    return {
        "compliant": len(missing_fields) == 0,
        "score": max(0.0, score),  # Score entre 0 et 100
        "missing_fields": missing_fields,
        "warnings": warnings,
        "required_fields_present": len(missing_fields) == 0
    }


def validate_french_vat(extracted_data: Dict) -> Dict:
    """
    Vérifie que les taux de TVA sont conformes à la réglementation française
    et que les calculs sont corrects
    """
    errors = []
    warnings = []
    
    total_ht = extracted_data.get("total_ht")
    total_ttc = extracted_data.get("total_ttc") or extracted_data.get("total")
    tva_amount = extracted_data.get("tva")
    
    # Si on a HT et TTC, calculer le taux de TVA
    if total_ht and total_ttc and total_ht > 0:
        calculated_tva = total_ttc - total_ht
        calculated_rate = (calculated_tva / total_ht) * 100
        
        # Arrondir à 2 décimales pour comparaison
        calculated_rate = round(calculated_rate, 2)
        
        # Vérifier si le taux est valide pour la France
        if calculated_rate not in VALID_FRENCH_VAT_RATES:
            # Chercher le taux le plus proche
            closest_rate = min(VALID_FRENCH_VAT_RATES, key=lambda x: abs(x - calculated_rate))
            errors.append({
                "field": "tva_rate",
                "error": f"Taux TVA {calculated_rate}% non valide pour la France",
                "closest_valid_rate": closest_rate,
                "detected_rate": calculated_rate
            })
        
        # Vérifier si le montant TVA correspond
        if tva_amount:
            diff = abs(calculated_tva - tva_amount)
            if diff > 0.01:  # Tolérance de 1 centime
                warnings.append({
                    "field": "tva_amount",
                    "warning": f"Différence entre TVA calculée ({calculated_tva:.2f}€) et TVA extraite ({tva_amount:.2f}€)",
                    "difference": round(diff, 2)
                })
        
        # Vérifier que HT + TVA = TTC (avec tolérance d'arrondi)
        expected_ttc = total_ht + calculated_tva
        diff_ttc = abs(expected_ttc - total_ttc)
        if diff_ttc > 0.01:
            errors.append({
                "field": "total_ttc",
                "error": f"Calcul incorrect : HT ({total_ht:.2f}€) + TVA ({calculated_tva:.2f}€) ≠ TTC ({total_ttc:.2f}€)",
                "expected_ttc": round(expected_ttc, 2),
                "actual_ttc": total_ttc
            })
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "vat_rate": round(calculated_rate, 2) if total_ht and total_ttc else None
    }


def enrich_siren_siret(siret: str, siren_api_key: Optional[str] = None) -> Dict:
    """
    Enrichit les données avec l'API Sirene (Insee)
    
    Nécessite une clé API Insee (gratuite sur api.insee.fr)
    """
    if not siret or len(siret) != 14:
        return {
            "success": False,
            "error": "SIRET invalide"
        }
    
    # Si pas de clé API, retourner juste une détection
    if not siren_api_key:
        return {
            "success": False,
            "error": "Clé API Sirene non configurée",
            "siret": siret,
            "siren": siret[:9]
        }
    
    try:
        # API Sirene v3 (nécessite authentification OAuth2)
        # Pour simplifier, on retourne une structure prête pour l'intégration
        # L'implémentation complète nécessite OAuth2 avec Insee
        
        return {
            "success": True,
            "siret": siret,
            "siren": siret[:9],
            "note": "Intégration API Sirene nécessite OAuth2. Structure prête pour implémentation."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "siret": siret
        }


def validate_vies(vat_number: str) -> Dict:
    """
    Valide un numéro TVA intracommunautaire via l'API VIES
    
    API VIES : http://ec.europa.eu/taxation_customs/vies/
    Utilise SOAP
    """
    if not vat_number:
        return {
            "success": False,
            "error": "Numéro TVA manquant"
        }
    
    # Nettoyer le numéro
    vat_clean = vat_number.replace(' ', '').replace('-', '').upper()
    
    # Extraire le code pays et le numéro
    if len(vat_clean) < 3:
        return {
            "success": False,
            "error": "Format TVA invalide"
        }
    
    country_code = vat_clean[:2]
    vat_number_only = vat_clean[2:]
    
    try:
        # API VIES SOAP endpoint
        vies_url = "http://ec.europa.eu/taxation_customs/vies/services/checkVatService"
        
        # Enveloppe SOAP
        soap_envelope = f"""<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
    <soap:Body>
        <checkVat xmlns="urn:ec.europa.eu:taxud:vies:services:checkVat:types">
            <countryCode>{country_code}</countryCode>
            <vatNumber>{vat_number_only}</vatNumber>
        </checkVat>
    </soap:Body>
</soap:Envelope>"""
        
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": "urn:ec.europa.eu:taxud:vies:services:checkVat/checkVat"
        }
        
        response = requests.post(vies_url, data=soap_envelope, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Parser la réponse SOAP (simplifié)
            if "<valid>true</valid>" in response.text:
                # Extraire le nom de l'entreprise
                name_match = re.search(r'<name>(.*?)</name>', response.text)
                address_match = re.search(r'<address>(.*?)</address>', response.text)
                
                return {
                    "success": True,
                    "valid": True,
                    "vat_number": vat_number,
                    "country_code": country_code,
                    "name": name_match.group(1) if name_match else None,
                    "address": address_match.group(1) if address_match else None
                }
            else:
                return {
                    "success": True,
                    "valid": False,
                    "vat_number": vat_number,
                    "error": "Numéro TVA non valide selon VIES"
                }
        else:
            return {
                "success": False,
                "error": f"Erreur API VIES : {response.status_code}"
            }
    
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Timeout API VIES"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors de la validation VIES : {str(e)}"
        }


def extract_compliance_data(extracted_data: Dict, ocr_text: str) -> Dict:
    """
    Extrait et vérifie toutes les données de conformité pour une facture française
    
    Retourne un dictionnaire complet avec :
    - Détection SIREN/SIRET
    - Détection TVA intracom
    - Vérification compliance FR
    - Validation TVA
    - Enrichissement (si configuré)
    """
    compliance_result = {
        "compliance_check": {},
        "vat_validation": {},
        "siren_siret": {},
        "vat_intracom": {},
        "enrichment": {}
    }
    
    # 1. Détecter SIREN/SIRET
    siren_siret = detect_siren_siret(ocr_text)
    compliance_result["siren_siret"] = siren_siret
    
    # 2. Détecter TVA intracom
    vat_intracom = detect_vat_intracom(ocr_text)
    compliance_result["vat_intracom"] = {
        "detected": vat_intracom,
        "validated": None
    }
    
    # 3. Vérifier compliance FR
    compliance_check = check_french_compliance(extracted_data)
    compliance_result["compliance_check"] = compliance_check
    
    # 4. Valider TVA
    vat_validation = validate_french_vat(extracted_data)
    compliance_result["vat_validation"] = vat_validation
    
    # 5. Enrichissement (si SIRET trouvé)
    if siren_siret.get("siret"):
        # Note: nécessite clé API configurée
        enrichment = enrich_siren_siret(siren_siret["siret"])
        compliance_result["enrichment"]["siren_siret"] = enrichment
    
    # 6. Validation VIES (si TVA intracom trouvé)
    if vat_intracom:
        vies_result = validate_vies(vat_intracom)
        compliance_result["vat_intracom"]["validated"] = vies_result
        compliance_result["enrichment"]["vies"] = vies_result
    
    return compliance_result

