from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from typing import Optional, List, Dict
from config import settings
from pydantic import BaseModel
import pytesseract
from PIL import Image
import io
import re
import os
try:
    import fitz  # PyMuPDF
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    try:
        from pdf2image import convert_from_bytes
        PDF_SUPPORT = True
    except ImportError:
        PDF_SUPPORT = False

# Configurer le chemin Tesseract si nécessaire (pour certains environnements Docker)
# Essayer plusieurs chemins possibles
tesseract_paths = ['/usr/bin/tesseract', '/usr/local/bin/tesseract', 'tesseract']
for path in tesseract_paths:
    if os.path.exists(path) or path == 'tesseract':
        try:
            pytesseract.pytesseract.tesseract_cmd = path
            # Tester si ça fonctionne
            pytesseract.get_tesseract_version()
            break
        except:
            continue

app = FastAPI(
    title="OCR Facture API",
    description="API professionnelle pour l'extraction automatique de données de factures via OCR. Extrait le texte, les montants, dates, numéros de facture, lignes de facture (items) et autres informations structurées. Inclut des scores de confiance pour chaque donnée extraite.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ajouter le support d'authentification dans Swagger
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="OCR Facture API",
        version="1.0.0",
        description="API professionnelle pour l'extraction automatique de données de factures via OCR.",
        routes=app.routes,
    )
    # Ajouter le schéma de sécurité
    openapi_schema["components"]["securitySchemes"] = {
        "RapidAPIProxySecret": {
            "type": "apiKey",
            "in": "header",
            "name": "X-RapidAPI-Proxy-Secret",
            "description": "Secret pour l'authentification RapidAPI"
        }
    }
    # Appliquer la sécurité aux endpoints protégés
    for path, path_item in openapi_schema["paths"].items():
        if path not in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            for method in path_item:
                if method in ["post", "get", "put", "delete", "patch"]:
                    if "security" not in path_item[method]:
                        path_item[method]["security"] = [{"RapidAPIProxySecret": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware pour vérifier l'authentification RapidAPI
@app.middleware("http")
async def verify_rapidapi_auth(request: Request, call_next):
    # Skip auth pour les endpoints de documentation et health
    if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health", "/"]:
        response = await call_next(request)
        return response
    
    # En mode debug, pas d'authentification requise
    if settings.debug_mode:
        response = await call_next(request)
        return response
    
    # Vérifier la clé secrète RapidAPI
    rapidapi_secret = request.headers.get("X-RapidAPI-Proxy-Secret")
    if not rapidapi_secret or rapidapi_secret != settings.rapidapi_proxy_secret:
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "message": "Invalid or missing X-RapidAPI-Proxy-Secret header"}
        )
    
    response = await call_next(request)
    return response


class OCRResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None
    extracted_data: Optional[dict] = None
    confidence_scores: Optional[dict] = None


