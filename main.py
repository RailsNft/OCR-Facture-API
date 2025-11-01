from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Body, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import base64
from typing import Optional, List, Dict, Any
from config import settings
from pydantic import BaseModel, Field
import pytesseract
from PIL import Image
import io
import re
import os
import hashlib
import json
from datetime import datetime, timedelta
from compliance import extract_compliance_data, detect_siren_siret, detect_vat_intracom, validate_vies, enrich_siren_siret, validate_french_vat
from facturx import generate_facturx_xml, parse_facturx_from_pdf, parse_facturx_xml, validate_facturx_xml
from rate_limiting import rate_limit_middleware
from monitoring import monitoring_middleware, get_metrics, log_cache_hit, log_cache_miss
from image_preprocessing import preprocess_image, should_preprocess
from cache_redis import (
    init_cache_backend,
    get_cached,
    set_cached,
    get_cache_info,
    get_cache_backend
)
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
    description="API professionnelle pour l'extraction automatique de données de factures via OCR. Extrait le texte, les montants, dates, numéros de facture, lignes de facture (items) et autres informations structurées. Inclut des scores de confiance pour chaque donnée extraite. Support Factur-X (EN16931) et compliance française.",
    version="2.0.0",
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

# Créer le router pour la version v1
v1_router = APIRouter(prefix="/v1", tags=["v1"])

# Initialiser le cache backend (Redis ou mémoire)
init_cache_backend(
    redis_url=settings.redis_url,
    redis_db=settings.redis_db,
    force_memory=settings.force_memory_cache
)

# Initialiser Redis pour rate limiting si disponible
if settings.redis_url and not settings.force_memory_cache:
    from rate_limiting import init_rate_limit_redis
    init_rate_limit_redis(settings.redis_url, settings.redis_db)

CACHE_TTL_HOURS = 24  # Cache valide 24h
IDEMPOTENCY_TTL_HOURS = 24  # Les clés idempotence sont valides 24h

# Cache mémoire de fallback pour idempotence (peut être migré vers Redis aussi)
idempotency_cache: Dict[str, Dict[str, Any]] = {}


# Exceptions personnalisées pour codes d'erreur spécifiques
class ComplianceError(HTTPException):
    """Erreur 422 - Erreur de conformité ou validation"""
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class DuplicateError(HTTPException):
    """Erreur 409 - Doublon détecté (idempotence)"""
    def __init__(self, detail: str, existing_result: Optional[Dict] = None):
        super().__init__(status_code=409, detail=detail)
        self.existing_result = existing_result


class TimeoutError(HTTPException):
    """Erreur 504 - Timeout lors du traitement OCR"""
    def __init__(self, detail: str = "Le traitement OCR a dépassé le délai maximum"):
        super().__init__(status_code=504, detail=detail)


class EnrichmentError(HTTPException):
    """Erreur 424 - Échec de l'enrichissement (ex: API Sirene)"""
    def __init__(self, detail: str):
        super().__init__(status_code=424, detail=detail)


def get_file_hash(file_data: bytes) -> str:
    """Génère un hash SHA256 du fichier pour le cache"""
    return hashlib.sha256(file_data).hexdigest()


def get_cached_result(file_hash: str) -> Optional[Dict]:
    """Récupère un résultat depuis le cache (Redis ou mémoire)"""
    cache_key = f"ocr_result:{file_hash}"
    cached_data = get_cached(cache_key)
    
    if cached_data:
        # Vérifier si le cache n'est pas expiré (si backend mémoire)
        cache_time = cached_data.get("timestamp")
        if cache_time:
            cache_dt = datetime.fromisoformat(cache_time)
            if datetime.now() - cache_dt < timedelta(hours=CACHE_TTL_HOURS):
                return cached_data.get("result")
            else:
                # Cache expiré (pour mémoire backend)
                from cache_redis import delete_cached
                delete_cached(cache_key)
        else:
            # Redis gère l'expiration automatiquement
            return cached_data.get("result")
    
    return None


def set_cached_result(file_hash: str, result: Dict):
    """Stocke un résultat dans le cache (Redis ou mémoire)"""
    cache_key = f"ocr_result:{file_hash}"
    cache_data = {
        "result": result,
        "timestamp": datetime.now().isoformat()
    }
    set_cached(cache_key, cache_data, ttl_hours=CACHE_TTL_HOURS)


def check_idempotency(request: Request) -> Optional[Dict]:
    """Vérifie si une Idempotency-Key existe déjà dans le cache"""
    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key and idempotency_key in idempotency_cache:
        cached_response = idempotency_cache[idempotency_key]
        cache_time = cached_response.get("timestamp")
        if cache_time:
            cache_dt = datetime.fromisoformat(cache_time)
            if datetime.now() - cache_dt < timedelta(hours=IDEMPOTENCY_TTL_HOURS):
                return cached_response.get("result")
            else:
                # Cache expiré, le supprimer
                del idempotency_cache[idempotency_key]
    return None


