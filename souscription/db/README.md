# Base de données PostgreSQL — Validation souscription

Base PostgreSQL du projet de **validation des documents de souscription**, via Docker
(même principe que la base Oracle des réclamations).

## Démarrer la base
```bash
cd db
docker compose up -d
```
Attends ~10 s (le 1er démarrage crée les tables via `init/01_schema.sql`).

## Se connecter dans DBeaver
Nouvelle connexion → **PostgreSQL** :

| Paramètre | Valeur |
|-----------|--------|
| Host      | `localhost` |
| Port      | `5432` |
| Database  | `souscription` |
| Username  | `souscription` |
| Password  | `souscription` |

## Les tables
- `inscriptions` — un dossier soumis par un opérateur
- `gerants` — les gérants (nom + CIN)
- `documents` — les fichiers téléversés
- `rapports_validation` — le résultat de la validation

## Commandes utiles
```bash
docker compose stop      # arrêter (les données restent)
docker compose start     # redémarrer
docker compose down      # arrêter + supprimer le conteneur (données gardées)
docker compose down -v   # tout supprimer (pour rejouer init/)
```

## Se connecter en ligne de commande
```bash
docker exec -it souscription-postgres psql -U souscription -d souscription
```