def process_pdf_multi_page(pdf_data: bytes, language: str) -> dict:
    """
    Traite un PDF multi-pages et fusionne les résultats
    """
    all_text = []
    all_data = []
    
    try:
        # Essayer PyMuPDF d'abord (plus rapide)
        if PDF_SUPPORT:
            try:
                import fitz
                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Augmenter la résolution
                    img_data = pix.tobytes("png")
                    image = Image.open(io.BytesIO(img_data))
                    
                    # OCR sur cette page
                    page_text = pytesseract.image_to_string(image, lang=language)
                    page_data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
                    
                    all_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    all_data.append(page_data)
                
                pdf_document.close()
                
                # Fusionner les textes
                merged_text = "\n\n".join(all_text)
                
                return {
                    "text": merged_text,
                    "data": all_data[0] if all_data else {},  # Prendre les données de la première page
                    "language": language,
                    "pages_processed": len(all_text)
                }
            except Exception as e:
                # Si PyMuPDF échoue, essayer pdf2image
                pass
        
        # Fallback sur pdf2image
        if PDF_SUPPORT:
            try:
                from pdf2image import convert_from_bytes
                images = convert_from_bytes(pdf_data, dpi=300)
                
                for page_num, image in enumerate(images):
                    # OCR sur cette page
                    page_text = pytesseract.image_to_string(image, lang=language)
                    page_data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
                    
                    all_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    all_data.append(page_data)
                
                # Fusionner les textes
                merged_text = "\n\n".join(all_text)
                
                return {
                    "text": merged_text,
                    "data": all_data[0] if all_data else {},
                    "language": language,
                    "pages_processed": len(all_text)
                }
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur lors du traitement PDF: {str(e)}. Assurez-vous que poppler est installé."
                )
        
        raise HTTPException(
            status_code=500,
            detail="Support PDF non disponible. Installez PyMuPDF ou pdf2image."
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement PDF: {str(e)}")


def perform_ocr(image_data: bytes, language: str = "fra", is_pdf: bool = False) -> dict:
    """
    Effectue l'OCR sur l'image utilisant pytesseract
    Supporte les PDFs multi-pages
    """
    try:
        # Vérifier que Tesseract est disponible
        try:
            pytesseract.get_tesseract_version()
        except Exception as tess_err:
            raise HTTPException(
                status_code=500, 
                detail=f"Tesseract OCR n'est pas disponible: {str(tess_err)}"
            )
        
        # Traiter les PDFs séparément
        if is_pdf:
            return process_pdf_multi_page(image_data, language)
        
        # Ouvrir l'image depuis les bytes
        image = Image.open(io.BytesIO(image_data))
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Mapping des codes langue
        lang_map = {
            "fra": "fra",
            "eng": "eng",
            "deu": "deu",
            "spa": "spa",
            "ita": "ita",
            "por": "por"
        }
        tesseract_lang = lang_map.get(language, "fra")
        
        # Vérifier que la langue est disponible
        try:
            available_langs = pytesseract.get_languages()
            if tesseract_lang not in available_langs:
                # Fallback sur eng si la langue demandée n'est pas disponible
                tesseract_lang = "eng" if "eng" in available_langs else available_langs[0] if available_langs else "fra"
        except:
            pass  # Si on ne peut pas vérifier, on continue quand même
        
        # Effectuer l'OCR
        text = pytesseract.image_to_string(image, lang=tesseract_lang)
        
        # Obtenir les données détaillées
        data = pytesseract.image_to_data(image, lang=tesseract_lang, output_type=pytesseract.Output.DICT)
        
        return {
            "text": text,
            "data": data,
            "language": tesseract_lang
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement OCR: {str(e)}")


def calculate_confidence(value, pattern_matches: int, context_quality: float = 1.0) -> float:
    """
    Calcule un score de confiance (0-1) pour une donnée extraite
    """
    if value is None:
        return 0.0
    
    # Base confidence selon le nombre de matches trouvés
    base_confidence = min(0.7 + (pattern_matches * 0.1), 0.95)
    
    # Ajuster selon la qualité du contexte
    confidence = base_confidence * context_quality
    
    # Bonus si la valeur semble valide
    if isinstance(value, (int, float)) and value > 0:
        confidence = min(confidence + 0.05, 1.0)
    elif isinstance(value, str) and len(value) > 2:
        confidence = min(confidence + 0.05, 1.0)
    
    return round(confidence, 2)


def extract_invoice_items(lines: List[str], text_lower: str) -> List[Dict]:
    """
    Extrait les lignes/articles de la facture
    """
    items = []
    
    # Patterns pour détecter les lignes de facture
    # Format typique: "Description [Qté] [Prix unitaire] [Total]"
    
    # Chercher la section des items (généralement entre "Description" et "Total")
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Détecter le début (header de tableau)
        if any(keyword in line_lower for keyword in ["description", "désignation", "article", "libellé", "item"]):
            if any(keyword in line_lower for keyword in ["prix", "montant", "total", "qté", "quantité"]):
                start_idx = i + 1
                break
    
    # Si pas de header trouvé, chercher après "Client" et avant "Total"
    if start_idx is None:
        for i, line in enumerate(lines):
            if "client" in line.lower() and ":" in line:
                start_idx = i + 5  # Après les infos client
                break
    
    # Trouver la fin (avant les totaux)
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in ["total", "sous-total", "montant total", "tva"]):
            if re.search(r'[\d,]+\.?\d*', line):  # Contient un nombre
                end_idx = i
                break
    
    # Si pas de fin trouvée, utiliser les 15 lignes après le début
    if start_idx is not None and end_idx is None:
        end_idx = min(start_idx + 15, len(lines))
    
    # Extraire les items dans cette section
    if start_idx is not None and end_idx is not None:
        for i in range(start_idx, end_idx):
            line = lines[i].strip()
            if not line or len(line) < 5:
                continue
            
            # Ignorer les lignes qui sont clairement des totaux ou headers
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ["total", "tva", "ht", "ttc", "description", "montant"]):
                if i == start_idx:  # Premier ligne peut être un header
                    continue
            
            # Chercher des patterns de ligne de facture
            # Format: "Description [nombre] [nombre] [nombre]"
            # Ou: "Description [nombre]€"
            
            # Extraire les nombres de la ligne
            numbers = re.findall(r'[\d,]+\.?\d*', line)
            
            if len(numbers) >= 1:
                # Essayer d'extraire description et montants
                # Pattern 1: "Description 500.00 €" (un seul nombre = total)
                # Pattern 2: "Description 1 500.00 500.00" (qté, prix unitaire, total)
                # Pattern 3: "Description 500.00" (total seulement)
                
                # Séparer description et nombres
                parts = re.split(r'[\d,]+\.?\d*', line)
                description = parts[0].strip() if parts else ""
                
                # Nettoyer la description
                description = re.sub(r'^[^\w]+', '', description)  # Enlever caractères spéciaux au début
                description = description.strip()
                
                if len(description) < 3:  # Description trop courte, prendre le début de la ligne
                    description = re.sub(r'[\d,]+\.?\d*.*$', '', line).strip()
                
                # Si description valide et au moins un nombre
                if len(description) >= 3 and len(numbers) >= 1:
                    item = {
                        "description": description,
                        "quantity": None,
                        "unit_price": None,
                        "total": None
                    }
                    
                    # Convertir les nombres
                    try:
                        if len(numbers) >= 3:
                            # Format: Qté Prix_unitaire Total
                            item["quantity"] = float(numbers[0].replace(',', '.'))
                            item["unit_price"] = float(numbers[1].replace(',', '.'))
                            item["total"] = float(numbers[2].replace(',', '.'))
                        elif len(numbers) >= 2:
                            # Format: Prix_unitaire Total (ou Qté Total)
                            # Essayer de deviner lequel est lequel
                            val1 = float(numbers[0].replace(',', '.'))
                            val2 = float(numbers[1].replace(',', '.'))
                            
                            # Si le premier est petit (< 100), c'est probablement une quantité
                            if val1 < 100 and val1 == int(val1):
                                item["quantity"] = val1
                                item["total"] = val2
                                if val1 > 0:
                                    item["unit_price"] = round(val2 / val1, 2)
                            else:
                                # Sinon, c'est prix unitaire et total
                                item["unit_price"] = val1
                                item["total"] = val2
                                item["quantity"] = 1.0
                        else:
                            # Un seul nombre = total
                            item["total"] = float(numbers[0].replace(',', '.'))
                            item["quantity"] = 1.0
                    except ValueError:
                        continue
                    
                    # Vérifier que l'item est valide
                    if item["description"] and (item["total"] or item["unit_price"]):
                        items.append(item)
    
    return items


