# 🧹 Nettoyer l'historique Git des secrets exposés

## ⚠️ Avant de commencer

**IMPORTANT** : Cette méthode ne fonctionne que si :
- ✅ Votre dépôt GitHub est **privé** (ou personne ne l'a cloné)
- ✅ Vous êtes le seul contributeur (ou tous sont d'accord)
- ✅ Vous acceptez de **réécrire l'historique Git** (les commits changent)

Si quelqu'un a déjà cloné le dépôt, il aura toujours les anciens secrets dans son historique local.

---

## 🎯 Option 1 : Utiliser `git filter-branch` (méthode standard)

### Étape 1 : Identifier les fichiers à nettoyer

Les fichiers suivants contenaient des secrets et sont dans l'historique Git :
- `test_ocr_invoice.py` (secret RapidAPI)
- `HOW_TO_TEST_IN_SWAGGER.md` (secret RapidAPI)
- `TEST_WITH_CURL.md` (secret RapidAPI)
- `TEST_REPORT.md` (secret RapidAPI)
- `create_test_invoice.py` (secret RapidAPI)

### Étape 2 : Sauvegarder votre travail actuel

```bash
# Assurez-vous que tous vos changements sont commités
git add .
git commit -m "Nettoyer les secrets des fichiers"

# Créez une branche de sauvegarde (au cas où)
git branch backup-avant-nettoyage
```

### Étape 3 : Nettoyer l'historique avec git filter-branch

```bash
# Supprimer les fichiers sensibles de TOUT l'historique Git
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch test_ocr_invoice.py HOW_TO_TEST_IN_SWAGGER.md TEST_WITH_CURL.md TEST_REPORT.md create_test_invoice.py" \
  --prune-empty --tag-name-filter cat -- --all
```

**Explication** :
- `--force` : Force la réécriture même si des sauvegardes existent
- `--index-filter` : Modifie l'index Git sans créer de nouveaux fichiers
- `git rm --cached` : Supprime les fichiers de l'index Git mais les garde sur le disque
- `--ignore-unmatch` : Continue même si un fichier n'existe pas dans certains commits
- `--prune-empty` : Supprime les commits vides créés
- `--tag-name-filter cat` : Préserve les tags
- `-- --all` : Applique à toutes les branches

### Étape 4 : Nettoyer les références (OBLIGATOIRE)

```bash
# Supprimer les sauvegardes créées par filter-branch
rm -rf .git/refs/original/

# Nettoyer le reflog
git reflog expire --expire=now --all

# Nettoyer et optimiser le dépôt
git gc --prune=now --aggressive
```

### Étape 5 : Forcer la mise à jour sur GitHub

⚠️ **ATTENTION** : Cela réécrit l'historique sur GitHub. Tous les collaborateurs devront recréer leur dépôt local.

```bash
# Forcer le push (remplace l'historique sur GitHub)
git push origin --force --all
git push origin --force --tags
```

---

## 🚀 Option 2 : Utiliser BFG Repo-Cleaner (plus rapide et recommandé)

BFG est plus rapide et plus simple que `git filter-branch`.

### Étape 1 : Installer BFG

**Sur macOS** :
```bash
brew install bfg
```

**Ou télécharger** : https://rtyley.github.io/bfg-repo-cleaner/

### Étape 2 : Créer un fichier avec les secrets à supprimer

```bash
# Créer un fichier avec les secrets à supprimer
cat > secrets.txt << EOF
f67eb770-b6b9-11f0-9b0e-0f41c7e962fd
cb14a7e2-62f9-4574-8ec1-bcd06e679eb0
cKBNQc63dwaoHFVohIWuP2kXuBL2XGsa
EOF
```

### Étape 3 : Nettoyer avec BFG

```bash
# Supprimer les secrets de l'historique
bfg --replace-text secrets.txt

# Ou supprimer complètement les fichiers
bfg --delete-files test_ocr_invoice.py
bfg --delete-files HOW_TO_TEST_IN_SWAGGER.md
bfg --delete-files TEST_WITH_CURL.md
bfg --delete-files TEST_REPORT.md
bfg --delete-files create_test_invoice.py
```

### Étape 4 : Nettoyer et forcer le push

```bash
# Nettoyer
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Forcer le push
git push origin --force --all
```

---

## ✅ Option 3 : Solution simple si les fichiers ne sont pas encore commités

Si les fichiers avec secrets ne sont **pas encore dans l'historique Git** (juste modifiés localement), vous pouvez simplement :

```bash
# Vérifier qu'ils ne sont pas dans l'historique
git log --all --oneline -- QUICK_START_SIRENE.md MES_IDENTIFIANTS_SIRENE.md CONFIGURATION_EXEMPLE.md MON_ENV_EXEMPLE.txt

# Si aucun résultat, ces fichiers ne sont pas dans Git → Parfait !
# Il suffit de s'assurer qu'ils sont dans .gitignore (déjà fait)
```

---

## 🔍 Vérification après nettoyage

### Vérifier que les secrets ont disparu

```bash
# Chercher les secrets dans l'historique Git
git log -p --all | grep -i "f67eb770-b6b9-11f0-9b0e-0f41c7e962fd"
git log -p --all | grep -i "cb14a7e2-62f9-4574-8ec1-bcd06e679eb0"
git log -p --all | grep -i "cKBNQc63dwaoHFVohIWuP2kXuBL2XGsa"

# Si aucun résultat, c'est bon ! ✅
```

### Vérifier que les fichiers ne sont plus dans Git

```bash
# Vérifier qu'un fichier n'est plus dans l'historique
git log --all --oneline -- test_ocr_invoice.py

# Si aucun résultat, le fichier a été supprimé de l'historique ✅
```

---

## ⚠️ Actions importantes après nettoyage

### 1. Informer les collaborateurs (si vous en avez)

Envoyez-leur ces instructions :

```bash
# Supprimer leur clone local
rm -rf OCR-Facture-API

# Recloner le dépôt propre
git clone https://github.com/RailsNft/OCR-Facture-API.git
cd OCR-Facture-API
```

### 2. Mettre à jour les variables d'environnement (si vous aviez révoqué)

Si vous aviez révoqué les identifiants avant de nettoyer Git, vous devrez :
- Créer de nouveaux identifiants
- Les mettre dans `.env` et Railway

### 3. Vérifier que GitHub n'a pas archivé l'historique

GitHub peut avoir archivé l'historique. Vérifiez :
- Allez sur votre dépôt GitHub
- Vérifiez que les anciens commits ne sont plus visibles

---

## 🎯 Recommandation : Option 3 (simple) si possible

**Si les fichiers avec secrets ne sont PAS dans l'historique Git** (fichiers non trackés), vous n'avez rien à faire ! Juste :

1. ✅ Vérifier qu'ils sont dans `.gitignore` (déjà fait)
2. ✅ S'assurer qu'ils ne sont jamais commités
3. ✅ Optionnel : Révoquer quand même les identifiants pour être sûr

---

## 📋 Checklist finale

- [ ] Vérifié si les fichiers sont dans l'historique Git
- [ ] Choisi la méthode de nettoyage (filter-branch ou BFG)
- [ ] Sauvegardé le travail actuel
- [ ] Nettoyé l'historique Git
- [ ] Vérifié que les secrets ont disparu
- [ ] Forcé le push sur GitHub
- [ ] Informé les collaborateurs (si nécessaire)
- [ ] Vérifié que GitHub affiche le nouvel historique

---

## 🆘 En cas de problème

Si quelque chose ne va pas après le nettoyage :

```bash
# Restaurer depuis la sauvegarde
git branch -D main  # ou master
git checkout backup-avant-nettoyage
git branch -m main
git push origin --force main
```

---

**Note** : Même après nettoyage de l'historique Git, si le dépôt était public, les secrets peuvent avoir été archivés par des services comme GitHub Archive, archive.org, etc. Dans ce cas, révoquer les identifiants reste la meilleure solution.

