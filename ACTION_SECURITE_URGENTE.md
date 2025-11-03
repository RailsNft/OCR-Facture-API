# 🚨 ACTION SÉCURITÉ URGENTE

## ⚠️ VOTRE SECRET RAPIDAPI A ÉTÉ EXPOSÉ

**Secret exposé** : Votre secret RapidAPI actuel

Ce secret était dans 5 fichiers publics sur GitHub.

---

## ✅ CE QUI A ÉTÉ FAIT

1. ✅ Fichiers sensibles supprimés du Git
2. ✅ .gitignore amélioré (bloque futurs fichiers sensibles)
3. ✅ Rapport de sécurité créé

**Les fichiers sont toujours sur votre ordinateur** (pas supprimés localement)  
**Mais ils ne sont plus dans Git public** ✅

---

## 🔐 CE QUE VOUS DEVEZ FAIRE MAINTENANT (5 minutes)

### ÉTAPE 1 : Régénérer le secret RapidAPI (URGENT)

1. **Allez sur RapidAPI** : https://rapidapi.com/provider/dashboard
2. Cliquez sur votre API **"ocrfactureapi"**
3. Allez dans **"Settings"** ou **"Security"**
4. Cherchez **"Proxy Secret"** ou **"X-RapidAPI-Proxy-Secret"**
5. Cliquez **"Regenerate"** ou **"Rotate Secret"**
6. **Copiez le nouveau secret** (il ressemblera à : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)

---

### ÉTAPE 2 : Mettre à jour sur Railway (URGENT)

1. **Allez sur Railway** : https://railway.app
2. Ouvrez votre projet **"ocr-facture-api-production"**
3. Cliquez sur **"Variables"**
4. Trouvez **`RAPIDAPI_PROXY_SECRET`**
5. **Remplacez** par le nouveau secret
6. Cliquez **"Save"** ou **"Deploy"**

**Railway redéploiera automatiquement avec le nouveau secret.**

---

### ÉTAPE 3 : Tester que tout fonctionne (2 min)

Attendez 2-3 minutes que Railway redéploie, puis testez :

```bash
curl -X GET "https://ocr-facture-api-production.up.railway.app/languages" \
  -H "X-RapidAPI-Proxy-Secret: VOTRE_NOUVEAU_SECRET"
```

**Si ça retourne la liste des langues → C'est bon ! ✅**

---

## 📋 CHECKLIST SÉCURITÉ

- [ ] **Secret régénéré sur RapidAPI** (1 min)
- [ ] **Nouveau secret sur Railway** (1 min)
- [ ] **Railway redéployé** (2 min automatique)
- [ ] **Test avec nouveau secret** (30 sec)
- [ ] **Ancien secret ne fonctionne plus** (vérification)

**Temps total : 5 minutes**

---

## ⚠️ POURQUOI C'EST IMPORTANT ?

**Avec votre ancien secret exposé**, quelqu'un pourrait :
- ❌ Utiliser votre API gratuitement (consommer votre quota)
- ❌ Faire des requêtes malveillantes
- ❌ Vous faire dépasser vos limites

**Après régénération** :
- ✅ Ancien secret invalide
- ✅ Nouveau secret sécurisé
- ✅ Contrôle total restauré

---

## 🔒 BONNES PRATIQUES (Pour l'avenir)

### ✅ À FAIRE

1. **Toujours** utiliser variables d'environnement :
   ```python
   SECRET = os.getenv("RAPIDAPI_PROXY_SECRET")
   ```

2. **Jamais** hardcoder secrets dans code :
   ```python
   SECRET = "f67eb770-..."  # ❌ NE JAMAIS FAIRE ÇA
   ```

3. **Vérifier** avant chaque commit :
   ```bash
   git diff | grep -i "secret\|key\|password"
   ```

4. **Utiliser** des outils comme :
   - `git-secrets` (détecte secrets avant commit)
   - `trufflehog` (scan historique Git)

---

## 📞 SUPPORT

**Questions ?**

1. Comment régénérer secret RapidAPI ? → Voir guide ci-dessus
2. Comment mettre à jour Railway ? → Voir ÉTAPE 2
3. Problème après changement ? → Testez avec curl (ÉTAPE 3)

---

## 🎯 RÉCAP

**FAIT** :
- ✅ 5 fichiers sensibles retirés du Git
- ✅ .gitignore amélioré
- ✅ Rapport de sécurité créé

**À FAIRE (VOUS - 5 min)** :
1. Régénérer secret RapidAPI
2. Mettre à jour Railway
3. Tester

**Après ça, votre API sera sécurisée ! 🔒**

---

**Régénérez votre secret MAINTENANT, puis revenez me dire c'est fait !** 🚨