def extract_invoice_data(ocr_result: dict) -> tuple[dict, dict]:
    """
    Extrait les données structurées de la facture depuis le résultat OCR
    Retourne (extracted_data, confidence_scores)
    """
    extracted = {
        "text": "",
        "lines": [],
        "total": None,
        "total_ht": None,
        "total_ttc": None,
        "tva": None,
        "date": None,
        "invoice_number": None,
        "vendor": None,
        "client": None,
        "items": [],
        "currency": "EUR"
    }
    
    confidence_scores = {
        "total": 0.0,
        "total_ht": 0.0,
        "total_ttc": 0.0,
        "tva": 0.0,
        "date": 0.0,
        "invoice_number": 0.0,
        "vendor": 0.0,
        "client": 0.0,
        "items": 0.0
    }
    
    parsed_text = ocr_result.get("text", "")
    extracted["text"] = parsed_text
    
    # Extraire les lignes de texte
    lines = [line.strip() for line in parsed_text.split("\n") if line.strip()]
    extracted["lines"] = lines
    
    if not parsed_text:
        return extracted, confidence_scores
    
    text_lower = parsed_text.lower()
    
    # EXTRACTION DES ITEMS (lignes de facture)
    items = extract_invoice_items(lines, text_lower)
    extracted["items"] = items
    confidence_scores["items"] = calculate_confidence(
        items if items else None,
        len(items),
        0.9 if len(items) > 0 else 0.0
    )
    
    # Recherche du total avec scoring
    total_patterns = [
        r'total\s*(?:ttc|t\.t\.c\.)?\s*[:=]?\s*([\d\s,]+\.?\d*)\s*([€$£]|eur|usd|gbp)?',
        r'montant\s*total\s*[:=]?\s*([\d\s,]+\.?\d*)\s*([€$£]|eur|usd|gbp)?',
        r'total\s*[:=]?\s*([\d\s,]+\.?\d*)\s*([€$£]|eur|usd|gbp)?'
    ]
    
    total_matches = 0
    for pattern in total_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                extracted["total"] = float(amount_str)
                total_matches += 1
                if match.lastindex >= 2 and match.group(2):
                    currency_map = {"€": "EUR", "$": "USD", "£": "GBP", "eur": "EUR", "usd": "USD", "gbp": "GBP"}
                    extracted["currency"] = currency_map.get(match.group(2).lower(), "EUR")
                break
            except:
                pass
    
    confidence_scores["total"] = calculate_confidence(extracted["total"], total_matches)
    
    # Recherche du total HT avec scoring
    ht_patterns = [
        r'total\s*ht\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'montant\s*ht\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'ht\s*[:=]?\s*([\d\s,]+\.?\d*)'
    ]
    ht_matches = 0
    for pattern in ht_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                extracted["total_ht"] = float(amount_str)
                ht_matches += 1
                break
            except:
                pass
    confidence_scores["total_ht"] = calculate_confidence(extracted["total_ht"], ht_matches)
    
    # Recherche du total TTC avec scoring
    ttc_patterns = [
        r'total\s*ttc\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'montant\s*ttc\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'ttc\s*[:=]?\s*([\d\s,]+\.?\d*)'
    ]
    ttc_matches = 0
    for pattern in ttc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                extracted["total_ttc"] = float(amount_str)
                ttc_matches += 1
                break
            except:
                pass
    confidence_scores["total_ttc"] = calculate_confidence(extracted["total_ttc"], ttc_matches)
    
    # Calcul de la TVA si HT et TTC disponibles
    if extracted["total_ht"] and extracted["total_ttc"]:
        extracted["tva"] = extracted["total_ttc"] - extracted["total_ht"]
        # Score de confiance pour TVA = moyenne des scores HT et TTC
        confidence_scores["tva"] = round((confidence_scores["total_ht"] + confidence_scores["total_ttc"]) / 2, 2)
    
    # Recherche de la date avec scoring
    date_patterns = [
        r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
        r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b',
        r'\b(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|mai|jun|jul|aoû|sep|oct|nov|déc)\s+\d{4})\b',
        r'\b(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4})\b'
    ]
    date_matches = 0
    for pattern in date_patterns:
        match = re.search(pattern, parsed_text, re.IGNORECASE)
        if match:
            extracted["date"] = match.group(1)
            date_matches += 1
            break
    confidence_scores["date"] = calculate_confidence(extracted["date"], date_matches, 0.95)
    
    # Recherche améliorée du numéro de facture avec scoring
    invoice_patterns = [
        r'facture\s*n°\s*[:=]?\s*([A-Z0-9\-]+)',
        r'facture\s*(?:n°|no|number)?\s*[:=]?\s*([A-Z0-9\-]+)',
        r'invoice\s*(?:#|n°|no|number)?\s*[:=]?\s*([A-Z0-9\-]+)',
        r'n°\s*[:=]?\s*([A-Z0-9\-]+)',
        r'ref[ée]rence\s*[:=]?\s*([A-Z0-9\-]+)',
        r'(?:facture|invoice)\s*(?:numéro|number|no|n°)?\s*[:=]?\s*([A-Z]{2,4}[-]?\d{4}[-]?\d{2,4})',
        r'(?:ref|réf)\.?\s*[:=]?\s*([A-Z0-9\-]{5,20})'
    ]
    
    invoice_matches = 0
    # Chercher dans les premières lignes (où se trouve généralement le numéro)
    search_lines = lines[:15] + [parsed_text]
    
    for search_text in search_lines:
        search_lower = search_text.lower() if isinstance(search_text, str) else ""
        for pattern in invoice_patterns:
            match = re.search(pattern, search_lower if search_lower else search_text, re.IGNORECASE)
            if match:
                invoice_num = match.group(1).upper().strip()
                # Vérifier que c'est un numéro valide (au moins 3 caractères)
                if len(invoice_num) >= 3 and len(invoice_num) <= 30:
                    extracted["invoice_number"] = invoice_num
                    invoice_matches += 1
                    break
        if extracted["invoice_number"]:
            break
    
    # Si pas trouvé, chercher directement les patterns de numéros dans toutes les lignes
    if not extracted["invoice_number"]:
        # Patterns pour numéros de facture communs
        direct_patterns = [
            r'\b([A-Z]{2,4}[-]?\d{4}[-]?\d{2,4})\b',  # FAC-2024-001
            r'\b([A-Z]{2,}[0-9]{4,})\b',  # FAC2024001
            r'\b(INV[-]?[0-9]{4,})\b',  # INV-2024
            r'\b(FA[-]?[0-9]{4,})\b',  # FA-2024
        ]
        for line in lines[:20]:  # Chercher dans les 20 premières lignes
            for pattern in direct_patterns:
                match = re.search(pattern, line.upper())
                if match:
                    invoice_num = match.group(1)
                    if len(invoice_num) >= 3:
                        extracted["invoice_number"] = invoice_num
                        invoice_matches += 1
                        break
            if extracted["invoice_number"]:
                break
    
    confidence_scores["invoice_number"] = calculate_confidence(
        extracted["invoice_number"],
        invoice_matches,
        0.9 if invoice_matches > 0 else 0.0
    )
    
    # Recherche du vendeur/fournisseur (généralement après "Vendeur:")
    vendor_found = False
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Si on trouve "Vendeur:" ou "Vendor:", prendre la ligne suivante
        if "vendeur" in line_lower or "vendor" in line_lower:
            # Prendre les lignes suivantes jusqu'à trouver une société
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip()
                # Ignorer les lignes vides ou trop courtes
                if len(next_line) > 5 and len(next_line) < 100:
                    # Ignorer les lignes qui sont des adresses (contiennent des chiffres et "rue", "avenue", etc.)
                    if not re.search(r'\d+\s+(rue|avenue|boulevard|street|road)', next_line.lower()):
                        vendor_keywords = ["sarl", "ltd", "inc", "sas", "sa", "eurl", "société", "company"]
                        if any(keyword in next_line.lower() for keyword in vendor_keywords) or j == i+1:
                            extracted["vendor"] = next_line
                            vendor_found = True
                            break
            if vendor_found:
                break
    
    # Fallback: chercher dans les premières lignes
    if not vendor_found:
        vendor_keywords = ["sarl", "ltd", "inc", "sas", "sa", "eurl", "société"]
        for i, line in enumerate(lines[:10]):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in vendor_keywords):
                if len(line) > 5 and len(line) < 100 and "facture" not in line_lower:
                    extracted["vendor"] = line.strip()
                    break
    
    # Recherche du client (généralement après "Client:" ou "Customer:")
    client_found = False
    for i, line in enumerate(lines):
        line_lower = line.lower()
        # Si on trouve "Client:" ou "Customer:", prendre la ligne suivante
        if ("client" in line_lower or "customer" in line_lower) and ":" in line:
            # Prendre la ligne suivante (nom du client)
            if i+1 < len(lines):
                next_line = lines[i+1].strip()
                # Ignorer les lignes vides ou trop courtes, ou qui sont des adresses
                if len(next_line) > 3 and len(next_line) < 100:
                    if not re.search(r'\d+\s+(rue|avenue|boulevard|street|road)', next_line.lower()):
                        # Si la ligne suivante ne contient pas de chiffres (pas une adresse)
                        if not re.search(r'^\d+', next_line):
                            extracted["client"] = next_line.rstrip('.')
                            client_found = True
                            break
    
    # Fallback: chercher "Client ABC" ou similaire dans la même ligne
    if not client_found:
        for line in lines:
            match = re.search(r'client\s+([A-Z][A-Za-z\s]+)', line, re.IGNORECASE)
            if match:
                client_name = match.group(1).strip()
                if len(client_name) > 2 and len(client_name) < 50:
                    extracted["client"] = client_name.rstrip('.')
                    client_found = True
                    break
    
    # Calculer les scores de confiance pour vendeur et client
    confidence_scores["vendor"] = calculate_confidence(
        extracted["vendor"],
        1 if vendor_found else 0,
        0.85 if vendor_found else 0.0
    )
    confidence_scores["client"] = calculate_confidence(
        extracted["client"],
        1 if client_found else 0,
        0.85 if client_found else 0.0
    )
    
    return extracted, confidence_scores


