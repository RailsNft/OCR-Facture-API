"""
Module de vérification de conformité pour factures françaises
Vérifie les mentions légales obligatoires, TVA, et enrichit avec SIREN/SIRET et VIES
"""

import re
import os
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
from fastapi import HTTPException
import tempfile


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


# Cache pour les tokens OAuth2 (évite de demander un nouveau token à chaque requête)
_token_cache: Dict[str, Dict] = {}


def _get_oauth2_token_client_credentials(
    client_id: str,
    client_certificate: str,
    token_url: str = "https://portail-api.insee.fr/token"
) -> Optional[str]:
    """
    Obtient un token OAuth2 avec Client Credentials flow et certificat client (mTLS)
    
    Args:
        client_id: Client ID
        client_certificate: Chemin vers le certificat PEM ou contenu du certificat
        token_url: URL du endpoint de token
    
    Returns:
        Token d'accès ou None en cas d'erreur
    """
    # Vérifier le cache de token
    cache_key = f"oauth2_token_{client_id}"
    if cache_key in _token_cache:
        cached_token = _token_cache[cache_key]
        expires_at = cached_token.get("expires_at")
        if expires_at and datetime.now() < expires_at:
            return cached_token.get("access_token")
    
    try:
        # Gérer le certificat (chemin fichier ou contenu)
        cert_path = None
        if os.path.exists(client_certificate):
            # C'est un chemin de fichier
            cert_path = client_certificate
        else:
            # C'est probablement le contenu du certificat
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as tmp_file:
                tmp_file.write(client_certificate)
                cert_path = tmp_file.name
        
        # Requête pour obtenir le token
        response = requests.post(
            token_url,
            data={"grant_type": "client_credentials"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            cert=cert_path,  # Certificat client pour mTLS
            auth=(client_id, ""),  # Client ID comme username
            timeout=10
        )
        
        # Nettoyer le fichier temporaire si créé
        if not os.path.exists(client_certificate) and cert_path:
            try:
                os.unlink(cert_path)
            except:
                pass
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)  # Par défaut 1 heure
            
            # Mettre en cache le token
            _token_cache[cache_key] = {
                "access_token": access_token,
                "expires_at": datetime.now() + timedelta(seconds=expires_in - 60)  # Expire 1 min avant
            }
            
            return access_token
        else:
            return None
    
    except Exception as e:
        return None


