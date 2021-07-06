
from geotrek_agg.env import COR_TABLE
from geotrek_agg.models import CommonCorrespondances

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

def get_all_cor_data(DB):
    sql = []
    for c in COR_TABLE:
        sql.append(
            "SELECT  '{cor_table}' as table_source, id, {label} as label FROM public.{cor_table}".format(
                cor_table=c, label=COR_TABLE[c]['label_field']
            )
        )
    query = ' UNION '.join(sql)

    data = DB.session.connection().execute(query)
    return data

def get_structured_cor_data(DB):
    voc_data = get_all_cor_data(DB)
    structured_voc_data = {}
    for voc in voc_data:
        if not voc[0] in structured_voc_data:
            structured_voc_data[voc[0]] = {}
        structured_voc_data[voc[0]][voc[1]] = voc[2] 
    return structured_voc_data


def get_mapping_el(DB, id):
    data = DB.session.query(CommonCorrespondances).filter_by(id = id).one()
    return data


def update_cor_data(DB, id, new_mapping_id=None):
    data = get_mapping_el(DB, id)
    data.id_destination = new_mapping_id
    try:
        DB.session.add(data)
        DB.session.commit()
    except Exception as e:
        raise(e)
