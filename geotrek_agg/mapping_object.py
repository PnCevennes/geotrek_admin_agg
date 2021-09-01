
from geotrek_agg.utils import get_common_col_name


class MappingObject(object):

    def __init__(self, DB, data_source, table_name, table_def, is_cor=False):
        self._DB = DB
        self._data_source = data_source
        self._table_name = table_name
        self._table_def = table_def
        self._is_cor = is_cor
        self._cor_list = []
        self.build_object()

    def build_object(self):

        # build cor table
        cor_tables = self._table_def.get("cor_tables",  [])
        if not cor_tables:
            return

        for cor_table in cor_tables:
            self._cor_list.append(self.build_cor_object(cor_table))


    def build_cor_object(self, cor_table):
        """
            Mise en forme des tables de correlation
            c-a-d ayant un lien n..m

        Args:
            cor_table (string): nom de la table de correlation

        Returns:
            MappingObject: table de corrélation
        """

        parent_table = self._get_parent_table()
        cor_table_data = self._table_def["cor_tables"][cor_table]
        cor_table_data["parent_table"] = parent_table
        cor_table_data["foreign_keys"] = {
            cor_table_data["key"]: parent_table
        }
        cor_table_data["filters"] = {
           "not_null": [k for k in cor_table_data["category_keys"]]
        }
        cor_table_data["filters"]["not_null"].append(cor_table_data["key"])

        return MappingObject(
            DB=self._DB,
            data_source=self._data_source,
            table_name=cor_table,
            table_def=cor_table_data,
            is_cor=True
        )

    def generate_sql_insert(self):

        cols = get_common_col_name(self._DB, self._data_source, self._table_name)

        SQL_MEDIA = ''
        if "common_attachment" in self._table_def:
            SQL_MEDIA = self._generate_attachment_sql_insert()
        if "excluded" in self._table_def:
            cols = list(filter(lambda col: col not in self._table_def["excluded"], cols))
        formated_cols = ','.join(['"{}"'.format(c) for c in cols])

        SQL_I = f"INSERT INTO {self._table_name} ({formated_cols})"


        # build select
        select_col = []
        for col in cols:
            if col in self._table_def.get("category_keys",  []) and col != "creator_id":
                # filter by category_keys appel de la fonction geotrekagg_get_category_id
                select_col.append(
                    """geotrekagg_get_category_id (
                        {col}, '{table}', '{db_source}'
                    ) as {col}
                    """.format(
                        col=col,
                        table=self._table_def["category_keys"][col],
                        db_source=self._data_source
                    )
                )
            elif col in self._table_def.get("foreign_keys",  []):
                # filter by foreign_keys appel de la fonction geotrekagg_get_foreign_key
                select_col.append(
                    """
                        geotrekagg_get_foreign_key (
                            {col_s}::varchar, '{table_s}','{table_r}', '{col_s}',  '{col_r}', '{db_source}'
                        ) as {col_s}
                    """.format(
                        table_s=self._table_name,
                        table_r=self._table_def["foreign_keys"][col]["table"],
                        col_s=col,
                        col_r=self._table_def["foreign_keys"][col]["col"],
                        db_source=self._data_source
                    )
                )
            else:
                # retourne uniquement le nom de la colonne
                select_col.append('"{}"'.format(col))

        # build filter
        #   not null column
        filter_col = []
        for f_col in self._table_def.get("filters",  []):
            if f_col == "not_null":
                filter_col.append(
                    " AND ".join([f" NOT {f} IS NULL " for f in self._table_def["filters"][f_col]])
                )
            else:
                pass

        # build final sql
        formated_insert_col = ','.join(select_col)
        if filter_col:
            formated_filter =  " WHERE " + ' AND'.join(filter_col)
        else:
            formated_filter = ""
        SQL_S = f"""
            SELECT *
            FROM (
                SELECT {formated_insert_col}
                FROM {self._data_source}.{self._table_name}
            ) a
            {formated_filter}
        """

        # build cor table
        cor_sql = []
        for table_cor in self._cor_list:
            # TODO
            cor_sql.append(table_cor.generate_sql_insert())

        SQL_COR = " ".join(cor_sql)

        return f"{SQL_I} {SQL_S}; {SQL_COR}; {SQL_MEDIA};"

    def generate_sql_delete(self):
        """
            Construction du sql de suppression des données de la source
        """
        if self._is_cor:
            # Génération du code sql de deletion des tables de
            #   correlations
            return self._generate_cor_sql_delete(
                table_name=self._table_name,
                key=self._table_def["key"],
                parent_table=self._table_def["parent_table"]
                )
        else:
            sql = []
            for cor in self._cor_list:
                sql.append(cor.generate_sql_delete())
            sql.append(self._generate_simple_sql_delete())
            sql = " ".join(sql)

            return sql

    def _generate_cor_sql_delete(self, table_name, key, parent_table):
        """
            Génération du code sql de deletion des tables de
            correlations
        """
        # parent_table = self._table_def["parent_table"]

        sql = """
            WITH to_del AS (
                SELECT p.{parent_col_id} AS id_to_del
                FROM {parent_table_name} p
                JOIN {source}.{parent_table_name} t
                ON p.uuid = t.uuid
            )
            DELETE FROM {table_name} p
            USING to_del
            WHERE p.{col_id} = to_del.id_to_del;
        """.format(
            parent_col_id=parent_table["col"],
            parent_table_name=parent_table["table"],
            source=self._data_source,
            table_name=table_name,
            col_id=key
        )
        return sql

    def _generate_simple_sql_delete(self):
        """
            Génération du code sql de deletion des tables principales
            ayant un uuid
        """
        # TODO : test uuid exists
        sql = f"""
            DELETE FROM {self._table_name} p
            USING {self._data_source}.{self._table_name} t
            WHERE p.uuid = t.uuid;
        """
        return sql

    def _generate_attachment_sql_insert(self):
        att_col = get_common_col_name(
            DB=self._DB,
            db_source=self._data_source,
            table_name='common_attachment'
        )
        specific_col = [
            "object_id",
            "content_type_id",
            "filetype_id",
            "creator_id",
            "attachment_file",
            "attachment_video",
            "attachment_link"
        ]
        excluded_col = [*specific_col, *["id"]]
        f_att_col = ','.join(['"{}"'.format(c) for c in att_col if not c in excluded_col])
        f_att_col_select = ','.join(['ca."{}"'.format(c) for c in att_col if not c in excluded_col])
        f_att_col_specific = ','.join(['"{}"'.format(c) for c in specific_col])
        sql = f"""
            INSERT INTO common_attachment ({f_att_col}, {f_att_col_specific})
            SELECT
                {f_att_col_select},
                p.{self._table_def["primary_key"]} as object_id,
                geotrekagg_get_category_id (content_type_id, 'django_content_type', '{self._data_source}') as content_type_id,
                geotrekagg_get_category_id (filetype_id, 'common_filetype', '{self._data_source}') as filetype_id,
                (SELECT id FROM auth_user WHERE username ILIKE '__internal__' LIMIT 1) as creator_id,
                '' AS attachment_file,
                '' AS attachment_video,
                (SELECT url FROM geotrekagg_sources WHERE bdd_source = '{self._data_source}' LIMIT 1) || 'media/' || COALESCE(attachment_file, attachment_video) as attachment_link
            FROM {self._data_source}.{self._table_name} tp
            JOIN {self._data_source}.common_attachment ca
            ON tp.{self._table_def["primary_key"]} = ca.object_id
            JOIN {self._data_source}.django_content_type dct
            ON dct.id = ca.content_type_id AND dct.app_label ||'_' || dct.model = '{self._table_name}'
            JOIN {self._table_name} p
            ON tp.uuid = p.uuid
        """
        return sql

    def _get_parent_table(self):
        return {
            "table": self._table_name,
            "col": self._table_def["primary_key"]
        }