------CREATION UUIDs dans BDD source

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE core_topology ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE common_attachment ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_informationdesk ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_touristiccontent ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_touristicevent ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE feedback_report ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();

ALTER TABLE trekking_trek ADD COLUMN IF NOT EXISTS uuid uuid;
UPDATE trekking_trek t SET uuid = uuid_generate_v4()
FROM core_topology ct WHERE ct.id = t.topo_object_id AND t.uuid IS NULL;

ALTER TABLE trekking_poi ADD COLUMN IF NOT EXISTS uuid uuid;
UPDATE trekking_poi t SET uuid = uuid_generate_v4()
FROM core_topology ct WHERE ct.id = t.topo_object_id AND t.uuid IS NULL;


------CREATION CHAMPS UUIDs dans BDD agg (sans génération)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE core_topology ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE common_attachment ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE tourism_informationdesk ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE tourism_touristiccontent ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE tourism_touristicevent ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE feedback_report ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE trekking_trek ADD COLUMN IF NOT EXISTS uuid uuid;
ALTER TABLE trekking_poi ADD COLUMN IF NOT EXISTS uuid uuid;



----MISE EN PLACE FDW dans BDD agg
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

--DROP SERVER IF EXISTS server_pnc CASCADE;
CREATE SERVER IF NOT EXISTS server_pnc
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host 'localhost', port '5432', dbname 'geotrek_pnc');

CREATE USER MAPPING FOR dbadmin
    SERVER server_pnc
    OPTIONS (user user, password password);

--DROP SCHEMA IF EXISTS pnc;
CREATE SCHEMA pnc;
IMPORT FOREIGN SCHEMA public
    FROM SERVER server_pnc
    INTO pnc;

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
$function$
;


--------FONCTION D'OBTENTION DE L'ID D
CREATE OR REPLACE FUNCTION public.geotrekagg_get_foreign_key(
	_filter_value varchar, -- Valeur pour filtrer et retrouver la données

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

	--RAISE NOTICE '%', _txt_sql;
	EXECUTE _txt_sql into _new_id;

    RETURN _new_id;
END;
$function$
;




----COMPARAISON SCHEMAS, permet d'identifier quelles sont les colonnes qui diffèrent dans les deux schémas
SELECT COALESCE(c1.table_name, c2.table_name) AS table_name,
       COALESCE(c1.column_name, c2.column_name) AS table_column,
       c1.column_name AS pnc,
       c2.column_name AS pne
FROM
    (SELECT table_name,
            column_name
     FROM information_schema.COLUMNS c
     WHERE c.table_schema = 'pnc') c1
FULL JOIN
         (SELECT table_name,
                 column_name
          FROM information_schema.COLUMNS c
          WHERE c.table_schema = 'pne') c2
ON c1.table_name = c2.table_name AND c1.column_name = c2.column_name
WHERE c1.column_name IS NULL
      OR c2.column_name IS NULL
ORDER BY table_name,
         table_column;