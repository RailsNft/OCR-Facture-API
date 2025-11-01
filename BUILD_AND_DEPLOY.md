# 🚀 Build et déploiement de l'interface

## Étape 1 : Builder l'interface

Dans votre terminal, exécutez :

```bash
cd demo
npm install
npm run build
cd ..
```

Cela créera le dossier `demo/dist/` avec les fichiers de production.

## Étape 2 : Vérifier que dist/ existe

```bash
ls -la demo/dist/
```

Vous devriez voir des fichiers comme `index.html`, `assets/`, etc.

## Étape 3 : Commit et push

```bash
git add demo/dist/
git commit -m "Add demo interface build"
git push
```

## Étape 4 : Accéder à l'interface

Une fois déployé sur Railway, l'interface sera accessible sur :
- `https://votre-api.railway.app/demo`

## Note

Le dossier `demo/dist/` doit être commité dans Git pour être déployé sur Railway.