@app.get("/")
async def root():
    return {
        "message": "OCR Facture API",
        "version": "1.1.0",
        "status": "running",
        "features": [
            "OCR extraction",
            "Invoice items extraction",
            "Confidence scoring",
            "Multi-page PDF support",
            "Multi-language support"
        ]
    }


@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API et les dépendances"""
    health_status = {
        "status": "healthy",
        "debug_mode": settings.debug_mode,
        "api_version": "1.1.0"
    }
    
    # Vérifier si Tesseract est disponible
    try:
        import subprocess
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            health_status["tesseract"] = "available"
            # Extraire la version
            version_line = result.stdout.split('\n')[0] if result.stdout else "unknown"
            health_status["tesseract_version"] = version_line
        else:
            health_status["tesseract"] = "error"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["tesseract"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status


@app.post("/ocr/upload", response_model=OCRResponse)
async def upload_and_ocr(
    file: UploadFile = File(...),
    language: str = Form("fra")
):
    """
    Upload une image de facture et extrait automatiquement les données structurées.
    
    **Paramètres:**
    - `file`: Fichier image (JPEG, PNG, PDF)
    - `language`: Code langue pour OCR (fra, eng, deu, spa, ita, por). Défaut: fra
    
    **Retourne:**
    - Texte extrait complet
    - Données structurées (total, date, numéro de facture, vendeur, items/lignes de facture, etc.)
    - Scores de confiance pour chaque donnée extraite
    - Support PDF multi-pages (toutes les pages sont traitées et fusionnées)
    """
    # Vérifier le type de fichier
    if not file.content_type or not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image (jpeg, png) ou un PDF"
        )
    
    try:
        # Lire le contenu du fichier
        file_data = await file.read()
        
        # Détecter si c'est un PDF
        is_pdf = file.content_type == "application/pdf" or (file.filename and file.filename.lower().endswith('.pdf'))
        
        # Effectuer l'OCR
        ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        
        # Extraire les données structurées avec scores de confiance
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        
        # Préparer les données de réponse
        response_data = {
            "text": ocr_result["text"],
            "language": ocr_result["language"]
        }
        if "pages_processed" in ocr_result:
            response_data["pages_processed"] = ocr_result["pages_processed"]
        
        return OCRResponse(
            success=True,
            data=response_data,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return OCRResponse(
            success=False,
            error=str(e)
        )


@app.post("/ocr/base64")
async def ocr_from_base64(
    image_base64: str = Form(...),
    language: str = Form("fra")
):
    """
    Traite une image encodée en base64 et extrait les données de facture.
    
    **Paramètres:**
    - `image_base64`: Image encodée en base64 (avec ou sans préfixe data:image)
    - `language`: Code langue pour OCR (fra, eng, deu, spa, ita, por). Défaut: fra
    """
    try:
        # Décoder l'image base64
        is_pdf = False
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]
        elif image_base64.startswith("data:application/pdf"):
            is_pdf = True
            image_base64 = image_base64.split(",")[1]
        
        file_data = base64.b64decode(image_base64)
        
        # Effectuer l'OCR
        ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        
        # Extraire les données structurées avec scores de confiance
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        
        # Préparer les données de réponse
        response_data = {
            "text": ocr_result["text"],
            "language": ocr_result["language"]
        }
        if "pages_processed" in ocr_result:
            response_data["pages_processed"] = ocr_result["pages_processed"]
        
        return OCRResponse(
            success=True,
            data=response_data,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores
        )
    
    except Exception as e:
        return OCRResponse(
            success=False,
            error=str(e)
        )


@app.get("/languages")
async def get_supported_languages():
    """
    Retourne la liste des langues supportées pour l'OCR
    """
    return {
        "languages": [
            {"code": "fra", "name": "Français"},
            {"code": "eng", "name": "English"},
            {"code": "deu", "name": "Deutsch"},
            {"code": "spa", "name": "Español"},
            {"code": "ita", "name": "Italiano"},
            {"code": "por", "name": "Português"}
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

