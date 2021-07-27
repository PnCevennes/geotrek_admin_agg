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
@click.option('-u', '--user', 'user', required=True, type=str)
@click.option('-d', '--db_name', 'db_name', required=True, type=str)
@click.option('-p', '--password', 'password', required=True, type=str)
@click.option('-o', '--overwrite', 'overwrite', is_flag=True)
@with_appcontext
def add_source(name, host, port, db_name,  user, password, overwrite):
    """
        Création d'une source pour l'aggrégateur

        Args:
            name ([string]): nom de la source
            host ([string]): hote de la base geotrek
            port ([int]): port de postgresql de l'hote
            user ([string]): utilisateur (ayant des droits de lecture sur la base)
            password ([string]): mot de passe de l'utilisateur
    """
    from geotrek_agg.app import DB
    from geotrek_agg.models import GeotrekAggSources
    from geotrek_agg.utils import create_fdw_server, get_source

    # Test if source exists
    source = get_source(DB, name)
    if source and not overwrite:
        current_app.logger.error(f"La source {name} existe déjà. Pour la redéfinir utiliser l'option -o (overwrite)")
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
        click.echo(f"Création du foreign data wrapper")
    except Exception as e:
        current_app.logger.error("Umpossible de créer le fdw", e.orig)
        exit()

    # Création d'une entrée dans la table des sources
    if not source:
        source = GeotrekAggSources(bdd_source=name)
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
    for ct in COR_TABLE:
        click.echo(f"Import table {ct}")
        if insert_cor_data(DB, name, ct, COR_TABLE[ct]['label_field']):
            auto_mapping(DB, ct, COR_TABLE[ct]['label_field'])
            click.echo(click.style('Done', fg='green'))
        else:
            click.echo(click.style('Table not found', fg='red'))


@click.command("populate_gta")
@with_appcontext
def populate_gta():
    from geotrek_agg.app import DB
    from .import_content.sql import queries
    source = "pne"
    for query in queries:
        DB.engine.execute(query.format(source=source))
        print('Insertion données effectuée')
