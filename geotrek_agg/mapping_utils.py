"""
    Fonctions permettant d'assurer le mapping des listes de valeurs
"""
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError, ProgrammingError
from sqlalchemy import text

def insert_cor_data(DB, db_source, cor_table, fields):
    """
        Insertion des données dans la table geotrekagg_correspondances
    """

    sql_del = f"""
        WITH
            a AS (
            SELECT * FROM public.geotrekagg_correspondances gc
            WHERE NOT EXISTS (
                SELECT * FROM {db_source}.{cor_table} p
                WHERE gc.id_origin = p.id
                )
            AND bdd_source = '{db_source}'
            AND table_origin = '{cor_table}'
            )
        DELETE FROM public.geotrekagg_correspondances gc
        USING a
        WHERE gc.bdd_source = a.bdd_source
        AND gc.table_origin = a.table_origin
        AND gc.id_origin = a.id_origin;

    """

    sql_ins = f"""
        INSERT INTO public.geotrekagg_correspondances
            (bdd_source, table_origin, id_origin, label_origin)
        SELECT  '{db_source}', '{cor_table}', id, "{fields}"
        FROM {db_source}.{cor_table}
        ON CONFLICT ON CONSTRAINT geotrekagg_correspondances_bdd_source_table_origin_id_origi_key
        DO UPDATE
        SET label_origin = excluded.label_origin;
    """
    sql = sql_del + sql_ins

    try:
        DB.session.execute(
            sql.format(
                db_source=db_source,
                cor_table=cor_table,
                label=fields
                )
            )
        DB.session.commit()
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
        WHERE c.table_origin = '{cor_table}' AND unaccent(i.{label}) ilike unaccent(c.label_origin);
    """
    try:
        DB.session.execute(
            sql.format(
                cor_table=cor_table,
                label=fields
                )
            )
        DB.session.commit()
    except SQLAlchemyError as e:
        current_app.logger.error(str(e.orig))
    except Exception as e:
        current_app.logger.error(str(e))

