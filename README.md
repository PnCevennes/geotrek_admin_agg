# geotrek_admin_agg

Pour le fonctionnement d'une agrégation, des étapes nécessaires sont décrites dans `/scripts/aggregator_preparation.sql` (création des uuids si non présents dans les bdd source, création des FDW, etc.).
 

# Prérequis

## Base de données d' aggrégation 
Installer les extensions suivantes en mode administrateur

```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgres_fdw;
```

Exécuter le script sql `/scripts/aggregator_preparation_dbmaster.sql` 
Ce fichier comprend toutes les requêtes nécessaires aux étapes de préparation des bases de données présentées ci-dessous.

## Préparation des bases filles de données source
Installer l'extension suivante en mode administrateur

```
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

Exécuter le script sql `/scripts/aggregator_preparation_dbsource.sql` 

# Descriptions scripts de préparation
## Préparation base de données source

Les tables
- `core_topology`
- `common_attachment`
- `tourism_informationdesk`
- `tourism_touristiccontent`
- `tourism_touristicevent`
- `feedback_report`
- `trekking_trek`
- `trekking_poi`
- `trekking_weblink`
- `signage_signage`
- `signage_blade`
- `signage_line`

doivent avoir un champ `uuid` renseigné.

## Préparation base de données destination (aggregator)

Les fonctions `geotrekagg_get_foreign_key()` et `geotrekagg_get_id_correspondance()` doivent être créées. Les mêmes tables que ci-dessus doivent avoir un champ `uuid`.
Les tables catégorielles
- `trekking_weblinkcategory`
- `feedback_reportstatus`
- `trekking_difficultylevel`
- `common_theme`
- `common_recordsource`
- `tourism_touristiceventtype`
- `trekking_practice`
- `feedback_reportactivity`
- `trekking_accessibility`
- `common_reservationsystem`
- `tourism_informationdesktype`
- `trekking_treknetwork`
- `common_label`
- `trekking_route`
- `authent_structure`
- `common_targetportal`
- `trekking_poitype`
- `feedback_reportproblemmagnitude`
- `feedback_reportcategory`
- `tourism_touristiccontentcategory`
- `common_filetype`

doivent être renseignées avec l'ensemble des catégories voulues (combinaison manuelle des catégories de toutes les bases de données sources).

# Installation

```
pip install flask flask-sqlalchemy psycopg2
cd web/static && npm ci
```


# Usage

```
export FLASK_APP=geotrek_agg/app
flask *commande*    # lance une des commandes définies dans geotrek_agg/commands.py
```
```
flask create_functions  # crée les fonctions SQL geotrekagg_get_id_correspondance() et geotrekagg_get_foreign_key()
flask create_db_schema  # crée les tables geotrekagg_source et geotrekagg_correspondances
flask add_source    # crée un foreign data wrapper et un schéma, complète la table geotrekagg_source
flask import_mapping    # remplit la table geotrekagg_correspondances et propose un mapping automatique
flask populate_gta  # retourne les commandes sql d'insertion en base
```


# TODO import des données
CONCEPTION :
- use marshmallow for object definition

Fonctionnalités:
- plus plein de trucs
