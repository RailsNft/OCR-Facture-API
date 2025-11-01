# Conditions d'utilisation - OCR Facture API

## 📋 CONDITIONS GÉNÉRALES D'UTILISATION

En utilisant l'API OCR Facture France ("l'API", "le Service"), vous acceptez les présentes Conditions d'utilisation ("Conditions"). Si vous n'acceptez pas ces Conditions, vous ne devez pas utiliser l'API.

---

## 1. DÉFINITIONS

- **"API"** : Le service OCR Facture France accessible via RapidAPI, permettant l'extraction de données de factures via OCR.
- **"Utilisateur"** : Toute personne physique ou morale utilisant l'API.
- **"Données"** : Les informations extraites des factures traitées via l'API.
- **"Service"** : L'ensemble des fonctionnalités fournies par l'API, incluant l'extraction OCR, la validation de conformité, et la génération Factur-X.
- **"RapidAPI"** : La plateforme RapidAPI sur laquelle l'API est hébergée et distribuée.

---

## 2. ACCEPTATION DES CONDITIONS

En accédant ou en utilisant l'API, vous déclarez et garantissez que :

1. Vous avez lu, compris et accepté ces Conditions d'utilisation.
2. Vous avez la capacité légale de conclure un contrat (si vous êtes une personne physique) ou l'autorité pour lier votre entreprise (si vous êtes une personne morale).
3. Votre utilisation de l'API est conforme à toutes les lois et réglementations applicables.
4. Vous ne serez pas utiliser l'API à des fins illégales ou non autorisées.

---

## 3. DESCRIPTION DU SERVICE

L'API OCR Facture France fournit :

- **Extraction OCR** : Extraction automatique de texte et données structurées depuis des images et PDFs de factures.
- **Validation de conformité** : Vérification des mentions légales obligatoires pour factures françaises (TVA, SIREN/SIRET, dates, montants).
- **Génération Factur-X** : Création de fichiers XML Factur-X conformes au standard EN16931.
- **Enrichissement** : Enrichissement des données avec API Sirene (Insee) et validation VIES (optionnel).

Le Service est fourni "tel quel" et peut être modifié, suspendu ou interrompu à tout moment sans préavis.

---

## 4. UTILISATION AUTORISÉE

### 4.1 Utilisation autorisée

Vous êtes autorisé à utiliser l'API uniquement pour :

- Traiter vos propres factures et documents comptables.
- Intégrer l'API dans vos applications, logiciels ou services légitimes.
- Développer des applications conformes aux lois et réglementations applicables.

### 4.2 Utilisation interdite

Il est strictement interdit d'utiliser l'API pour :

- **Violer des lois** : Toute activité illégale ou frauduleuse.
- **Accès non autorisé** : Tenter d'accéder à des systèmes, données ou réseaux non autorisés.
- **Modification du Service** : Tenter de modifier, décompiler, reverse engineer ou extraire le code source de l'API.
- **Spam ou abus** : Envoyer des requêtes automatisées excessives, du spam, ou utiliser l'API de manière à nuire à la disponibilité du Service.
- **Données sensibles** : Traiter des données sensibles (santé, financières personnelles) sans autorisation appropriée.
- **Violation de propriété intellectuelle** : Violer les droits de propriété intellectuelle de tiers.
- **Falsification** : Manipuler ou falsifier les résultats de l'API.
- **Revendre le Service** : Revendre ou redistribuer l'API sans autorisation écrite explicite.

---

## 5. LIMITES D'UTILISATION

### 5.1 Quotas et limites

Votre utilisation de l'API est soumise aux limites de votre plan d'abonnement :

- **Plan BASIC (Gratuit)** : 100 requêtes par mois
  - Batch processing désactivé (1 facture = 1 requête)
  - OCR basique uniquement (pas de compliance FR, pas de Factur-X)
