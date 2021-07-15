
from geotrek_agg.env import COR_TABLE
from geotrek_agg.models import GeotrekAggCorrespondances


def insert_cor_data(DB, db_source, cor_table, fields):
    """
        Insertion des données dans la table geotrekagg_correspondances
    """
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
    except Exception as e:
        print(e)


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
    except Exception as e:
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



def build_sql_insert(DB, db_source, table_name, table_data):
    """
        Construction du sql de création des données

    Args:
        DB ([type]): [description]
        db_source ([type]): [description]
        table_name ([type]): [description]
        table_data ([type]): [description]

    """
    cols = get_common_col_name(DB, db_source, table_name)

    if "excluded" in table_data:
        cols = list(filter(lambda col: col not in table_data["excluded"], cols))
    formated_cols = ','.join(['"{}"'.format(c) for c in cols])

    SQL_I = f"INSERT INTO {table_name} ({formated_cols})"

    # build select
    # filter by correspondances_keys
    select_col = []
    for col in cols:
        if col in table_data.get("correspondances_keys",  []):
            select_col.append(
                "geotrekagg_get_id_correspondance( {col}, '{table}', '{db_source}' ) as col".format(
                    col=col,
                    table=table_data["correspondances_keys"][col],
                    db_source=db_source
                )
            )
        else:
            select_col.append('"{}"'.format(col))

    formated_insert_col = ','.join(select_col)
    SQL_S = f"SELECT {formated_insert_col} FROM {db_source}.{table_name}"

    try:
        DB.engine.execute(SQL_I + " " + SQL_S)
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
            SELECT * FROM  information_schema.COLUMNS
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