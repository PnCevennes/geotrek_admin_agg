import click
from flask import current_app
from flask.cli import with_appcontext

from geotrek_agg.env import COR_TABLE


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
@click.option('-p', '--password', 'password', required=True, type=str)
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

    # Test if source exists
    source = get_source(DB, name)
    if source and not overwrite:
        current_app.logger.error(f"La source {name} existe déjà. Pour la redéfinir utiliser l'option -o (overwrite)")
        exit()


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
    for c in COR_TABLE:
        click.echo(f"Import table {c}")
        if insert_cor_data(DB, 'pne', c, COR_TABLE[c]['label_field']):
            auto_mapping(DB,  c, COR_TABLE[c]['label_field'])
            click.echo(click.style('Done', fg='green'))
        else:
            click.echo(click.style('Table not found', fg='red'))

@click.command("populate_gta")
@with_appcontext
def populate_gta():
    from geotrek_agg.app import DB
    from .import_content.sql import queries
    from geotrek_agg.env import IMPORT_MODEL
    from geotrek_agg.mapping_object import MappingObject
    source = "pne"
    # TODO TEST_BEFORE_IMPORT FIRST

    # TODO clean source

    # Import des données table par table
    for table in IMPORT_MODEL:
        print(f" -- Import table {table}")
        table_object = MappingObject(
            DB=DB,
            data_source=source,
            table_name=table,
            table_def=IMPORT_MODEL[table]
        )
        try:
            sql_d = table_object.generate_sql_delete()
            print(sql_d)
            sql_i = table_object.generate_sql_insert()
            print(sql_i)
        except Exception as e:
            print('Erreur', e)
            raise(e)
            exit


@click.command("create_functions")
@with_appcontext
def create_functions():
    from geotrek_agg.app import DB
    from sqlalchemy import text
    click.echo("Création des fonctions...")
    sql = f"""
        -------FONCTION D'OBTENTION DU NOUVEL ID D'UNE CATEGORIE
        CREATE OR REPLACE FUNCTION public.geotrekagg_get_id_correspondance(
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
    DB.engine.execute(text(sql).execution_options(autocommit=True))
    click.echo("Fait")
