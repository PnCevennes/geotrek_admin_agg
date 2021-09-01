import click
from flask import current_app
from flask.cli import with_appcontext
from sqlalchemy.orm import Session

from geotrek_agg.env import CAT_TABLE


@click.command("create_db_schema")
@with_appcontext
def create_db_schema():
    from geotrek_agg.app import DB
    click.echo("Generate DB structure")
    DB.drop_all()
    DB.create_all()


@click.command("add_source")
@click.option('-n', '--name', 'name', required=True, type=str)
@click.option('-h', '--host', 'host', required=True, type=str)
@click.option('-p', '--port', 'port', type=int, default=5432, show_default=True)
@click.option('-d', '--db_name', 'db_name', required=True, type=str)
@click.option('-U', '--user', 'user', required=True, type=str)
@click.option('-P', '--password', 'password', required=True, type=str)
@click.option('-u', '--url', 'url', required=True, type=str)
@click.option('-o', '--overwrite', 'overwrite', is_flag=True)
@with_appcontext
def add_source(name, host, port, db_name, user, password, overwrite, url):
    """
        Création d'une source pour l'aggrégateur

        Args:
            name ([string]): nom de la source
            host ([string]): hote de la base geotrek
            port ([int]): port de postgresql de l'hote
            db_name([string]): nom de la base de données
            user ([string]): utilisateur (ayant des droits de lecture sur la base)
            password ([string]): mot de passe de l'utilisateur
            url ([string]): url de la source (Geotrek-admin)
            overwrite ([]): écraser la source si déjà existante
    """
    from geotrek_agg.app import DB
    from geotrek_agg.models import GeotrekAggSources
    from geotrek_agg.utils import create_fdw_server, get_source

    # Test if source exists
    source = get_source(DB, name)
    if source and not overwrite:
        current_app.logger.info(f"La source {name} existe déjà. Pour la redéfinir utiliser l'option -o")
        exit()

    # Création du FDW
    try:
        create_fdw_server(
            DB=DB,
            name=name,
            host=host,
            port=port,
            db_name=db_name,
            user=user,
            password=password
        )
        click.echo(click.style(f"Foreign data wrapper créé", fg='green'))
    except Exception as e:
        current_app.logger.error("Impossible de créer le fdw", e.orig)
        exit()

    # Création d'une entrée dans la table des sources
    if not source:
        source = GeotrekAggSources(bdd_source=name, url=url)
        DB.session.add(source)
        try:
            DB.session.commit()
            click.echo(f"Création de la source dans la table GeotrekAggSources")
        except Exception as e:
            DB.session.rollback()
            current_app.logger.error("Impossible de créer bdd_source", str(e))



@click.command("import_mapping")
@click.argument("name")
@with_appcontext
def import_mapping(name):
    """
        Import des données des tables de vocabulaires
        dans la table geotrekagg_correspondances

        Args:
            name (string): nom de la source
    """
    from geotrek_agg.app import DB
    from geotrek_agg.mapping_utils import insert_cor_data, auto_mapping
    from geotrek_agg.utils import get_source
    # Test if source exists
    source = get_source(DB, name)
    if not source:
        current_app.logger.info(f"La source {name} n'existe pas.")
        exit()
    for c in CAT_TABLE:
        click.echo(f"Import table {c}")
        if insert_cor_data(DB, name, c, CAT_TABLE[c]['label_field']):
            auto_mapping(DB,  c, CAT_TABLE[c]['label_field'])
            click.echo(click.style('Done', fg='green'))
        else:
            click.echo(click.style('Table not found', fg='red'))

