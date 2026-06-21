# eventflow

> Plateforme de billetterie événementielle — support pédagogique (fil rouge) de la formation Testeur QA.

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

eventflow est une application web réaliste à trois tiers (React, FastAPI, PostgreSQL) qui permet à des organisateurs de mettre en vente des billets pour leurs événements, et au public de réserver et payer en ligne. Elle sert de fil rouge à la formation Testeur QA : les stagiaires l'explorent, la testent et l'industrialisent tout au long du programme, du test manuel jusqu'à la chaîne CI/CD.

La version actuelle implémente le comportement attendu. Les bugs intentionnels du fil rouge (B1 à B12) seront ajoutés ensuite, activables via une variable d'environnement, afin de servir les exercices de chaque module.

## Sommaire

- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Stack technique](#stack-technique)
- [Prérequis](#prérequis)
- [Démarrage rapide (Docker)](#démarrage-rapide-docker)
- [Démarrage manuel](#démarrage-manuel)
- [Configuration](#configuration)
- [Données de démonstration](#données-de-démonstration)
- [Référence de l'API](#référence-de-lapi)
- [Parcours fonctionnel](#parcours-fonctionnel)
- [Règles métier](#règles-métier)
- [Modèle de données](#modèle-de-données)
- [Charte graphique](#charte-graphique)
- [Contexte pédagogique](#contexte-pédagogique)
- [Structure du dépôt](#structure-du-dépôt)
- [Dépannage](#dépannage)
- [Feuille de route](#feuille-de-route)
- [Licence](#licence)

## Fonctionnalités

Côté public :

- Catalogue d'événements avec recherche par mot-clé et filtre par ville.
- Compte client : inscription, connexion par OAuth2 / JWT, profil.
- Tunnel de réservation : sélection des places, réservation temporaire de dix minutes, paiement, confirmation.
- Codes promo et catégories tarifaires (early bird, plein tarif, VIP).
- Espace « Mes billets » et billet téléchargeable au format PDF avec QR code.
- Profil utilisateur : photo (avatar), modification des informations et changement de mot de passe.

Côté back-office (rôles `organizer` et `admin`) :

- Tableau de bord des ventes : nombre d'événements, billets vendus, chiffre d'affaires.
- Gestion des événements : création, modification, publication, ajout de catégories.
- Suivi des commandes et des participants par événement.
- Gestion des codes promo : création, suivi d'utilisation, désactivation.

## Architecture

L'application expose les trois surfaces que les stagiaires apprennent à tester : une base de données relationnelle, une API REST authentifiée, et des interfaces web.

```
Navigateur  ──HTTP──>  Frontend React (Vite, port 5173)
                              │  proxy /api
                              ▼
                       API FastAPI (port 8000)  ──SQLAlchemy──>  PostgreSQL (port 5432)
```

Le frontend appelle l'API via un proxy `/api` (configuré dans `vite.config.js`), ce qui évite tout problème de CORS en développement.

## Stack technique

| Couche          | Technologies                                                        |
|-----------------|---------------------------------------------------------------------|
| Base de données | PostgreSQL 16                                                       |
| API             | FastAPI, SQLAlchemy 2, Pydantic 2, OAuth2 / JWT (python-jose), bcrypt |
| Billet PDF      | reportlab, qrcode                                                   |
| Frontend        | React 19, Vite 8, React Router 8, axios                            |
| Design          | Clash Display, Inter, FontAwesome                                  |
| Conteneurisation | Docker, Docker Compose                                             |

## Prérequis

- Docker et Docker Compose (méthode recommandée), ou
- Python 3.12 et Node.js 22 pour un démarrage manuel.

## Démarrage rapide (Docker)

À la racine du projet :

```bash
docker compose up --build
```

Services disponibles :

| Service     | URL                              |
|-------------|----------------------------------|
| Frontend    | http://localhost:5173            |
| API         | http://localhost:8000            |
| Documentation Swagger | http://localhost:8000/docs |
| PostgreSQL  | localhost:5432 (`eventflow` / `eventflow`) |

Au premier lancement, le backend crée les tables et injecte les données de démonstration. Le code (`backend/app` et `frontend/src`) est monté en volume : les modifications sont rechargées à chaud (uvicorn `--reload` et HMR Vite). Une reconstruction n'est nécessaire que lorsque les dépendances changent :

```bash
docker compose up --build backend
```

## Démarrage manuel

Backend (nécessite un PostgreSQL accessible, ou adapter `DATABASE_URL`) :

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python -m app.seed               # crée les tables et les données de démo
uvicorn app.main:app --reload
```

Frontend :

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Le backend se configure par variables d'environnement (voir `backend/.env.example`).

| Variable               | Défaut                                                            | Description                                    |
|------------------------|------------------------------------------------------------------|------------------------------------------------|
| `DATABASE_URL`         | `postgresql+psycopg2://eventflow:eventflow@db:5432/eventflow`     | Chaîne de connexion SQLAlchemy                 |
| `JWT_SECRET`           | `dev-secret-change-me`                                            | Secret de signature des jetons JWT             |
| `ACCESS_TOKEN_MINUTES` | `120`                                                            | Durée de validité d'un jeton                   |
| `RESERVATION_MINUTES`  | `10`                                                             | Durée d'une réservation avant expiration       |
| `SEED_BUGS`            | `false`                                                          | Active les bugs pédagogiques du fil rouge      |
| `CORS_ORIGINS`         | `http://localhost:5173`                                          | Origines autorisées (séparées par des virgules) |

En production, `JWT_SECRET` doit impérativement être remplacé par une valeur secrète et aléatoire.

## Données de démonstration

Comptes créés par le seed :

| Rôle           | Email                    | Mot de passe |
|----------------|--------------------------|--------------|
| Administrateur | admin@eventflow.test     | admin1234    |
| Organisateur   | orga@eventflow.test      | orga1234     |
| Client         | client@eventflow.test    | client1234   |

Codes promo :

| Code        | Réduction | Remarque                |
|-------------|-----------|-------------------------|
| `WELCOME10` | 10 %      | Valide                  |
| `VIP25`     | 25 %      | Valide                  |
| `EXPIRED`   | 15 %      | Expiré (utile aux tests) |

Cartes de paiement simulées (page de paiement) :

| Numéro                 | Résultat        |
|------------------------|-----------------|
| `4242 4242 4242 4242`  | Paiement accepté |
| `4000 0000 0000 0002`  | Paiement refusé  |

La date d'expiration (future) et le CVC sont libres. Aucune donnée de carte n'est stockée : il s'agit d'une simulation.

## Référence de l'API

Base : `http://localhost:8000`. Documentation interactive : `/docs`.

Authentification :

| Méthode | Route                  | Accès    | Description                       |
|---------|------------------------|----------|-----------------------------------|
| POST    | `/api/auth/register`        | Public   | Créer un compte                   |
| POST    | `/api/auth/token`           | Public   | Connexion (OAuth2, renvoie un JWT) |
| GET     | `/api/auth/me`              | Connecté | Profil de l'utilisateur courant   |
| PATCH   | `/api/auth/me`              | Connecté | Modifier ses informations (nom, téléphone) |
| POST    | `/api/auth/me/avatar`       | Connecté | Définir la photo de profil        |
| DELETE  | `/api/auth/me/avatar`       | Connecté | Retirer la photo de profil        |
| POST    | `/api/auth/change-password` | Connecté | Changer son mot de passe          |

Catalogue et réservations :

| Méthode | Route                       | Accès    | Description                          |
|---------|-----------------------------|----------|--------------------------------------|
| GET     | `/api/events`               | Public   | Catalogue (filtres `q`, `city`)      |
| GET     | `/api/events/{id}`          | Public   | Détail et disponibilité par catégorie |
| POST    | `/api/orders`               | Connecté | Créer une réservation (dix minutes)  |
| GET     | `/api/orders/me`            | Connecté | Mes commandes                        |
| GET     | `/api/orders/{id}`          | Connecté | Détail d'une commande (propriétaire) |
| POST    | `/api/orders/{id}/pay`      | Connecté | Payer une réservation                |
| GET     | `/api/orders/{id}/ticket`   | Connecté | Billet PDF avec QR code              |

Back-office (rôles `organizer` ou `admin`, sinon 403) :

| Méthode  | Route                                  | Description                       |
|----------|----------------------------------------|-----------------------------------|
| GET      | `/api/admin/summary`                   | Totaux (événements, ventes, CA)   |
| GET      | `/api/admin/events`                    | Liste avec ventes et remplissage  |
| POST     | `/api/admin/events`                    | Créer un événement et ses catégories |
| GET      | `/api/admin/events/{id}`               | Statistiques détaillées           |
| PUT      | `/api/admin/events/{id}`               | Modifier un événement             |
| POST     | `/api/admin/events/{id}/categories`    | Ajouter une catégorie de billets  |
| GET      | `/api/admin/events/{id}/orders`        | Commandes et participants         |
| GET, POST | `/api/admin/promo`                    | Lister, créer un code promo       |
| PUT      | `/api/admin/promo/{id}`                | Modifier un code promo            |
| POST     | `/api/admin/promo/{id}/disable`        | Désactiver un code promo          |

## Parcours fonctionnel

1. Le client s'authentifie.
2. Il choisit un événement et une catégorie tarifaire.
3. Il sélectionne de un à six billets ; une réservation temporaire bloque le stock pendant dix minutes.
4. Il applique éventuellement un code promo.
5. Il paie via la page de paiement simulée ; le paiement valide la commande et décrémente définitivement le stock.
6. Il reçoit une confirmation et peut télécharger son billet PDF. Si la réservation expire avant le paiement, le stock est libéré.

## Règles métier

| Code | Règle                                                                       |
|------|-----------------------------------------------------------------------------|
| RM1  | Le nombre de places vendues ne dépasse jamais la capacité disponible.       |
| RM2  | Une réservation non payée expire après dix minutes et libère le stock.      |
| RM3  | Maximum six billets par commande.                                           |
| RM4  | Un code promo a un nombre d'usages maximum et une date d'expiration.        |
| RM7  | Un client ne peut consulter que ses propres commandes et billets.           |

Les règles RM5 (tarif early bird limité) et RM6 (remboursement jusqu'à 48 h avant l'événement) seront ajoutées dans les itérations suivantes.

## Modèle de données

Le schéma relationnel de référence est disponible dans `db/schema.sql` (il sert au module SQL). Les tables sont également créées automatiquement par SQLAlchemy au démarrage.

| Table               | Rôle                                                       |
|---------------------|------------------------------------------------------------|
| `users`             | Comptes, rôles (`client`, `organizer`, `admin`), profil (téléphone, avatar) |
| `events`            | Événements (titre, ville, date, capacité, statut)          |
| `ticket_categories` | Catégories tarifaires d'un événement (prix, quota)         |
| `orders`            | Commandes (statut, total, expiration)                      |
| `order_items`       | Lignes de commande (catégorie, quantité, prix unitaire)    |
| `payments`          | Paiements associés aux commandes                           |
| `promo_codes`       | Codes promo (réduction, usages, expiration)                |
| `refunds`           | Remboursements                                             |

## Charte graphique

| Couleur | Code      | Usage                         |
|---------|-----------|-------------------------------|
| Ink     | `#15131E` | Texte, surfaces sombres       |
| Flux    | `#6C4DF6` | Couleur primaire, actions     |
| Spark   | `#FF5B4A` | Accent                        |
| Mint    | `#1FD6A6` | Succès, disponibilité         |
| Paper   | `#F6F5F2` | Fond d'application            |

Typographie : Clash Display (titres) et Inter (interface). Iconographie : FontAwesome, sans emoji. Les fichiers de marque (logo, brand board) se trouvent dans le dossier `brand/`.

## Contexte pédagogique

eventflow est le fil rouge de la formation Testeur QA. Le même produit est testé sous des angles de plus en plus techniques, module après module : SQL de validation, test manuel, gestion de campagne, test d'API, sécurité, performance, automatisation UI et CI/CD.

La variable `SEED_BUGS` (désactivée par défaut) injecte des anomalies intentionnelles, chacune rattachée au module qui la révèle. Le comportement correct sert de référence ; `SEED_BUGS=true` bascule l'application en mode bugué.

```bash
SEED_BUGS=true docker compose up --build backend
```

Bugs déjà disponibles : B1 (sur-réservation), B2 (plafond de billets contournable), B3 (IDOR), B4 (code promo expiré accepté), B5 (stock non libéré), B7 (écart d'arrondi), B9 (JWT sans expiration), B10 (injection SQL), B11 (réponse non conforme), B12 (bouton de paiement instable). Le détail et la reproduction de chacun se trouvent dans `docs/FIL_ROUGE_BUGS.md`. L'endpoint `GET /api/config` expose l'état du mode bug.

## Structure du dépôt

```
eventflow/
├── backend/                  API FastAPI
│   ├── app/
│   │   ├── main.py           point d'entrée et configuration
│   │   ├── config.py         variables d'environnement
│   │   ├── database.py       moteur et session SQLAlchemy
│   │   ├── models.py         tables ORM
│   │   ├── schemas.py        schémas Pydantic
│   │   ├── auth.py           hachage, JWT, contrôle de rôle
│   │   ├── services.py       règles métier (disponibilité, expiration)
│   │   ├── ticket_pdf.py     génération du billet PDF avec QR
│   │   ├── seed.py           données de démonstration
│   │   └── routers/          auth, events, orders, admin
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 SPA React (Vite)
│   ├── src/
│   │   ├── pages/            Catalog, EventDetail, Checkout, Confirmation, Login, MyTickets, Profile
│   │   ├── pages/admin/      Dashboard, EventForm, EventManage, Promos
│   │   ├── components/       NavBar, EventCard, Logo, Avatar
│   │   ├── api.js            client axios et utilitaires
│   │   ├── auth.jsx          contexte d'authentification
│   │   └── theme.css         design system eventflow
│   ├── Dockerfile
│   └── vite.config.js
├── db/
│   └── schema.sql            schéma relationnel de référence
├── docker-compose.yml
└── README.md
```

## Dépannage

Connexion impossible avec une erreur 500 mentionnant un email invalide : les adresses en `.test` sont des domaines réservés. Les schémas de sortie ne valident pas strictement l'email pour cette raison ; conservez ce point en tête si vous renforcez la validation.

Réservation affichée comme « expirée » dès la page de paiement : signe d'une date interprétée dans le mauvais fuseau. L'API renvoie des dates en UTC explicite (suffixe `Z`) et le frontend les parse comme UTC. Conservez ce contrat si vous ajoutez des dates.

Colonnes de profil (`phone`, `avatar`) absentes sur une base ancienne : le backend les ajoute automatiquement au démarrage via une migration idempotente (`ALTER TABLE ... ADD COLUMN`). Un redémarrage du 