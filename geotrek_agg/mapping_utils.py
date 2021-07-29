"""
    Fonctions permettant d'assurer le mapping des listes de valeurs
"""
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError

def insert_cor_data(DB, db_source, cor_table, fields):
    """
        Insertion des données dans la table geotrekagg_correspondances
    """

    sql = """
        INSERT INTO public.geotrekagg_correspondances
            (bdd_source, table_origin, id_origin, label_origin)
        SELECT  '{db_source}', '{cor_table}', id, {label} FROM {db_source}.{cor_table}
        ON CONFLICT ON CONSTRAINT geotrekagg_correspondances_bdd_source_table_origin_id_origi_key DO NOTHING
    """

    try:
        DB.engine.execute(
            sql.format(db_source=db_source, cor_table=cor_table, label=fields)
        )
        return True
    except ProgrammingError as e:
        if e.code == 'f405':
            return False
    except SQLAlchemyError as e:
        current_app.logger.error(str(e.orig))
    except Exception as e:
        current_app.logger.error(str(e))


def auto_mapping(DB, cor_table, fields):
    """
        mapping automatique des nomenclatures
         dans la table geotrekagg_correspondances
    """

    sql = """
        UPDATE public.geotrekagg_correspondances c SET id_destination = i.id
        FROM public.{cor_table} i
        WHERE c.table_origin = '{cor_table}' AND i.{label} = c.label_origin;
    """
    try:
        DB.engine.execute(sql.format(cor_table=cor_table, label=fields))
    except SQLAlchemyError as e:
        current_app.logger.error(str(e.orig))
    except Exception as e:
        current_app.logger.error(str(e))

