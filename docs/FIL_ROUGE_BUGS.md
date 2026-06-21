# Fil rouge — bugs intentionnels

Ce document décrit les anomalies volontairement introduites dans eventflow pour servir de support aux exercices QA. Toutes sont **désactivées par défaut** et pilotées par une seule variable d'environnement.

## Activation

Les bugs ne s'activent que lorsque `SEED_BUGS=true`. Par défaut (`false`), l'application a un comportement correct, qui sert de référence.

Avec Docker :

```bash
SEED_BUGS=true docker compose up --build backend
```

En local :

```bash
SEED_BUGS=true uvicorn app.main:app --reload
```

L'état courant est exposé par l'API : `GET /api/config` renvoie `{ "seed_bugs": true|false }`. Le frontend l'utilise pour activer le bug d'interface B12.

> Avertissement : `SEED_BUGS=true` rend volontairement l'application vulnérable et incorrecte (injection SQL, contrôle d'accès cassé, jeton sans expiration). À n'utiliser qu'en environnement de formation jetable, jamais en production.

## Cartographie des bugs

| Code | Anomalie | Module(s) | Type de test |
|------|----------|-----------|--------------|
| B1   | Sur-réservation : le contrôle de stock est ignoré | 2 (SQL), 9 (perf) | Concurrence, charge |
| B2   | Le plafond de 6 billets n'est pas contrôlé côté API | 5 (manuel), 7 (API) | Valeurs limites, API |
| B3   | IDOR : on peut consulter la commande et le billet d'autrui | 9 (sécurité) | Contrôle d'accès |
| B4   | Un code promo expiré est accepté par l'API | 2 (SQL), 7 (API) | Validation métier |
| B5   | Une réservation expirée ne libère pas le stock | 5 (manuel), 11 (flaky) | Temporel, instabilité |
| B7   | Écart d'arrondi entre total commande et montant payé | 2 (SQL), 9 (données) | Réconciliation |
| B9   | Le jeton JWT est émis sans date d'expiration | 9 (sécurité) | Authentification |
| B10  | Recherche d'événements vulnérable à l'injection SQL | 9 (sécurité) | Injection |
| B11  | La réponse du catalogue omet le champ capacity | 9 (JSON Schema) | Contrat / schéma |
| B12  | Le bouton de paiement est parfois inactif | 10 (Playwright) | Automatisation, flaky |

Bugs prévus mais en attente de fonctionnalités dédiées : B6 (tarif early bird encore appliqué après J-30) et B8 (remboursement autorisé à moins de 48 h). Ils seront ajoutés avec les règles RM5 et RM6.

## Détail et reproduction

### B1 — Sur-réservation

- Comportement correct : une commande dont la quantité dépasse le stock disponible est refusée (409).
- Comportement bugué : la commande est acceptée (201) même au-delà de la capacité.
- Reproduction : commander une quantité supérieure aux places restantes d'une catégorie.
- Détection : requête SQL d'agrégation comparant la somme des billets payés à la capacité.
- Emplacement : `backend/app/routers/orders.py`, fonction `create_order` (contrôle RM1).

### B2 — Plafond de 6 billets contournable

- Comportement correct : l'API refuse plus de 6 billets par commande (400).
- Comportement bugué : seule l'interface limite à 6 ; un appel direct à l'API en accepte davantage.
- Reproduction : `POST /api/orders` avec une quantité de 7.
- Emplacement : `create_order` (contrôle RM3).

### B3 — IDOR sur les commandes et billets

- Comportement correct : un utilisateur ne peut lire que ses propres commandes (404 sinon).
- Comportement bugué : n'importe quel utilisateur connecté peut lire la commande et télécharger le billet d'autrui en changeant l'identifiant.
- Reproduction : se connecter avec un compte A, appeler `GET /api/orders/{id}` avec l'identifiant d'une commande du compte B.
- Emplacement : `get_order` et `download_ticket` (contrôle RM7).

### B4 — Code promo expiré accepté

- Comportement correct : un code promo expiré est refusé (400).
- Comportement bugué : l'API applique la réduction malgré l'expiration.
- Reproduction : utiliser le code `EXPIRED` lors d'une commande.
- Emplacement : `_validate_promo`.

### B5 — Stock non libéré après expiration

- Comportement correct : une réservation non payée expire après dix minutes et libère le stock.
- Comportement bugué : les réservations expirées continuent de bloquer le stock.
- Reproduction : créer une réservation, attendre l'expiration, constater que la disponibilité ne remonte pas.
- Emplacement : `backend/app/services.py`, `expire_stale_orders` et `category_sold`.

### B7 — Écart d'arrondi total / paiement

- Comportement correct : le montant payé est égal au total de la commande.
- Comportement bugué : le montant prélevé est recalculé par troncature, créant un écart d'un centime sur certaines remises.
- Reproduction : commander la catégorie « Early bird » avec le code `WELCOME10`, puis comparer `orders.total_cents` et `payments.amount_cents`.
- Détection : `SELECT ... WHERE orders.total_cents <> payments.amount_cents`.
- Emplacement : `pay_order`.

### B9 — JWT sans expiration

- Comportement correct : le jeton contient une date d'expiration (`exp`).
- Comportement bugué : le jeton est émis sans `exp` et reste valable indéfiniment.
- Reproduction : décoder le jeton renvoyé par `POST /api/auth/token` et constater l'absence de `exp`.
- Emplacement : `backend/app/auth.py`, `create_access_token`.

### B10 — Injection SQL dans la recherche

- Comportement correct : la recherche utilise une requête paramétrée et ne renvoie que les événements publiés.
- Comportement bugué : le paramètre `q` est concaténé dans la requête (injectable) et le filtre « publié » saute, exposant les brouillons.
- Reproduction : rechercher avec une charge utile telle que `%' OR title LIKE '%` pour révéler des événements non publiés.
- Emplacement : `backend/app/routers/events.py`, `list_events`.

### B11 — Réponse non conforme au schéma

- Comportement correct : chaque événement du catalogue expose le champ `capacity`.
- Comportement bugué : le champ `capacity` est absent de la réponse de `GET /api/events`.
- Détection : validation de la réponse contre un JSON Schema attendu.
- Emplacement : `list_events`.

### B12 — Bouton de paiement instable

- Comportement correct : le bouton « Payer » déclenche toujours le paiement.
- Comportement bugué : le clic est parfois ignoré, sans message d'erreur.
- Reproduction : sur la page de paiement, cliquer plusieurs fois ; le paiement n'aboutit pas systématiquement.
- Détection : un test d'automatisation naïf devient instable (flaky) ; il faut une stratégie d'attente et de nouvelle tentative robuste.
- Emplacement : `frontend/src/pages/Checkout.jsx`, fonction `pay`.