def store_idempotency(request: Request, result: Dict):
    """Stocke un résultat dans le cache d'idempotence"""
    idempotency_key = request.headers.get("Idempotency-Key")
    if idempotency_key:
        idempotency_cache[idempotency_key] = {
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        # Limiter la taille du cache
        if len(idempotency_cache) > 1000:
            sorted_items = sorted(idempotency_cache.items(), key=lambda x: x[1].get("timestamp", ""))
            for key, _ in sorted_items[:100]:
                del idempotency_cache[key]


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monitoring middleware (doit être avant rate limiting pour mesurer tout)
app.middleware("http")(monitoring_middleware)

# Rate limiting middleware
app.middleware("http")(rate_limit_middleware)


# Middleware pour vérifier l'authentification RapidAPI
@app.middleware("http")
async def verify_rapidapi_auth(request: Request, call_next):
    # Skip auth pour les endpoints de documentation, health, demo et assets statiques
    public_paths = ["/docs", "/redoc", "/openapi.json", "/health", "/"]
    if (request.url.path in public_paths 
        or request.url.path.startswith("/demo")
        or request.url.path.startswith("/assets/")
        or request.url.path.startswith("/v1/languages")):
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
    cached: Optional[bool] = False  # Indique si le résultat vient du cache
    compliance: Optional[dict] = None  # Données de conformité FR (si demandé)


class BatchOCRRequest(BaseModel):
    files: List[str] = Field(..., description="Liste d'images encodées en base64")
    language: str = Field(default="fra", description="Code langue pour OCR")


class BatchOCRResponse(BaseModel):
    success: bool
    results: List[OCRResponse] = []
    total_processed: int = 0
    total_cached: int = 0


class WebhookPayload(BaseModel):
    invoice_id: str
    invoice_data: dict
    timestamp: str
    source: str = "ocr_facture_api"


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
        
        # Préprocessing d'image amélioré (si recommandé)
        if should_preprocess(image):
            try:
                image = preprocess_image(
                    image,
                    enhance_contrast=True,
                    denoise=True,
                    deskew=True,
                    upscale=False
                )
            except Exception as preprocess_error:
                # Si le preprocessing échoue, continuer avec l'image originale
                pass
        
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


def detect_structured_tables(lines: List[str], ocr_data: Optional[Dict] = None) -> List[Dict]:
    """
    Détecte et extrait les tableaux structurés de la facture
    Retourne une liste de tableaux avec leurs colonnes détectées automatiquement
    """
    tables = []
    
    # Chercher les sections qui ressemblent à des tableaux
    # Un tableau commence généralement par un header avec plusieurs colonnes
    # et contient plusieurs lignes avec des données alignées
    
    # Patterns pour détecter les headers de tableaux
    header_keywords = [
        ["description", "désignation", "article", "libellé", "item"],
        ["quantité", "qté", "qty", "quant"],
        ["prix", "pu", "unit", "unitaire"],
        ["montant", "total", "amount", "somme"]
    ]
    
    # Chercher les lignes qui contiennent plusieurs colonnes (séparées par espaces multiples ou |
    table_start = None
    table_end = None
    
    for i, line in enumerate(lines):
        # Détecter si c'est un header de tableau (contient plusieurs mots-clés)
        line_lower = line.lower()
        header_matches = sum(1 for keyword_group in header_keywords 
                            if any(kw in line_lower for kw in keyword_group))
        
        # Si on trouve au moins 2 groupes de mots-clés, c'est probablement un header
        if header_matches >= 2:
            table_start = i
            # Chercher la fin du tableau (ligne vide ou ligne avec "Total")
            for j in range(i + 1, min(i + 30, len(lines))):
                next_line = lines[j].strip()
                if not next_line or len(next_line) < 3:
                    table_end = j
                    break
                # Si on trouve "Total" avec un nombre, c'est la fin
                if re.search(r'total.*[\d,]+\.?\d*', next_line.lower()):
                    table_end = j
                    break
            else:
                table_end = min(i + 30, len(lines))
            
            if table_start is not None and table_end is not None:
                # Extraire le tableau
                table_lines = lines[table_start:table_end]
                
                # Détecter les colonnes (séparateurs: espaces multiples, |, ou tabulations)
                if table_lines:
                    header_line = table_lines[0]
                    
                    # Détecter les colonnes en cherchant les séparateurs
                    # Essayer avec |
                    if '|' in header_line:
                        columns = [col.strip() for col in header_line.split('|')]
                    # Essayer avec espaces multiples
                    elif re.search(r'\s{2,}', header_line):
                        columns = re.split(r'\s{2,}', header_line)
                    else:
                        # Détecter colonnes par position approximative
                        # Pour simplification, on prend les premiers mots comme colonnes
                        columns = header_line.split()[:5]  # Max 5 colonnes
                    
                    # Extraire les lignes de données
                    rows = []
                    for data_line in table_lines[1:]:
                        if not data_line.strip() or len(data_line.strip()) < 5:
                            continue
                        
                        # Parser la ligne selon le même séparateur que le header
                        if '|' in data_line:
                            row_data = [col.strip() for col in data_line.split('|')]
                        elif re.search(r'\s{2,}', data_line):
                            row_data = re.split(r'\s{2,}', data_line)
                        else:
                            row_data = data_line.split()[:len(columns)]
                        
                        # Créer un objet ligne avec les colonnes comme clés
                        row_dict = {}
                        for idx, col_name in enumerate(columns):
                            if idx < len(row_data):
                                row_dict[col_name.strip()] = row_data[idx].strip()
                        
                        if row_dict:
                            rows.append(row_dict)
                    
                    if rows:
                        tables.append({
                            "header": columns,
                            "rows": rows,
                            "row_count": len(rows)
                        })
                
                table_start = None
                table_end = None
    
    return tables


def extract_banking_info(text: str, lines: List[str]) -> Dict:
    """
    Extrait les coordonnées bancaires (IBAN, SWIFT/BIC, RIB)
    """
    banking_info = {
        "iban": None,
        "swift": None,
        "bic": None,
        "rib": None,
        "account_number": None,
        "bank_name": None
    }
    
    text_upper = text.upper()
    
    # Pattern IBAN (format standard: 2 lettres + 2 chiffres + jusqu'à 30 caractères alphanumériques)
    iban_patterns = [
        r'\b([A-Z]{2}\d{2}[A-Z0-9]{4,30})\b',  # IBAN standard
        r'IBAN\s*[:=]?\s*([A-Z]{2}\d{2}[A-Z0-9\s]{4,30})',  # IBAN: FR76...
        r'IBAN\s*[:=]?\s*([A-Z0-9\s]{15,34})'  # IBAN sans préfixe
    ]
    
    for pattern in iban_patterns:
        match = re.search(pattern, text_upper.replace(' ', ''))
        if match:
            iban = match.group(1).replace(' ', '').replace('-', '')
            # Valider la longueur IBAN (15-34 caractères)
            if 15 <= len(iban) <= 34:
                banking_info["iban"] = iban
                break
    
    # Pattern SWIFT/BIC (8 ou 11 caractères: 4 lettres + 2 lettres + 2 caractères + 3 optionnels)
    swift_patterns = [
        r'\b([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?)\b',  # SWIFT/BIC standard
        r'SWIFT\s*[:=]?\s*([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?)',  # SWIFT: ABCD...
        r'BIC\s*[:=]?\s*([A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?)'  # BIC: ABCD...
    ]
    
    for pattern in swift_patterns:
        match = re.search(pattern, text_upper)
        if match:
            swift = match.group(1)
            # Valider la longueur SWIFT (8 ou 11 caractères)
            if len(swift) == 8 or len(swift) == 11:
                banking_info["swift"] = swift
                banking_info["bic"] = swift  # BIC et SWIFT sont synonymes
                break
    
    # Pattern RIB français (23 chiffres: 5+5+11+2)
    rib_patterns = [
        r'\b(\d{5}\s?\d{5}\s?[A-Z0-9]{11}\s?\d{2})\b',  # RIB avec espaces
        r'RIB\s*[:=]?\s*(\d{5}\s?\d{5}\s?[A-Z0-9]{11}\s?\d{2})',  # RIB: 12345...
        r'\b(\d{23})\b'  # RIB sans espaces (23 chiffres consécutifs)
    ]
    
    for pattern in rib_patterns:
        match = re.search(pattern, text_upper.replace(' ', ''))
        if match:
            rib = match.group(1).replace(' ', '')
            if len(rib) == 23:
                banking_info["rib"] = rib
                break
    
    # Pattern numéro de compte (généralement long, avec des espaces ou tirets)
    account_patterns = [
        r'Compte\s*[:=]?\s*([\d\s\-]{10,20})',  # Compte: 1234 5678 9012
        r'Account\s*[:=]?\s*([\d\s\-]{10,20})',  # Account: 1234 5678 9012
        r'N°\s*Compte\s*[:=]?\s*([\d\s\-]{10,20})'  # N° Compte: 1234 5678 9012
    ]
    
    for pattern in account_patterns:
        match = re.search(pattern, text_upper)
        if match:
            account = match.group(1).replace(' ', '').replace('-', '')
            if len(account) >= 10:
                banking_info["account_number"] = account
                break
    
    # Chercher le nom de la banque (près des coordonnées bancaires)
    bank_keywords = ["banque", "bank", "banking", "bancaire"]
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in bank_keywords):
            # Prendre le nom de la banque (généralement avant le mot-clé ou après)
            if i > 0:
                prev_line = lines[i-1].strip()
                if len(prev_line) > 3 and len(prev_line) < 50:
                    banking_info["bank_name"] = prev_line
            elif i < len(lines) - 1:
                next_line = lines[i+1].strip()
                if len(next_line) > 3 and len(next_line) < 50:
                    banking_info["bank_name"] = next_line
            break
    
    return banking_info


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
        "currency": "EUR",
        "tables": [],  # Tableaux structurés détectés
        "banking_info": {}  # Coordonnées bancaires
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
        "items": 0.0,
        "tables": 0.0,
        "banking_info": 0.0
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
    
    # EXTRACTION DES TABLEAUX STRUCTURÉS
    tables = detect_structured_tables(lines, ocr_result.get("data"))
    extracted["tables"] = tables
    confidence_scores["tables"] = calculate_confidence(
        tables if tables else None,
        len(tables),
        0.85 if len(tables) > 0 else 0.0
    )
    
    # EXTRACTION DES COORDONNÉES BANCAIRES
    banking_info = extract_banking_info(parsed_text, lines)
    extracted["banking_info"] = banking_info
    
    # Calculer le score de confiance pour les infos bancaires
    banking_fields_found = sum(1 for v in banking_info.values() if v is not None)
    confidence_scores["banking_info"] = calculate_confidence(
        banking_info if banking_fields_found > 0 else None,
        banking_fields_found,
        0.9 if banking_fields_found > 0 else 0.0
    )
    
    return extracted, confidence_scores


