from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import base64
from typing import Optional
from config import settings
from pydantic import BaseModel
import pytesseract
from PIL import Image
import io
import re

app = FastAPI(
    title="OCR Facture API",
    description="API professionnelle pour l'extraction automatique de données de factures via OCR. Extrait le texte, les montants, dates, numéros de facture et autres informations structurées.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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


def perform_ocr(image_data: bytes, language: str = "fra") -> dict:
    """
    Effectue l'OCR sur l'image utilisant pytesseract
    """
    try:
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
        
        # Effectuer l'OCR
        text = pytesseract.image_to_string(image, lang=tesseract_lang)
        
        # Obtenir les données détaillées
        data = pytesseract.image_to_data(image, lang=tesseract_lang, output_type=pytesseract.Output.DICT)
        
        return {
            "text": text,
            "data": data,
            "language": tesseract_lang
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement OCR: {str(e)}")


def extract_invoice_data(ocr_result: dict) -> dict:
    """
    Extrait les données structurées de la facture depuis le résultat OCR
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
    
    parsed_text = ocr_result.get("text", "")
    extracted["text"] = parsed_text
    
    # Extraire les lignes de texte
    lines = [line.strip() for line in parsed_text.split("\n") if line.strip()]
    extracted["lines"] = lines
    
    if not parsed_text:
        return extracted
    
    text_lower = parsed_text.lower()
    
    # Recherche du total
    total_patterns = [
        r'total\s*(?:ttc|t\.t\.c\.)?\s*[:=]?\s*([\d\s,]+\.?\d*)\s*([€$£]|eur|usd|gbp)?',
        r'montant\s*total\s*[:=]?\s*([\d\s,]+\.?\d*)\s*([€$£]|eur|usd|gbp)?',
        r'total\s*[:=]?\s*([\d\s,]+\.?\d*)\s*([€$£]|eur|usd|gbp)?'
    ]
    
    for pattern in total_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                extracted["total"] = float(amount_str)
                if match.lastindex >= 2 and match.group(2):
                    currency_map = {"€": "EUR", "$": "USD", "£": "GBP", "eur": "EUR", "usd": "USD", "gbp": "GBP"}
                    extracted["currency"] = currency_map.get(match.group(2).lower(), "EUR")
                break
            except:
                pass
    
    # Recherche du total HT
    ht_patterns = [
        r'total\s*ht\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'montant\s*ht\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'ht\s*[:=]?\s*([\d\s,]+\.?\d*)'
    ]
    for pattern in ht_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                extracted["total_ht"] = float(amount_str)
                break
            except:
                pass
    
    # Recherche du total TTC
    ttc_patterns = [
        r'total\s*ttc\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'montant\s*ttc\s*[:=]?\s*([\d\s,]+\.?\d*)',
        r'ttc\s*[:=]?\s*([\d\s,]+\.?\d*)'
    ]
    for pattern in ttc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            try:
                amount_str = match.group(1).replace(' ', '').replace(',', '.')
                extracted["total_ttc"] = float(amount_str)
                break
            except:
                pass
    
    # Calcul de la TVA si HT et TTC disponibles
    if extracted["total_ht"] and extracted["total_ttc"]:
        extracted["tva"] = extracted["total_ttc"] - extracted["total_ht"]
    
    # Recherche de la date
    date_patterns = [
        r'\b(\d{2}[/-]\d{2}[/-]\d{4})\b',
        r'\b(\d{4}[/-]\d{2}[/-]\d{2})\b',
        r'\b(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre|jan|fév|mar|avr|mai|jun|jul|aoû|sep|oct|nov|déc)\s+\d{4})\b',
        r'\b(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s+\d{4})\b'
    ]
    for pattern in date_patterns:
        match = re.search(pattern, parsed_text, re.IGNORECASE)
        if match:
            extracted["date"] = match.group(1)
            break
    
    # Recherche du numéro de facture
    invoice_patterns = [
        r'facture\s*(?:n°|no|number)?\s*[:=]?\s*([A-Z0-9\-]+)',
        r'invoice\s*(?:#|n°|no|number)?\s*[:=]?\s*([A-Z0-9\-]+)',
        r'n°\s*(?:facture|invoice)?\s*[:=]?\s*([A-Z0-9\-]+)',
        r'ref[ée]rence\s*[:=]?\s*([A-Z0-9\-]+)'
    ]
    for pattern in invoice_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted["invoice_number"] = match.group(1).upper()
            break
    
    # Recherche du vendeur/fournisseur (généralement dans les premières lignes)
    vendor_keywords = ["sarl", "ltd", "inc", "sas", "sa", "eurl", "société"]
    for i, line in enumerate(lines[:10]):  # Chercher dans les 10 premières lignes
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in vendor_keywords) or i < 3:
            if len(line) > 5 and len(line) < 100:
                extracted["vendor"] = line.strip()
                break
    
    # Recherche du client
    client_keywords = ["client", "customer", "billing to", "facturé à"]
    for keyword in client_keywords:
        for line in lines:
            if keyword in line.lower():
                extracted["client"] = line.strip()
                break
        if extracted["client"]:
            break
    
    return extracted


@app.get("/")
async def root():
    return {
        "message": "OCR Facture API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "debug_mode": settings.debug_mode,
        "api_version": "1.0.0"
    }


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
    - Données structurées (total, date, numéro de facture, vendeur, etc.)
    """
    # Vérifier le type de fichier
    if not file.content_type or not (file.content_type.startswith("image/") or file.content_type == "application/pdf"):
        raise HTTPException(
            status_code=400,
            detail="Le fichier doit être une image (jpeg, png) ou un PDF"
        )
    
    try:
        # Lire le contenu du fichier
        image_data = await file.read()
        
        # Effectuer l'OCR
        ocr_result = perform_ocr(image_data, language)
        
        # Extraire les données structurées
        extracted_data = extract_invoice_data(ocr_result)
        
        return OCRResponse(
            success=True,
            data={
                "text": ocr_result["text"],
                "language": ocr_result["language"]
            },
            extracted_data=extracted_data
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
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]
        
        image_data = base64.b64decode(image_base64)
        
        # Effectuer l'OCR
        ocr_result = perform_ocr(image_data, language)
        
        # Extraire les données structurées
        extracted_data = extract_invoice_data(ocr_result)
        
        return OCRResponse(
            success=True,
            data={
                "text": ocr_result["text"],
                "language": ocr_result["language"]
            },
            extracted_data=extracted_data
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

