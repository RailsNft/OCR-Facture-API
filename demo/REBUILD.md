# 🔄 Rebuild nécessaire

Après modification du code source, vous devez rebuilder l'interface :

```bash
cd demo
npm run build
cd ..
git add demo/dist/ demo/src/App.jsx
git commit -m "Fix API key header sending"
git push
```

## Vérifications

1. Ouvrez la console du navigateur (F12)
2. Entrez votre clé API dans le champ
3. Upload une facture
4. Vérifiez dans la console :
   - "Envoi de la requête vers: ..."
   - "Header X-RapidAPI-Proxy-Secret: Présent"
   - Si erreur, vérifiez les logs

## Important

La clé API doit correspondre exactement à `RAPIDAPI_PROXY_SECRET` dans les variables d'environnement Railway.



