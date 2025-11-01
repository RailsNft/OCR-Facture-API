#!/bin/bash
# Script pour commit et push les changements

cd /Users/philippe/Downloads/OCR-Facture-API

# Ajouter tous les changements
git add -A

# Commit avec message descriptif
git commit -m "Mise à jour tarifs et nettoyage fichiers obsolètes

- Mise à jour tarifs: Basic (100/mois gratuit), Pro (20k/mois \$15), Ultra (80k/mois \$59), Mega (250k/mois \$149)
- Suppression fichiers obsolètes: CHANGELOG multiples, nettoyer_historique.sh, test_api.py, etc.
- Mise à jour rate_limiting.py avec nouveaux plans
- Synchronisation tous les fichiers de documentation avec bons tarifs
- SDK Python et JavaScript finalisés
- CI/CD GitHub Actions configuré"

# Push vers origin
git push origin main

echo "✅ Changements poussés sur Git avec succès!"

