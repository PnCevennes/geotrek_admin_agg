# geotrek_admin_agg

Pour le fonctionnement d'une agrégation, des étapes nécessaires sont décrites dans '/geotrek_agg/import_content/aggregator_preparation' (création des uuids si non présents dans les bdd source, création des FDW, etc.).

'aggregator_donnees.sql' est juste le script issu du SGBD qui permet l'insertion des données non catégorielles (treks, pois, touristicevent, etc.), son contenu va être transféré dans 'sql.py'

# Prérequis

```
pip install flask
pip install flask-sqlalchemy
pip install psycopg2
```

## Base de données source
Ses tables `core_topology`, `common_attachment`, `tourism_informationdesk`, `tourism_touristiccontent`, `tourism_touristicevent`, `feedback_report`, `trekking_trek`, `trekking_poi` ont un champ `uuid`. La requête SQL de création de ces champs et de génération des uuids est disponible dans `geotrek_agg/import_content/aggregator_preparation.sql`.

## Base de données destination (aggregator)
Un Foreign Data Wrapper de la (ou les) base de données source doit y être créé, afin d'importer les données de cette dernière dans un schéma. Les requêtes sont disponibles dans `geotrek_agg/import_content/aggregator_preparation.sql`.

# Usage

```
export FLASK_APP=geotrek_agg/app
flask *commande* # lance une des commandes définies dans geotrek_agg/commands.py
```
```
flask create_db_schema # crée les tables geotrekagg_source et geotrekagg_correspondances
flask populate_gta # retourne les commandes sql d'insertion en base
```


# TODO import des données
CONCEPTION :
- use marshmallow for object definition

Fonctionnalités:
- gestion des tables de types trekking_trekrelationship
               => faisable avec foreign_keys en théorie
- deletion en cascade pour les tables de correlation
- ajouter option source de la données dans commandes
- plus plein de trucs

Documentation