- **Plan PRO** : 20 000 requêtes par mois ($15/mois)
  - Batch processing activé (jusqu'à 10 factures par requête)
  - Compliance FR + Factur-X inclus
- **Plan ULTRA** : 80 000 requêtes par mois ($59/mois)
  - Batch processing activé (jusqu'à 10 factures par requête)
  - Compliance FR + Factur-X inclus
- **Plan MEGA** : 250 000 requêtes par mois ($149/mois)
  - Batch processing activé (jusqu'à 10 factures par requête)
  - Compliance FR + Factur-X inclus

Le dépassement des quotas peut entraîner la suspension temporaire ou permanente de votre accès.

### 5.2 Limites techniques

- **Taille de fichier** : Maximum 10 Mo par fichier (par défaut)
- **Traitement par lot** : 
  - Plan BASIC : Batch désactivé (1 facture = 1 requête obligatoire)
  - Plans PRO/ULTRA/MEGA : Maximum 10 fichiers par requête batch
- **Taux de requêtes** : Limites de débit selon votre plan (rate limiting)

### 5.3 Droit de modification

Nous nous réservons le droit de modifier les limites d'utilisation à tout moment, avec un préavis raisonnable pour les utilisateurs des plans PRO, ULTRA ou MEGA.

---

## 6. DONNÉES ET CONFIDENTIALITÉ

### 6.1 Données traitées

L'API traite les fichiers que vous uploadez pour :
- Effectuer l'extraction OCR
- Valider la conformité
- Générer les fichiers Factur-X

### 6.2 Stockage et rétention

- **Cache** : Les résultats peuvent être mis en cache jusqu'à 24 heures pour améliorer les performances.
- **Données sources** : Les fichiers uploadés ne sont pas stockés de manière permanente après traitement.
- **Résultats** : Les résultats peuvent être conservés dans le cache pour optimisation.

### 6.3 Confidentialité

- Nous ne vendons pas vos données à des tiers.
- Nous ne partageons vos données qu'avec :
  - Les services tiers nécessaires au fonctionnement de l'API (hébergement, API Sirene, VIES)
  - Les autorités légales si requis par la loi

### 6.4 Conformité RGPD

L'API est conforme au Règlement Général sur la Protection des Données (RGPD) :

- **Droit d'accès** : Vous pouvez demander l'accès à vos données.
- **Droit de rectification** : Vous pouvez demander la correction de vos données.
- **Droit à l'effacement** : Vous pouvez demander la suppression de vos données.
- **Droit à la portabilité** : Vous pouvez récupérer vos données dans un format structuré.
- **Droit d'opposition** : Vous pouvez vous opposer au traitement de vos données.

Pour exercer vos droits, contactez-nous via le support RapidAPI.

---

## 7. PROPRIÉTÉ INTELLECTUELLE

### 7.1 Droits de l'API

L'API, son code source, sa documentation, et tous les éléments associés sont la propriété exclusive du fournisseur de l'API et sont protégés par les lois sur la propriété intellectuelle.

### 7.2 Droits sur les données extraites

- Les **données extraites** de vos factures vous appartiennent.
- Les **résultats générés** (JSON, XML Factur-X) vous appartiennent.
- Vous êtes libre d'utiliser ces données comme vous le souhaitez, conformément à la loi.

### 7.3 Licences

En utilisant l'API, vous recevez une licence limitée, non exclusive, non transférable et révocable pour :
- Accéder et utiliser l'API selon ces Conditions.
- Intégrer l'API dans vos applications conformément à ces Conditions.

Cette licence ne vous accorde aucun droit de propriété sur l'API ou ses composants.

---

## 8. GARANTIES ET DISCLAIMERS

### 8.1 Service "tel quel"

L'API est fournie "EN L'ÉTAT" et "SELON DISPONIBILITÉ", sans garantie d'aucune sorte, expresse ou implicite, incluant mais sans s'y limiter :

- Garanties de qualité marchande
- Garanties d'adéquation à un usage particulier
- Garanties de non-violation
- Garanties concernant la précision, la fiabilité ou l'exhaustivité des résultats

### 8.2 Précision des résultats

- Les résultats de l'OCR peuvent contenir des erreurs, notamment pour :
  - Documents de mauvaise qualité
  - Documents scannés illisibles
  - Formats non standardisés
  - Factures avec mise en page complexe

- **Vous êtes responsable** de vérifier et valider tous les résultats avant utilisation dans un contexte professionnel ou légal.

- Les **scores de confiance** fournis sont indicatifs et ne garantissent pas la précision absolue.

### 8.3 Conformité légale

- L'API fournit des outils de validation de conformité, mais :
  - **Ne constitue pas un conseil juridique ou comptable**
  - **Ne garantit pas la conformité légale complète** de vos factures
  - **Ne remplace pas** l'avis d'un expert-comptable ou d'un avocat

- Vous êtes responsable de vous assurer que vos factures sont conformes à toutes les réglementations applicables.

### 8.4 Disponibilité du Service

- Nous ne garantissons pas que l'API sera disponible en permanence ou sans interruption.
- Le Service peut être interrompu pour :
  - Maintenance programmée ou d'urgence
  - Pannes techniques
  - Mises à jour
  - Raisons de sécurité

---

## 9. LIMITATION DE RESPONSABILITÉ

### 9.1 Exclusion de responsabilité

Dans les limites permises par la loi applicable, le fournisseur de l'API ne sera en aucun cas responsable de :

- **Dommages directs ou indirects** résultant de l'utilisation ou de l'impossibilité d'utiliser l'API
- **Perte de données**, de profits, de revenus, d'opportunités commerciales ou de réputation
- **Erreurs ou inexactitudes** dans les résultats de l'API
- **Interruptions du Service** ou perte de disponibilité
- **Dommages résultant** de l'utilisation des données extraites ou générées

### 9.2 Limite de responsabilité

Dans tous les cas, la responsabilité totale du fournisseur de l'API est limitée au montant que vous avez payé pour l'utilisation de l'API au cours des 12 derniers mois, ou à 100€ si vous utilisez le plan BASIC (gratuit).

### 9.3 Exceptions légales

Cette limitation de responsabilité ne s'applique pas en cas de :
- Faute intentionnelle ou dolosive
- Négligence grave
- Violation de garanties légales obligatoires selon la loi applicable

---

## 10. INDEMNISATION

Vous acceptez d'indemniser, défendre et dégager de toute responsabilité le fournisseur de l'API, ses dirigeants, employés et partenaires contre toutes réclamations, dommages, pertes, responsabilités et frais (y compris les frais d'avocat) résultant de :

- Votre utilisation de l'API
- Votre violation de ces Conditions
- Votre violation de droits de tiers
- Votre violation de lois ou réglementations applicables

---

## 11. MODIFICATIONS DES CONDITIONS

### 11.1 Droit de modification

Nous nous réservons le droit de modifier ces Conditions d'utilisation à tout moment.

### 11.2 Notification des modifications

- Pour les modifications majeures, nous vous notifierons :
  - Par email (pour utilisateurs des plans PRO, ULTRA ou MEGA)
  - Via la plateforme RapidAPI
  - Par mise à jour de ce document

### 11.3 Acceptation des modifications

- Votre utilisation continue de l'API après la publication des modifications constitue votre acceptation des nouvelles Conditions.
- Si vous n'acceptez pas les modifications, vous devez cesser d'utiliser l'API.

---

## 12. SUSPENSION ET RÉSILIATION

### 12.1 Résiliation par vous

Vous pouvez résilier votre utilisation de l'API à tout moment en :
- Annulant votre abonnement sur RapidAPI
- Cessant d'utiliser l'API

### 12.2 Résiliation par nous

Nous nous réservons le droit de suspendre ou résilier votre accès à l'API immédiatement, sans préavis, en cas de :

- Violation de ces Conditions
- Utilisation frauduleuse ou abusive
- Non-paiement (pour plans PRO, ULTRA, MEGA)
- Activité illégale
- Raisons de sécurité
- Dépassement répété des quotas de votre plan

### 12.3 Conséquences de la résiliation

En cas de résiliation :
- Votre accès à l'API sera immédiatement interrompu
- Toutes les données en cache pourront être supprimées
- Vous perdrez l'accès à tous les résultats précédents
- Les frais déjà payés ne sont pas remboursables (sauf obligation légale)

---

## 13. LOI APPLICABLE ET JURIDICTION

### 13.1 Loi applicable

Ces Conditions sont régies par le droit français.

### 13.2 Juridiction

En cas de litige, et à défaut d'accord amiable, les tribunaux français seront seuls compétents.

### 13.3 Médiation

Conformément à la législation française, en cas de litige, vous pouvez recourir à la médiation de la consommation. Plus d'informations sur : [https://www.economie.gouv.fr/mediation-conso](https://www.economie.gouv.fr/mediation-conso)

---

## 14. DISPOSITIONS GÉNÉRALES

### 14.1 Intégralité de l'accord

Ces Conditions constituent l'intégralité de l'accord entre vous et le fournisseur de l'API concernant l'utilisation de l'API.

### 14.2 Divisibilité

Si une disposition de ces Conditions est jugée invalide ou inapplicable, les autres dispositions restent en vigueur.

### 14.3 Non-renonciation

Le fait de ne pas exercer un droit prévu par ces Conditions ne constitue pas une renonciation à ce droit.

### 14.4 Cession

Vous ne pouvez pas céder ou transférer vos droits ou obligations sous ces Conditions sans notre consentement écrit préalable.

### 14.5 Force majeure

Nous ne serons pas responsables de tout retard ou défaillance dans l'exécution de nos obligations résultant de circonstances indépendantes de notre volonté raisonnable (force majeure).

---

## 15. CONTACT ET SUPPORT

### 15.1 Support technique

Pour toute question technique concernant l'API :
- **Support RapidAPI** : Via le dashboard RapidAPI
- **Documentation** : `/docs` (Swagger UI)
- **GitHub** : [https://github.com/RailsNft/OCR-Facture-API](https://github.com/RailsNft/OCR-Facture-API)

### 15.2 Questions légales

Pour toute question concernant ces Conditions d'utilisation :
- Contactez-nous via le support RapidAPI
- Mentionnez "Questions Conditions d'utilisation" dans votre demande

### 15.3 Signalement d'abus

Pour signaler un abus ou une violation de ces Conditions :
- Contactez le support RapidAPI
- Fournissez tous les détails pertinents

---

## 16. ACCEPTATION

En utilisant l'API, vous reconnaissez avoir lu, compris et accepté ces Conditions d'utilisation dans leur intégralité.

Si vous n'acceptez pas ces Conditions, vous ne devez pas utiliser l'API.

