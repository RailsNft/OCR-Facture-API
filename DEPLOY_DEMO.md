# 🚀 Déploiement de l'interface de démo

## Méthode simple : Build avant push

L'interface React doit être buildée **avant** le déploiement. Le dossier `demo/dist` sera ensuite servi par FastAPI.

### Étapes :

1. **Builder l'interface localement** :
```bash
cd demo
npm install
npm run build
cd ..
```

2. **Vérifier que demo/dist existe** :
```bash
ls -la demo/dist/
```

3. **Commit et push** :
```bash
git add demo/dist/
git commit -m "Add demo interface build"
git push
```

4. **Railway va déployer automatiquement** et l'interface sera accessible sur `/demo`

## Note importante

Le dossier `demo/dist` doit être **commité dans Git** pour être déployé. Il est déjà exclu du `.gitignore` de la racine, mais inclus dans `demo/.gitignore` - vous pouvez retirer cette exclusion si nécessaire.

## Alternative : Build dans Railway (optionnel)

Si vous préférez builder sur Railway, ajoutez une variable d'environnement `RAILWAY_BUILD_COMMAND` :
```
cd demo && npm install && npm run build
```

Mais la méthode simple (build local + commit) est recommandée.