def _get_oauth2_token_consumer_key(
    consumer_key: str,
    consumer_secret: str,
    token_url: str = "https://portail-api.insee.fr/token"
) -> Optional[str]:
    """
    Obtient un token OAuth2 avec Consumer Key/Secret (ancien système)
    
    Args:
        consumer_key: Consumer Key
        consumer_secret: Consumer Secret
        token_url: URL du endpoint de token
    
    Returns:
        Token d'accès ou None en cas d'erreur
    """
    # Vérifier le cache de token
    cache_key = f"oauth2_token_{consumer_key}"
    if cache_key in _token_cache:
        cached_token = _token_cache[cache_key]
        expires_at = cached_token.get("expires_at")
        if expires_at and datetime.now() < expires_at:
            return cached_token.get("access_token")
    
    try:
        # Requête pour obtenir le token avec Basic Auth
        response = requests.post(
            token_url,
            data={"grant_type": "client_credentials"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            auth=(consumer_key, consumer_secret),
            timeout=10
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            
            # Mettre en cache le token
            _token_cache[cache_key] = {
                "access_token": access_token,
                "expires_at": datetime.now() + timedelta(seconds=expires_in - 60)
            }
            
            return access_token
        else:
            return None
    
    except Exception as e:
        return None


def _call_sirene_api(siret: str, access_token: str) -> Optional[Dict]:
    """
    Appelle l'API Sirene v3 pour obtenir les données d'un SIRET
    
    Args:
        siret: Numéro SIRET (14 chiffres)
        access_token: Token OAuth2
    
    Returns:
        Données de l'entreprise ou None en cas d'erreur
    """
    try:
        api_url = f"https://api.insee.fr/entreprises/sirene/v3/siret/{siret}"
        
        response = requests.get(
            api_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None  # SIRET non trouvé
        else:
            return None
    
    except Exception as e:
        return None


def _parse_sirene_response(sirene_data: Dict) -> Dict:
    """
    Parse la réponse de l'API Sirene et extrait les données pertinentes
    
    Args:
        sirene_data: Réponse JSON de l'API Sirene
    
    Returns:
        Dictionnaire avec les données structurées
    """
    try:
        # Structure de la réponse API Sirene v3
        etablissement = sirene_data.get("etablissement", {})
        periodes_etablissement = etablissement.get("periodesEtablissement", [])
        
        if not periodes_etablissement:
            return {}
        
        # Prendre la période la plus récente
        periode = periodes_etablissement[0]
        
        # Unite legale (si disponible)
        unite_legale = etablissement.get("uniteLegale", {})
        periodes_unite_legale = unite_legale.get("periodesUniteLegale", [])
        periode_unite = periodes_unite_legale[0] if periodes_unite_legale else {}
        
        # Adresse
        adresse = periode.get("adresseEtablissement", {})
        
        # Activité
        activite = periode.get("activitePrincipaleEtablissement", "")
        
        # Forme juridique
        forme_juridique = periode_unite.get("categorieJuridiqueUniteLegale", "")
        
        # Raison sociale
        denomination = periode_unite.get("denominationUniteLegale", "")
        nom = periode_unite.get("nomUniteLegale", "")
        prenom = periode_unite.get("prenom1UniteLegale", "")
        
        raison_sociale = denomination
        if not raison_sociale:
            if nom and prenom:
                raison_sociale = f"{prenom} {nom}"
            elif nom:
                raison_sociale = nom
        
        # Effectifs
        tranche_effectifs = periode.get("trancheEffectifsEtablissement", "")
        
        # Statut
        etat_administratif = periode.get("etatAdministratifEtablissement", "")
        statut = "Actif" if etat_administratif == "A" else "Inactif"
        
        # Date de création
        date_creation = periode.get("dateCreationEtablissement", "")
        
        # Date de cessation (si inactif)
        date_cessation = periode.get("dateDebut", "") if etat_administratif != "A" else None
        
        # Construire l'adresse complète
        adresse_complete = ""
        if adresse:
            adresse_parts = []
            if adresse.get("numeroVoieEtablissement"):
                adresse_parts.append(adresse.get("numeroVoieEtablissement"))
            if adresse.get("typeVoieEtablissement"):
                adresse_parts.append(adresse.get("typeVoieEtablissement"))
            if adresse.get("libelleVoieEtablissement"):
                adresse_parts.append(adresse.get("libelleVoieEtablissement"))
            if adresse_parts:
                adresse_complete = " ".join(adresse_parts)
            if adresse.get("codePostalEtablissement"):
                adresse_complete += f", {adresse.get('codePostalEtablissement')}"
            if adresse.get("libelleCommuneEtablissement"):
                adresse_complete += f" {adresse.get('libelleCommuneEtablissement')}"
        
        return {
            "siret": etablissement.get("siret", ""),
            "siren": etablissement.get("siren", ""),
            "raison_sociale": raison_sociale,
            "adresse_complete": adresse_complete,
            "code_postal": adresse.get("codePostalEtablissement", "") if adresse else "",
            "ville": adresse.get("libelleCommuneEtablissement", "") if adresse else "",
            "activite_principale": activite,
            "forme_juridique": forme_juridique,
            "statut": statut,
            "date_creation": date_creation,
            "date_cessation": date_cessation,
            "tranche_effectifs": tranche_effectifs,
            "source": "API Sirene (Insee)"
        }
    
    except Exception as e:
        return {}


def enrich_siren_siret(
    siret: str, 
    siren_api_key: Optional[str] = None,
    siren_api_secret: Optional[str] = None,
    siren_client_id: Optional[str] = None,
    siren_client_certificate: Optional[str] = None
) -> Dict:
    """
    Enrichit les données avec l'API Sirene (Insee)
    
    Nécessite une clé API Insee (gratuite sur https://portail-api.insee.fr/)
    
    Deux méthodes d'authentification possibles :
    1. OAuth2 avec Client ID + Client Certificate (PEM) - Recommandé
    2. Consumer Key/Secret - Ancien système
    
    Args:
        siret: Numéro SIRET (14 chiffres)
        siren_api_key: Consumer Key (ancien système)
        siren_api_secret: Consumer Secret (ancien système)
        siren_client_id: Client ID pour OAuth2 (recommandé)
        siren_client_certificate: Chemin vers le certificat PEM ou contenu du certificat pour OAuth2
    
    Returns:
        Dictionnaire avec les données enrichies ou erreur
    """
    if not siret or len(siret) != 14 or not siret.isdigit():
        return {
            "success": False,
            "error": "SIRET invalide (doit contenir 14 chiffres)",
            "siret": siret,
            "siren": siret[:9] if siret and len(siret) >= 9 else None
        }
    
    # Vérifier qu'au moins une méthode d'authentification est configurée
    has_oauth2 = siren_client_id and siren_client_certificate
    has_consumer = siren_api_key and siren_api_secret
    
    if not has_oauth2 and not has_consumer:
        return {
            "success": False,
            "error": "Clé API Sirene non configurée. Configurez soit SIRENE_CLIENT_ID + SIRENE_CLIENT_CERTIFICATE (OAuth2), soit SIRENE_API_KEY + SIRENE_API_SECRET (Consumer Key/Secret)",
            "siret": siret,
            "siren": siret[:9],
            "config_url": "https://portail-api.insee.fr/"
        }
    
    try:
        # Obtenir le token OAuth2
        access_token = None
        
        if has_oauth2:
            access_token = _get_oauth2_token_client_credentials(
                siren_client_id,
                siren_client_certificate
            )
            auth_method = "OAuth2 (Client ID + Certificate)"
        elif has_consumer:
            access_token = _get_oauth2_token_consumer_key(
                siren_api_key,
                siren_api_secret
            )
            auth_method = "OAuth2 (Consumer Key/Secret)"
        
        if not access_token:
            return {
                "success": False,
                "error": "Impossible d'obtenir le token OAuth2. Vérifiez vos identifiants API Sirene.",
                "siret": siret,
                "siren": siret[:9],
                "auth_method": auth_method
            }
        
        # Appeler l'API Sirene
        sirene_data = _call_sirene_api(siret, access_token)
        
        if not sirene_data:
            return {
                "success": False,
                "error": "SIRET non trouvé dans la base Sirene ou erreur API",
                "siret": siret,
                "siren": siret[:9]
            }
        
        # Parser la réponse
        parsed_data = _parse_sirene_response(sirene_data)
        
        if not parsed_data:
            return {
                "success": False,
                "error": "Erreur lors du parsing de la réponse API Sirene",
                "siret": siret,
                "siren": siret[:9]
            }
        
        return {
            "success": True,
            "siret": parsed_data.get("siret", siret),
            "siren": parsed_data.get("siren", siret[:9]),
            "raison_sociale": parsed_data.get("raison_sociale"),
            "adresse_complete": parsed_data.get("adresse_complete"),
            "code_postal": parsed_data.get("code_postal"),
            "ville": parsed_data.get("ville"),
            "activite_principale": parsed_data.get("activite_principale"),
            "forme_juridique": parsed_data.get("forme_juridique"),
            "statut": parsed_data.get("statut"),
            "date_creation": parsed_data.get("date_creation"),
            "date_cessation": parsed_data.get("date_cessation"),
            "tranche_effectifs": parsed_data.get("tranche_effectifs"),
            "source": parsed_data.get("source", "API Sirene (Insee)"),
            "auth_method": auth_method
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Erreur lors de l'enrichissement Sirene : {str(e)}",
            "siret": siret,
            "siren": siret[:9]
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


def extract_compliance_data(
    extracted_data: Dict, 
    ocr_text: str,
    siren_api_key: Optional[str] = None,
    siren_api_secret: Optional[str] = None,
    siren_client_id: Optional[str] = None,
    siren_client_certificate: Optional[str] = None
) -> Dict:
    """
    Extrait et vérifie toutes les données de conformité pour une facture française
    
    Retourne un dictionnaire complet avec :
    - Détection SIREN/SIRET
    - Détection TVA intracom
    - Vérification compliance FR
    - Validation TVA
    - Enrichissement (si configuré)
    
    Args:
        extracted_data: Données extraites de la facture
        ocr_text: Texte OCR complet
        siren_api_key: Consumer Key pour API Sirene (optionnel)
        siren_api_secret: Consumer Secret pour API Sirene (optionnel)
        siren_client_id: Client ID pour API Sirene OAuth2 (optionnel)
        siren_client_certificate: Certificat PEM pour API Sirene OAuth2 (optionnel)
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
        # Passer les identifiants API Sirene si disponibles
        enrichment = enrich_siren_siret(
            siren_siret["siret"],
            siren_api_key=siren_api_key,
            siren_api_secret=siren_api_secret,
            siren_client_id=siren_client_id,
            siren_client_certificate=siren_client_certificate
        )
        compliance_result["enrichment"]["siren_siret"] = enrichment
    
    # 6. Validation VIES (si TVA intracom trouvé)
    if vat_intracom:
        vies_result = validate_vies(vat_intracom)
        compliance_result["vat_intracom"]["validated"] = vies_result
        compliance_result["enrichment"]["vies"] = vies_result
    
    return compliance_result

