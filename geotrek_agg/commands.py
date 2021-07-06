import click
from flask import current_app
from flask.cli import with_appcontext

from geotrek_agg.env import COR_TABLE

@click.command("create_db_schema") 
@with_appcontext
def create_db_schema(): 
    from geotrek_agg.app import DB
    from geotrek_agg.models import CommonCorrespondances
    DB.create_all()


@click.command("import_mapping") 
@with_appcontext
def import_mapping(): 
    from geotrek_agg.app import DB
    for c in COR_TABLE:
        print(f"Import table {c}")
        insert_cor_data(DB, 'pne', c, COR_TABLE[c]['label_field'])
        auto_mapping(DB, 'pne', c, COR_TABLE[c]['label_field'])



def insert_cor_data(DB, db_source, cor_table, fields):

    sql = """
        INSERT INTO public.geotrekagg_correspondances
            (bdd_source, table_origin, id_origin, label_origin)
        SELECT  '{db_source}', '{cor_table}', id, {label} FROM {db_source}.{cor_table}
    """
    try:
        DB.engine.execute(sql.format(db_source=db_source, cor_table=cor_table, label=fields))
    except Exception as e:
        print(e)


def auto_mapping(DB, db_source, cor_table, fields):

    sql = """
        UPDATE public.geotrekagg_correspondances c SET id_destination = i.id
        FROM public.{cor_table} i
        WHERE c.table_origin = '{cor_table}' AND i.{label} = c.label_origin;
    """
    try:
        DB.engine.execute(sql.format(cor_table=cor_table, label=fields))
    except Exception as e:
        print(e)