#!/bin/bash
# Script pour nettoyer l'historique Git des secrets exposés

set -e  # Arrêter en cas d'erreur

echo "🧹 Nettoyage de l'historique Git des secrets exposés"
echo "=================================================="
echo ""

# Vérifier qu'on est dans un dépôt Git
if [ ! -d .git ]; then
    echo "❌ Erreur : Ce script doit être exécuté dans un dépôt Git"
    exit 1
fi

# Vérifier que les changements sont commités
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  Attention : Vous avez des changements non commités"
    echo "Voulez-vous les commiter avant de continuer ? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        git add .
        git commit -m "Nettoyer les secrets des fichiers avant nettoyage historique"
    else
        echo "❌ Annulé. Commitez d'abord vos changements."
        exit 1
    fi
fi

# Créer une branche de sauvegarde
echo "📦 Création d'une branche de sauvegarde..."
git branch backup-avant-nettoyage-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true
echo "✅ Sauvegarde créée"
echo ""

# Fichiers à nettoyer de l'historique
FILES_TO_REMOVE="test_ocr_invoice.py HOW_TO_TEST_IN_SWAGGER.md TEST_WITH_CURL.md TEST_REPORT.md create_test_invoice.py"

echo "🔍 Fichiers à nettoyer de l'historique :"
for file in $FILES_TO_REMOVE; do
    if git log --all --oneline -- "$file" | head -1 > /dev/null 2>&1; then
        echo "  - $file (présent dans l'historique)"
    else
        echo "  - $file (non trouvé dans l'historique)"
    fi
done
echo ""

echo "⚠️  ATTENTION : Cette opération va réécrire l'historique Git"
echo "   Si quelqu'un a déjà cloné le dépôt, il devra le recréer"
echo ""
echo "Voulez-vous continuer ? (y/n)"
read -r response

if [ "$response" != "y" ]; then
    echo "❌ Annulé."
    exit 1
fi

echo ""
echo "🧹 Nettoyage de l'historique avec git filter-branch..."
echo "   (Cela peut prendre quelques minutes)"

# Nettoyer l'historique
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch $FILES_TO_REMOVE" \
  --prune-empty --tag-name-filter cat -- --all

echo ""
echo "🧹 Nettoyage des références Git..."

# Supprimer les sauvegardes créées par filter-branch
rm -rf .git/refs/original/ 2>/dev/null || true

# Nettoyer le reflog
git reflog expire --expire=now --all 2>/dev/null || true

# Nettoyer et optimiser
git gc --prune=now --aggressive 2>/dev/null || true

echo ""
echo "✅ Nettoyage terminé !"
echo ""
echo "🔍 Vérification que les secrets ont disparu..."

# Vérifier que les secrets ne sont plus dans l'historique
SECRET_RAPIDAPI="f67eb770-b6b9-11f0-9b0e-0f41c7e962fd"
SECRET_SIRENE_KEY="cb14a7e2-62f9-4574-8ec1-bcd06e679eb0"
SECRET_SIRENE_SECRET="cKBNQc63dwaoHFVohIWuP2kXuBL2XGsa"

FOUND_SECRETS=0

if git log -p --all | grep -q "$SECRET_RAPIDAPI"; then
    echo "  ⚠️  Secret RapidAPI encore trouvé dans l'historique"
    FOUND_SECRETS=1
fi

if git log -p --all | grep -q "$SECRET_SIRENE_KEY"; then
    echo "  ⚠️  Secret Sirene Key encore trouvé dans l'historique"
    FOUND_SECRETS=1
fi

if git log -p --all | grep -q "$SECRET_SIRENE_SECRET"; then
    echo "  ⚠️  Secret Sirene Secret encore trouvé dans l'historique"
    FOUND_SECRETS=1
fi

if [ $FOUND_SECRETS -eq 0 ]; then
    echo "  ✅ Aucun secret trouvé dans l'historique !"
else
    echo "  ⚠️  Des secrets sont encore présents. Vous devrez peut-être utiliser BFG Repo-Cleaner."
fi

echo ""
echo "📋 Prochaines étapes :"
echo ""
echo "1. Vérifiez que tout fonctionne :"
echo "   git log --oneline"
echo ""
echo "2. Si tout est OK, forcez le push sur GitHub :"
echo "   git push origin --force --all"
echo "   git push origin --force --tags"
echo ""
echo "3. Si vous avez des collaborateurs, ils devront recréer leur clone :"
echo "   rm -rf OCR-Facture-API"
echo "   git clone https://github.com/RailsNft/OCR-Facture-API.git"
echo ""
echo "✅ Terminé !"

