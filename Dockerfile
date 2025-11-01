FROM python:3.11-slim

# Installer Tesseract OCR et les dépendances système
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-fra \
    tesseract-ocr-eng \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    tesseract-ocr-ita \
    tesseract-ocr-por \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code de l'application
COPY . .

# Rendre le script de démarrage exécutable
RUN chmod +x start.sh

# Exposer le port (Railway définit PORT dynamiquement)
EXPOSE ${PORT:-8000}

# Commande pour démarrer l'application
CMD ["./start.sh"]

