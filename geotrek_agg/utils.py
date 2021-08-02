import click
from geotrek_agg.env import COR_TABLE
from geotrek_agg.models import GeotrekAggCorrespondances, GeotrekAggSources
from sqlalchemy.orm.exc import NoResultFound


def get_all_cor_data(DB):
    """
        Récupération de l'ensemble des données de type "nomenclature"

    Args:
        DB ([type]): [description]

    Returns:
        [type]: [description]
    """
    sql = []
    for c in COR_TABLE:
        sql.append(
            "SELECT  '{cor_table}' as table_source, id, {label} as label FROM public.{cor_table}".format(
                cor_table=c, label=COR_TABLE[c]['label_field']
            )
        )
    query = ' UNION '.join(sql)
    try:
        data = DB.session.connection().execute(query)
    except Exception:
        return []
    return data


def get_structured_cor_data(DB):
    """
       Récupération et mise en forme de l'ensemble des données
       de geotrekagg_correspondances

    Args:
        DB ([type]): [description]

    Returns:
        [type]: [description]
    """
    voc_data = get_all_cor_data(DB)
    structured_voc_data = {}
    for voc in voc_data:
        if not voc[0] in structured_voc_data:
            structured_voc_data[voc[0]] = {}
        structured_voc_data[voc[0]][voc[1]] = voc[2]
    return structured_voc_data


def get_mapping_el(DB, id):
    """
        Récupération d'un élément de GeotrekAggCorrespondances

    Args:
        DB ([type]): [description]
        id (int): identifiant de l'élément

    Returns:
        [type]: [description]
    """
    data = DB.session.query(GeotrekAggCorrespondances).filter_by(id = id).one()
    return data


def update_cor_data(DB, id, new_mapping_id=None):
    """
        Mise à jour de l'élément de mapping
    Args:
        DB ([type]): [description]
        id (int): identifiant de l'élément
        new_mapping_id (int, optional): identifiant de l'élément dans la base aggrégator. Defaults to None.
    """
    data = get_mapping_el(DB, id)
    data.id_destination = new_mapping_id
    try:
        DB.session.add(data)
        DB.session.commit()
    except Exception as e:
        raise(e)


def get_common_col_name(DB, db_source, table_name):
    """
        Récupération des colonnes communes aux deux modèles

    Args:
        DB ([type]): [description]
        db_source ([type]): [description]
        table_name ([type]): [description]
    """
    sql = """
        WITH gta_col AS (
            SELECT * FROM information_schema.COLUMNS
            WHERE table_name = '{table_name}'
                AND table_schema = 'public'
        ), import_col AS (
            SELECT * FROM information_schema.COLUMNS
            WHERE table_name = '{table_name}'
                AND table_schema = '{db_source}'
        )
        SELECT i.column_name
        FROM gta_col g, import_col i
        WHERE g.column_name = i.column_name;
    """
    try:
        columns = DB.engine.execute(sql.format(db_source=db_source, table_name=table_name)).fetchall()
        return [c[0] for c in columns]
    except Exception as e:
        raise(e)


def get_source(DB, name):
    """[summary]

    Args:
        DB ([connexion]):
        name ([string]): nom de la source

    Returns:
        [GeotrekAggSources]: [description]
    """
    try:
        source = DB.session.query(
            GeotrekAggSources
        ).filter_by(bdd_source=name).one()
    except NoResultFound:
        return None
    return source


def create_fdw_server(DB, name, db_name, host, port, user, password):
    """
        Création du server fdw

    Args:
        DB ([connexion])
        name ([string]): nom de la source
        host ([string]): hote de la base geotrek
        port ([int]): port de postgresql de l'hote
        user ([string]): utilisateur (ayant des droits de lecture sur la base)
        password ([string]): mot de passe de l'utilisateur
    """

    sql1 = f"""
        DROP SERVER IF EXISTS server_{name} CASCADE;
        CREATE SERVER IF NOT EXISTS server_{name}
                FOREIGN DATA WRAPPER postgres_fdw
                OPTIONS (host '{host}', port '{port}', dbname '{db_name}');
    """
    sql2 = f"""
        CREATE USER MAPPING FOR dbadmin
            SERVER server_{name}
            OPTIONS (user '{user}', password '{password}');
    """
    sql3= f"""
        DROP SCHEMA IF EXISTS {name};
        CREATE SCHEMA {name};
        IMPORT FOREIGN SCHEMA public
            FROM SERVER server_{name}
            INTO {name};       
    """
    DB.engine.execute(sql1)
    click.echo(f"Serveur créé")
    DB.engine.execute(sql2)
    click.echo(f"User mapping effectué")
    DB.engine.execute(sql3)
    click.echo(f"Schéma importé")