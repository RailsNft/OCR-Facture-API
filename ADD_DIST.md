# Commandes à exécuter pour ajouter demo/dist/

```bash
# Forcer l'ajout des fichiers
git add -f demo/dist/

# Vérifier ce qui a été ajouté
git status

# Commit
git commit -m "Add demo interface build files"

# Push
git push
```

Si ça ne marche toujours pas, essayez :

```bash
# Ajouter tous les fichiers dans dist/
git add demo/dist/index.html demo/dist/assets/

# Ou forcer avec le chemin complet
git add --force demo/dist/
```