@app.get("/")
async def root():
    return {
        "message": "OCR Facture API",
        "version": "2.0.0",
        "status": "running",
        "features": [
            "OCR extraction",
            "Invoice items extraction",
            "Confidence scoring",
            "Multi-page PDF support",
            "Multi-language support",
            "Structured table detection",
            "Banking info extraction (IBAN, SWIFT, RIB)",
            "Batch processing",
            "Result caching",
            "Webhook integrations (Zapier, Make, Salesforce)",
            "🆕 French compliance check (mentions légales, TVA validation)",
            "🆕 SIREN/SIRET detection and enrichment",
            "🆕 VIES validation (TVA intracom)",
            "🆕 Factur-X XML generation (EN16931)",
            "🆕 Factur-X parser (extract from PDF/A-3)",
            "🆕 Factur-X validator (XSD + business rules)"
        ]
    }


@app.get("/health")
async def health_check():
    """Vérifie l'état de santé de l'API et les dépendances"""
    # Informations sur le cache
    cache_info = get_cache_info()
    
    health_status = {
        "status": "healthy",
        "debug_mode": settings.debug_mode,
        "api_version": "2.0.0",
        "cache": cache_info
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


# Version originale (sans /v1/) - À déprécier progressivement
@app.post("/ocr/upload", response_model=OCRResponse)
async def upload_and_ocr(
    file: UploadFile = File(...),
    language: str = Form("fra"),
    check_compliance: bool = Form(False),
    request: Request = None
):
    """
    Upload une image de facture et extrait automatiquement les données structurées.
    
    **⚠️ DÉPRÉCIÉ : Utilisez /v1/ocr/upload à la place**
    
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
        
        # Vérifier le cache
        file_hash = get_file_hash(file_data)
        cached_result = get_cached_result(file_hash)
        
        if cached_result:
            # Retourner le résultat depuis le cache
            return OCRResponse(
                success=True,
                data=cached_result.get("data"),
                extracted_data=cached_result.get("extracted_data"),
                confidence_scores=cached_result.get("confidence_scores"),
                cached=True
            )
        
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
        
        # Stocker dans le cache
        cache_data = {
            "data": response_data,
            "extracted_data": extracted_data,
            "confidence_scores": confidence_scores
        }
        set_cached_result(file_hash, cache_data)
        
        return OCRResponse(
            success=True,
            data=response_data,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores,
            cached=False
        )
    
    except HTTPException:
        raise
    except Exception as e:
        return OCRResponse(
            success=False,
            error=str(e)
        )


# Version v1 avec idempotence et codes d'erreur spécifiques
@v1_router.post("/ocr/upload", response_model=OCRResponse)
async def upload_and_ocr_v1(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form("fra"),
    check_compliance: bool = Form(False)
):
    """
    Upload une image de facture et extrait automatiquement les données structurées.
    
    **Version v1** : Support Idempotency-Key et codes d'erreur spécifiques
    
    **Headers optionnels:**
    - `Idempotency-Key`: Clé unique pour éviter les doublons (UUID recommandé)
    
    **Paramètres:**
    - `file`: Fichier image (JPEG, PNG, PDF)
    - `language`: Code langue pour OCR (fra, eng, deu, spa, ita, por). Défaut: fra
    - `check_compliance`: Activer validation conformité FR (bool). Défaut: false
    
    **Codes d'erreur:**
    - 400 : Fichier invalide
    - 409 : Doublon détecté (Idempotency-Key)
    - 422 : Erreur de conformité
    - 504 : Timeout OCR
    """
    # Vérifier l'idempotence
    idempotent_result = check_idempotency(request)
    if idempotent_result:
        raise DuplicateError(
            detail="Une requête identique a déjà été traitée avec cette Idempotency-Key",
            existing_result=idempotent_result
        )
    
    # Vérifier le type de fichier
    if not file.content_type or not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image (jpeg, png) ou un PDF"
        )
    
    try:
        # Lire le contenu du fichier
        file_data = await file.read()
        
        # Vérifier le cache
        file_hash = get_file_hash(file_data)
        cached_result = get_cached_result(file_hash)
        
        if cached_result:
            log_cache_hit("/v1/ocr/upload")
            result = OCRResponse(
                success=True,
                data=cached_result.get("data"),
                extracted_data=cached_result.get("extracted_data"),
                confidence_scores=cached_result.get("confidence_scores"),
                cached=True
            )
            # Stocker pour idempotence
            store_idempotency(request, result.dict())
            return result
        
        # Détecter si c'est un PDF
        is_pdf = file.content_type == "application/pdf" or (file.filename and file.filename.lower().endswith('.pdf'))
        
        # Effectuer l'OCR avec timeout
        try:
            ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        except Exception as ocr_error:
            if "timeout" in str(ocr_error).lower() or "timed out" in str(ocr_error).lower():
                raise TimeoutError("Le traitement OCR a dépassé le délai maximum (30 secondes)")
            raise
        
        # Extraire les données structurées avec scores de confiance
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        
        # Validation compliance si demandée
        compliance_data = None
        if check_compliance:
            try:
                compliance_data = extract_compliance_data(
                    extracted_data,
                    ocr_result["text"],
                    siren_api_key=settings.sirene_api_key,
                    siren_api_secret=settings.sirene_api_secret,
                    siren_client_id=settings.sirene_client_id,
                    siren_client_certificate=settings.sirene_client_certificate
                )
                if not compliance_data.get("compliance_check", {}).get("compliant", True):
                    # Erreur 422 pour non-conformité
                    missing_fields = compliance_data.get("compliance_check", {}).get("missing_fields", [])
                    raise ComplianceError(
                        detail=f"Facture non conforme : {missing_fields}"
                    )
            except ComplianceError:
                raise
            except Exception as comp_error:
                raise ComplianceError(detail=f"Erreur lors de la validation de conformité : {str(comp_error)}")
        
        # Préparer les données de réponse
        response_data = {
            "text": ocr_result["text"],
            "language": ocr_result["language"]
        }
        if "pages_processed" in ocr_result:
            response_data["pages_processed"] = ocr_result["pages_processed"]
        
        # Stocker dans le cache
        cache_data = {
            "data": response_data,
            "extracted_data": extracted_data,
            "confidence_scores": confidence_scores
        }
        if compliance_data:
            cache_data["compliance"] = compliance_data
        set_cached_result(file_hash, cache_data)
        
        result = OCRResponse(
            success=True,
            data=response_data,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores,
            cached=False,
            compliance=compliance_data
        )
        
        # Stocker pour idempotence
        store_idempotency(request, result.dict())
        
        return result
    
    except (HTTPException, ComplianceError, DuplicateError, TimeoutError):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement : {str(e)}")


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
        
        # Vérifier le cache
        file_hash = get_file_hash(file_data)
        cached_result = get_cached_result(file_hash)
        
        if cached_result:
            log_cache_hit("/ocr/base64")
            # Retourner le résultat depuis le cache
            return OCRResponse(
                success=True,
                data=cached_result.get("data"),
                extracted_data=cached_result.get("extracted_data"),
                confidence_scores=cached_result.get("confidence_scores"),
                cached=True
            )
        
        log_cache_miss("/ocr/base64")
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
        
        # Stocker dans le cache
        cache_data = {
            "data": response_data,
            "extracted_data": extracted_data,
            "confidence_scores": confidence_scores
        }
        set_cached_result(file_hash, cache_data)
        
        return OCRResponse(
            success=True,
            data=response_data,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores,
            cached=False
        )
    
    except Exception as e:
        return OCRResponse(
            success=False,
            error=str(e)
        )


@app.post("/ocr/batch", response_model=BatchOCRResponse)
async def batch_ocr(batch_request: BatchOCRRequest):
    """
    Traite plusieurs factures en une seule requête (batch processing).
    
    **Paramètres:**
    - `files`: Liste d'images encodées en base64
    - `language`: Code langue pour OCR (fra, eng, deu, spa, ita, por). Défaut: fra
    
    **Limite:** Maximum 10 fichiers par requête
    
    **Retourne:**
    - Liste des résultats OCR pour chaque fichier
    - Nombre total traité
    - Nombre servi depuis le cache
    """
    if len(batch_request.files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 fichiers par requête batch"
        )
    
    results = []
    total_cached = 0
    
    for file_base64 in batch_request.files:
        try:
            # Décoder l'image base64
            is_pdf = False
            if file_base64.startswith("data:image"):
                file_base64 = file_base64.split(",")[1]
            elif file_base64.startswith("data:application/pdf"):
                is_pdf = True
                file_base64 = file_base64.split(",")[1]
            
            file_data = base64.b64decode(file_base64)
            
            # Vérifier le cache
            file_hash = get_file_hash(file_data)
            cached_result = get_cached_result(file_hash)
            
            if cached_result:
                results.append(OCRResponse(
                    success=True,
                    data=cached_result.get("data"),
                    extracted_data=cached_result.get("extracted_data"),
                    confidence_scores=cached_result.get("confidence_scores"),
                    cached=True
                ))
                total_cached += 1
            else:
                # Effectuer l'OCR
                ocr_result = perform_ocr(file_data, batch_request.language, is_pdf=is_pdf)
                
                # Extraire les données structurées
                extracted_data, confidence_scores = extract_invoice_data(ocr_result)
                
                # Préparer les données de réponse
                response_data = {
                    "text": ocr_result["text"],
                    "language": ocr_result["language"]
                }
                if "pages_processed" in ocr_result:
                    response_data["pages_processed"] = ocr_result["pages_processed"]
                
                # Stocker dans le cache
                cache_data = {
                    "data": response_data,
                    "extracted_data": extracted_data,
                    "confidence_scores": confidence_scores
                }
                set_cached_result(file_hash, cache_data)
                
                results.append(OCRResponse(
                    success=True,
                    data=response_data,
                    extracted_data=extracted_data,
                    confidence_scores=confidence_scores,
                    cached=False
                ))
        except Exception as e:
            results.append(OCRResponse(
                success=False,
                error=str(e)
            ))
    
    return BatchOCRResponse(
        success=True,
        results=results,
        total_processed=len(batch_request.files),
        total_cached=total_cached
    )


@app.post("/webhooks/zapier")
async def webhook_zapier(request: Request):
    """
    Webhook pour intégration Zapier
    Reçoit une facture et retourne les données extraites
    """
    try:
        form = await request.form()
        file = form.get("file")
        
        if not file:
            raise HTTPException(status_code=400, detail="Fichier manquant")
        
        file_data = await file.read()
        language = form.get("language", "fra")
        
        # Traiter la facture
        is_pdf = file.content_type == "application/pdf" if hasattr(file, 'content_type') else False
        ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        
        # Générer un ID unique pour la facture
        invoice_id = hashlib.md5(file_data).hexdigest()
        
        # Préparer le payload webhook
        webhook_payload = {
            "invoice_id": invoice_id,
            "invoice_data": extracted_data,
            "timestamp": datetime.now().isoformat(),
            "source": "ocr_facture_api"
        }
        
        return webhook_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/make")
async def webhook_make(request: Request):
    """
    Webhook pour intégration Make (Integromat)
    Reçoit une facture et retourne les données extraites
    """
    try:
        form = await request.form()
        file = form.get("file")
        
        if not file:
            raise HTTPException(status_code=400, detail="Fichier manquant")
        
        file_data = await file.read()
        language = form.get("language", "fra")
        
        # Traiter la facture
        is_pdf = file.content_type == "application/pdf" if hasattr(file, 'content_type') else False
        ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        
        # Générer un ID unique pour la facture
        invoice_id = hashlib.md5(file_data).hexdigest()
        
        # Préparer le payload webhook (format Make)
        webhook_payload = {
            "id": invoice_id,
            "data": extracted_data,
            "confidence": confidence_scores,
            "timestamp": datetime.now().isoformat()
        }
        
        return webhook_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/webhooks/salesforce")
async def webhook_salesforce(request: Request):
    """
    Webhook pour intégration Salesforce
    Reçoit une facture et retourne les données au format Salesforce
    """
    try:
        form = await request.form()
        file = form.get("file")
        
        if not file:
            raise HTTPException(status_code=400, detail="Fichier manquant")
        
        file_data = await file.read()
        language = form.get("language", "fra")
        
        # Traiter la facture
        is_pdf = file.content_type == "application/pdf" if hasattr(file, 'content_type') else False
        ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        
        # Préparer le payload Salesforce (format Salesforce Invoice object)
        salesforce_payload = {
            "InvoiceNumber": extracted_data.get("invoice_number"),
            "TotalAmount": extracted_data.get("total_ttc") or extracted_data.get("total"),
            "InvoiceDate": extracted_data.get("date"),
            "VendorName": extracted_data.get("vendor"),
            "CustomerName": extracted_data.get("client"),
            "Items": [
                {
                    "Description": item.get("description"),
                    "Quantity": item.get("quantity"),
                    "UnitPrice": item.get("unit_price"),
                    "TotalPrice": item.get("total")
                }
                for item in extracted_data.get("items", [])
            ],
            "BankingInfo": extracted_data.get("banking_info", {}),
            "ConfidenceScores": confidence_scores
        }
        
        return salesforce_payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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


@app.post("/compliance/check")
async def check_compliance_endpoint(
    invoice_data: dict = Body(...)
):
    """
    Vérifie la conformité d'une facture française
    
    **Paramètres:**
    - `invoice_data`: Données extraites de la facture (format JSON)
    
    **Retourne:**
    - Vérification compliance FR (mentions légales)
    - Validation TVA FR
    - Détection SIREN/SIRET
    - Détection TVA intracom
    - Enrichissement (si configuré)
    """
    try:
        compliance_result = extract_compliance_data(
            invoice_data,
            invoice_data.get("text", ""),
            siren_api_key=settings.sirene_api_key,
            siren_api_secret=settings.sirene_api_secret,
            siren_client_id=settings.sirene_client_id,
            siren_client_certificate=settings.sirene_client_certificate
        )
        return {
            "success": True,
            "compliance": compliance_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/validate-vat")
async def validate_vat_endpoint(
    invoice_data: dict = Body(...)
):
    """
    Valide les taux et calculs de TVA pour une facture française
    
    **Paramètres:**
    - `invoice_data`: Données extraites avec montants HT, TTC, TVA
    
    **Retourne:**
    - Validation des taux TVA (20%, 10%, 5.5%, 2.1%, 0%)
    - Vérification des calculs
    - Erreurs et avertissements
    """
    try:
        validation_result = validate_french_vat(invoice_data)
        return {
            "success": True,
            "validation": validation_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/enrich-siret")
async def enrich_siret_endpoint(
    siret: str = Body(..., embed=True)
):
    """
    Enrichit les données avec l'API Sirene (Insee) à partir d'un SIRET
    
    **Paramètres:**
    - `siret`: Numéro SIRET (14 chiffres)
    
    **Retourne:**
    - Raison sociale
    - Adresse complète
    - Forme juridique
    - Date de création
    - etc.
    """
    try:
        enrichment_result = enrich_siren_siret(
            siret,
            siren_api_key=settings.sirene_api_key,
            siren_api_secret=settings.sirene_api_secret,
            siren_client_id=settings.sirene_client_id,
            siren_client_certificate=settings.sirene_client_certificate
        )
        return {
            "success": True,
            "enrichment": enrichment_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compliance/validate-vies")
async def validate_vies_endpoint(
    vat_number: str = Body(..., embed=True)
):
    """
    Valide un numéro TVA intracommunautaire via l'API VIES
    
    **Paramètres:**
    - `vat_number`: Numéro TVA intracom (ex: FR47945319300)
    
    **Retourne:**
    - Validité du numéro
    - Nom de l'entreprise
    - Adresse
    """
    try:
        vies_result = validate_vies(vat_number)
        return {
            "success": True,
            "validation": vies_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/facturx/generate")
async def generate_facturx_endpoint(
    invoice_data: dict = Body(...)
):
    """
    Génère un XML Factur-X (EN16931) à partir des données de facture
    
    **Paramètres:**
    - `invoice_data`: Données de facture extraites (date, numéro, montants, vendeur, client, items)
    
    **Retourne:**
    - XML Factur-X conforme EN16931
    """
    try:
        xml_content = generate_facturx_xml(invoice_data)
        return {
            "success": True,
            "xml": xml_content,
            "format": "Factur-X EN16931"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/facturx/parse")
async def parse_facturx_endpoint(
    file: UploadFile = File(...)
):
    """
    Extrait le XML Factur-X embarqué dans un PDF/A-3
    
    **Paramètres:**
    - `file`: PDF/A-3 avec XML Factur-X embarqué
    
    **Retourne:**
    - XML extrait
    - Données parsées de la facture
    """
    try:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")
        
        file_data = await file.read()
        xml_content, invoice_data = parse_facturx_from_pdf(file_data)
        
        if not xml_content:
            raise HTTPException(status_code=404, detail="Aucun XML Factur-X trouvé dans le PDF")
        
        return {
            "success": True,
            "xml": xml_content,
            "invoice_data": invoice_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/facturx/parse-xml")
async def parse_facturx_xml_endpoint(
    xml_content: str = Body(..., embed=True)
):
    """
    Parse un XML Factur-X et extrait les données structurées
    
    **Paramètres:**
    - `xml_content`: XML Factur-X (format string)
    
    **Retourne:**
    - Données extraites de la facture
    """
    try:
        invoice_data = parse_facturx_xml(xml_content)
        return {
            "success": True,
            "invoice_data": invoice_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/facturx/validate")
async def validate_facturx_endpoint(
    xml_content: str = Body(..., embed=True)
):
    """
    Valide un XML Factur-X contre le schéma EN16931 et vérifie les règles métier
    
    **Paramètres:**
    - `xml_content`: XML Factur-X à valider
    
    **Retourne:**
    - Résultat de validation
    - Liste des erreurs
    - Liste des avertissements
    - Rapport lisible
    """
    try:
        validation_result = validate_facturx_xml(xml_content)
        return {
            "success": True,
            "validation": validation_result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Ajouter les autres endpoints v1 essentiels
@v1_router.post("/ocr/base64", response_model=OCRResponse)
async def ocr_from_base64_v1(
    request: Request,
    image_base64: str = Form(...),
    language: str = Form("fra")
):
    """Version v1 de /ocr/base64 avec idempotence"""
    idempotent_result = check_idempotency(request)
    if idempotent_result:
        raise DuplicateError(
            detail="Une requête identique a déjà été traitée avec cette Idempotency-Key",
            existing_result=idempotent_result
        )
    
    try:
        is_pdf = False
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]
        elif image_base64.startswith("data:application/pdf"):
            is_pdf = True
            image_base64 = image_base64.split(",")[1]
        
        file_data = base64.b64decode(image_base64)
        file_hash = get_file_hash(file_data)
        cached_result = get_cached_result(file_hash)
        
        if cached_result:
            result = OCRResponse(
                success=True,
                data=cached_result.get("data"),
                extracted_data=cached_result.get("extracted_data"),
                confidence_scores=cached_result.get("confidence_scores"),
                cached=True
            )
            store_idempotency(request, result.dict())
            return result
        
        try:
            ocr_result = perform_ocr(file_data, language, is_pdf=is_pdf)
        except Exception as ocr_error:
            if "timeout" in str(ocr_error).lower():
                raise TimeoutError("Le traitement OCR a dépassé le délai maximum")
            raise
        
        extracted_data, confidence_scores = extract_invoice_data(ocr_result)
        response_data = {
            "text": ocr_result["text"],
            "language": ocr_result["language"]
        }
        if "pages_processed" in ocr_result:
            response_data["pages_processed"] = ocr_result["pages_processed"]
        
        cache_data = {
            "data": response_data,
            "extracted_data": extracted_data,
            "confidence_scores": confidence_scores
        }
        set_cached_result(file_hash, cache_data)
        
        result = OCRResponse(
            success=True,
            data=response_data,
            extracted_data=extracted_data,
            confidence_scores=confidence_scores,
            cached=False
        )
        store_idempotency(request, result.dict())
        return result
    
    except (HTTPException, DuplicateError, TimeoutError):
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@v1_router.post("/ocr/batch", response_model=BatchOCRResponse)
async def batch_ocr_v1(request: Request, batch_request: BatchOCRRequest):
    """Version v1 de /ocr/batch avec idempotence"""
    idempotent_result = check_idempotency(request)
    if idempotent_result:
        raise DuplicateError(
            detail="Une requête identique a déjà été traitée avec cette Idempotency-Key",
            existing_result=idempotent_result
        )
    
    if len(batch_request.files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 fichiers par requête batch")
    
    results = []
    total_cached = 0
    
    for file_base64 in batch_request.files:
        try:
            is_pdf = False
            if file_base64.startswith("data:image"):
                file_base64 = file_base64.split(",")[1]
            elif file_base64.startswith("data:application/pdf"):
                is_pdf = True
                file_base64 = file_base64.split(",")[1]
            
            file_data = base64.b64decode(file_base64)
            file_hash = get_file_hash(file_data)
            cached_result = get_cached_result(file_hash)
            
            if cached_result:
                results.append(OCRResponse(
                    success=True,
                    data=cached_result.get("data"),
                    extracted_data=cached_result.get("extracted_data"),
                    confidence_scores=cached_result.get("confidence_scores"),
                    cached=True
                ))
                total_cached += 1
            else:
                try:
                    ocr_result = perform_ocr(file_data, batch_request.language, is_pdf=is_pdf)
                except Exception as ocr_error:
                    if "timeout" in str(ocr_error).lower():
                        raise TimeoutError("Le traitement OCR a dépassé le délai maximum")
                    raise
                
                extracted_data, confidence_scores = extract_invoice_data(ocr_result)
                response_data = {
                    "text": ocr_result["text"],
                    "language": ocr_result["language"]
                }
                if "pages_processed" in ocr_result:
                    response_data["pages_processed"] = ocr_result["pages_processed"]
                
                cache_data = {
                    "data": response_data,
                    "extracted_data": extracted_data,
                    "confidence_scores": confidence_scores
                }
                set_cached_result(file_hash, cache_data)
                
                results.append(OCRResponse(
                    success=True,
                    data=response_data,
                    extracted_data=extracted_data,
                    confidence_scores=confidence_scores,
                    cached=False
                ))
        except Exception as e:
            results.append(OCRResponse(success=False, error=str(e)))
    
    result = BatchOCRResponse(
        success=True,
        results=results,
        total_processed=len(batch_request.files),
        total_cached=total_cached
    )
    store_idempotency(request, result.dict())
    return result


@v1_router.post("/compliance/check")
async def compliance_check_v1(request: Request, invoice_data: dict = Body(...)):
    """Version v1 de /compliance/check avec codes d'erreur spécifiques"""
    try:
        compliance_result = extract_compliance_data(
            invoice_data,
            invoice_data.get("text", ""),
            siren_api_key=settings.sirene_api_key,
            siren_api_secret=settings.sirene_api_secret,
            siren_client_id=settings.sirene_client_id,
            siren_client_certificate=settings.sirene_client_certificate
        )
        if not compliance_result.get("compliance_check", {}).get("compliant", True):
            missing_fields = compliance_result.get("compliance_check", {}).get("missing_fields", [])
            raise ComplianceError(
                detail=f"Facture non conforme : {missing_fields}"
            )
        return {"success": True, "compliance": compliance_result}
    except ComplianceError:
        raise
    except Exception as e:
        raise ComplianceError(detail=f"Erreur lors de la validation : {str(e)}")


@v1_router.get("/languages")
async def get_languages_v1():
    """Version v1 de /languages"""
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


@v1_router.get("/quota")
async def get_quota_v1(request: Request):
    """
    Retourne les informations sur le quota restant pour l'utilisateur
    
    Headers retournés:
    - X-RateLimit-Limit: Limite totale
    - X-RateLimit-Remaining: Requêtes restantes
    - X-RateLimit-Reset: Timestamp de réinitialisation
    - X-RateLimit-Plan: Plan actuel
    """
    from rate_limiting import get_plan_from_request, check_rate_limit
    
    plan = get_plan_from_request(request)
    daily_allowed, daily_info = check_rate_limit(request, limit_type="daily")
    
    # Pour monthly, calculer depuis daily si nécessaire
    monthly_allowed, monthly_info = check_rate_limit(request, limit_type="monthly")
    
    return {
        "plan": plan,
        "daily": {
            "limit": daily_info["limit"] if daily_info else None,
            "remaining": daily_info["remaining"] if daily_info else None,
            "reset_time": daily_info["reset_time"] if daily_info else None
        },
        "monthly": {
            "limit": monthly_info["limit"] if monthly_info else None,
            "remaining": monthly_info["remaining"] if monthly_info else None,
            "reset_time": monthly_info["reset_time"] if monthly_info else None
        }
    }


@v1_router.get("/metrics")
async def get_metrics_v1(request: Request):
    """
    Retourne les métriques de performance de l'API
    
    Note: Endpoint pour monitoring interne, peut nécessiter authentification admin
    """
    metrics_data = get_metrics()
    return {
        "status": "ok",
        "metrics": metrics_data,
        "timestamp": datetime.now().isoformat()
    }


# Inclure le router v1 dans l'application
app.include_router(v1_router)

# Servir l'interface de démo React (si le dossier dist existe)
demo_dist_path = os.path.join(os.path.dirname(__file__), "demo", "dist")
if os.path.exists(demo_dist_path):
    app.mount("/demo", StaticFiles(directory=demo_dist_path, html=True), name="demo")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