@click.command("populate_gta")
@click.argument("name")
@with_appcontext
def populate_gta(name):
    """
        Insertion des données dans la BDD destination

        Args:
            name (string): nom de la source
    """
    from geotrek_agg.app import DB
    from .import_content.sql import queries
    from geotrek_agg.env import IMPORT_MODEL
    from geotrek_agg.mapping_object import MappingObject
    from sqlalchemy import text

    source = name
    # TODO TEST_BEFORE_IMPORT FIRST

    sql_d = {}
    sql_i = {}

    # Alimentation du dictionnaire sql_d table par table
    # (dans l'ordre inverse de l'insertion)
    for table in reversed(IMPORT_MODEL):
        table_object = MappingObject(
            DB=DB,
            data_source=source,
            table_name=table,
            table_def=IMPORT_MODEL[table]
        )
        sql_d[table] = table_object.generate_sql_delete()

    # Alimentation du dictionnaire sql_i table par table
    for table in IMPORT_MODEL:
        table_object = MappingObject(
            DB=DB,
            data_source=source,
            table_name=table,
            table_def=IMPORT_MODEL[table]
        )
        sql_i[table] = table_object.generate_sql_insert()

    # Essai d'exécution des requêtes, puis commit de celles-ci en cas de succès
    try:
        DB.session.execute(f"""
            ALTER TABLE core_topology DISABLE TRIGGER core_topology_latest_updated_d_tgr;

            DELETE FROM common_attachment p
            USING {name}.common_attachment s
            WHERE s.uuid = p.uuid;
        """)
        for key, value in sql_d.items():
            click.echo(f" -- Deleting table {key}...")
            DB.session.execute(value)
            click.echo(f" -- {key} data deleted!\n")
        for key, value in sql_i.items():
            click.echo(f" -- Importing table {key}...")
            DB.session.execute(value)
            click.echo(f" -- {key} data inserted!\n")
        DB.session.execute("""
            UPDATE core_topology SET date_update = NOW()
            WHERE id IN (SELECT id FROM core_topology ORDER BY date_update DESC LIMIT 1);

            ALTER TABLE core_topology ENABLE TRIGGER core_topology_latest_updated_d_tgr;
        """)
        DB.session.commit()
        click.echo(click.style('Transaction committed', fg='green'))
    except Exception as e:

        click.echo(f"{e.orig}...")
        exit()


# Fonction en doublons avec le script de préparation.
#   a voir si pertinent car peut lisible par rapport à un script sql classique

@click.command("create_functions")
@with_appcontext
def create_functions():
    from geotrek_agg.app import DB
    from sqlalchemy import text
    click.echo("Création des fonctions...")
    sql = f"""
        -------FONCTION D'OBTENTION DU NOUVEL ID D'UNE CATEGORIE
        CREATE OR REPLACE FUNCTION public.geotrekagg_get_category_id(
            _initial_id integer,
            _table_origin character varying,
            _db_source character varying
        )
        RETURNS integer
        LANGUAGE plpgsql
        AS $function$
        BEGIN
            RETURN  (
                SELECT id_destination
             FROM geotrekagg_correspondances gc
             WHERE
                    id_origin = _initial_id
                    AND table_origin = _table_origin
                    AND bdd_source = _db_source
            );
        END;
        $function$;

        --------FONCTION D'OBTENTION DE L'ID DE LA CLEF ETRANGERE
        CREATE OR REPLACE FUNCTION public.geotrekagg_get_foreign_key(
            _filter_value varchar, -- Valeur pour filtrer et retrouver la donnée

            _table_origin character varying,  -- TABLE SOURCE de la donnée
            _table_reference character varying, -- TABLE de jointure

            _col_origin character varying, -- Colonne de la TABLE source
            _col_reference character varying, -- Colonne de la TABLE de jointure

            _db_source character VARYING -- nom de la SOURCE
        )
         RETURNS integer
         LANGUAGE plpgsql
        AS $function$
        DECLARE
            _txt_sql TEXT;
            _new_id int;
        BEGIN

            _txt_sql := '
            SELECT DISTINCT  ct."' ||_col_reference || '"
            FROM '|| _db_source ||'."' || _table_origin || '"  p
            JOIN '|| _db_source ||'."' || _table_reference || '" t
            ON t."' ||_col_reference || '" = p."' ||_col_origin || '"
            JOIN "' || _table_reference || '" ct
            ON t.uuid = ct.uuid
            WHERE p."' ||_col_origin || '"::varchar = ''' || _filter_value || '''
            ';

            --RAISE NOTICE '%%', _txt_sql;
            EXECUTE _txt_sql into _new_id;

            RETURN _new_id;
        END;
        $function$;
    """
    DB.session.execute(sql)
    DB.session.commit()
    click.echo(click.style("Fonctions créées", fg='green'))
