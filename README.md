# geotrek_admin_agg

Pour le fonctionnement d'une agrégation, des étapes nécessaires sont décrites dans '/geotrek_agg/import_content/aggregator_preparation' (création des uuids si non présents dans les bdd source, création des FDW, etc.).

'aggregator_donnees.sql' est juste le script issu du SGBD qui permet l'insertion des données non catégorielles (treks, pois, touristicevent, etc.), son contenu va être transféré dans 'sql.py'


# Usage

```
export FLASk_APP=app
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
- + pleins de trucs

Documentation
