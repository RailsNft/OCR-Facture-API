#!/bin/bash
set -e

# Afficher la version de Tesseract pour debug
echo "Checking Tesseract installation..."
tesseract --version || echo "WARNING: Tesseract not found"

# Afficher les variables d'environnement importantes
echo "PORT: ${PORT:-8000}"
echo "DEBUG_MODE: ${DEBUG_MODE:-False}"

# Démarrer l'application
echo "Starting application on port ${PORT:-8000}..."
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}

