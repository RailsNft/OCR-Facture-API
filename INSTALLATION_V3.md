# Guide d'installation - Version 3.0.0

## 📦 Installation des dépendances

### Dépendances Python

```bash
pip install -r requirements.txt
```

**Nouvelles dépendances v3.0.0** :
- `opencv-python>=4.8.0` - Préprocessing d'image amélioré (optionnel mais recommandé)
- `numpy>=1.24.0` - Support préprocessing

**Note** : Si OpenCV n'est pas installé, le preprocessing utilisera PIL uniquement (fonctionnalités limitées).

### Installation OpenCV (recommandé)

**macOS** :
```bash
brew install opencv
pip install opencv-python
```

**Ubuntu/Debian** :
```bash
sudo apt-get install python3-opencv
pip install opencv-python
```

**Windows** :
```bash
pip install opencv-python
```

---

## 🚀 Démarrage rapide

### 1. Configuration

Copier `.env.example` vers `.env` :
```bash
cp env.example .env
```

Éditer `.env` :
```env
RAPIDAPI_PROXY_SECRET=votre_secret_rapidapi
DEBUG_MODE=False
DEFAULT_LANGUAGE=fra
SIRENE_API_KEY=optionnel
SIRENE_API_SECRET=optionnel
```

### 2. Lancer l'API

```bash
python main.py
```

Ou avec uvicorn :
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. Vérifier le fonctionnement

```bash
curl http://localhost:8000/health
```

---

## 📦 Installation du SDK Python

### Option 1 : Installation depuis le répertoire local

```bash
cd sdk/python
pip install -e .
```

### Option 2 : Installation depuis PyPI (quand publié)

```bash
pip install ocr-facture-api
```

### Utilisation du SDK

```python
from ocr_facture_api import OCRFactureAPI

api = OCRFactureAPI(
    api_key="votre_cle_api",
    base_url="https://votre-api.com"
)

result = api.extract_from_file("facture.pdf")
print(result["extracted_data"]["invoice_number"])
```

---

## 🔧 Configuration avancée

### Rate Limiting

Le rate limiting est activé automatiquement. Pour modifier les limites, éditer `rate_limiting.py` :

```python
PLAN_LIMITS = {
    "BASIC": {
        "monthly": 100,
        "daily": None,
        "per_minute": 1,
    },
    # ...
}
```

### Monitoring

Les logs sont envoyés vers stdout par défaut. Pour rediriger vers un fichier :

```python
# Dans monitoring.py
logging.basicConfig(
    handlers=[
        logging.FileHandler("api.log"),
        logging.StreamHandler()
    ]
)
```

### Préprocessing

Le préprocessing est activé automatiquement pour les images de faible qualité. Pour désactiver :

```python
# Dans main.py, fonction perform_ocr()
# Commenter ces lignes :
# if should_preprocess(image):
#     image = preprocess_image(...)
```

---

## 🐳 Docker

### Build

```bash
docker build -t ocr-facture-api .
```

### Run

```bash
docker run -p 8000:8000 \
  -e RAPIDAPI_PROXY_SECRET=votre_secret \
  ocr-facture-api
```

---

## ☁️ Déploiement

### Railway

1. Connecter le repository GitHub
2. Railway détecte automatiquement le `Dockerfile`
3. Ajouter les variables d'environnement dans Railway dashboard

### Render

1. Créer un nouveau Web Service
2. Connecter le repository
3. Build command : `pip install -r requirements.txt`
4. Start command : `uvicorn main:app --host 0.0.0.0 --port $PORT`

---

## ✅ Vérification

### Health Check

```bash
curl http://localhost:8000/health
```

Réponse attendue :
```json
{
  "status": "healthy",
  "debug_mode": false,
  "api_version": "2.0.0",
  "cache_size": 0,
  "tesseract": "available"
}
```

### Test OCR

```bash
curl -X POST http://localhost:8000/v1/ocr/upload \
  -H "X-RapidAPI-Proxy-Secret: votre_secret" \
  -F "file=@facture_test.png" \
  -F "language=fra"
```

### Vérifier les métriques

```bash
curl http://localhost:8000/v1/metrics \
  -H "X-RapidAPI-Proxy-Secret: votre_secret"
```

### Vérifier le quota

```bash
curl http://localhost:8000/v1/quota \
  -H "X-RapidAPI-Proxy-Secret: votre_secret"
```

---

## 🔍 Dépannage

### Erreur : "Tesseract OCR n'est pas disponible"

**Solution** : Installer Tesseract OCR
- macOS : `brew install tesseract`
- Ubuntu : `sudo apt-get install tesseract-ocr`

### Erreur : "OpenCV not available"

**Solution** : Installer OpenCV (optionnel)
```bash
pip install opencv-python
```

### Rate limiting trop strict

**Solution** : Modifier les limites dans `rate_limiting.py` ou désactiver temporairement en mode debug.

### Cache mémoire plein

**Solution** : Migrer vers Redis (voir TODOS_DEVELOPPEMENT.md)

---

## 📚 Documentation

- Documentation API complète : `http://localhost:8000/docs`
- Documentation ReDoc : `http://localhost:8000/redoc`
- Guide SDK : `sdk/python/README.md`

---

**Version 3.0.0** - Prêt pour la production ! 🚀





