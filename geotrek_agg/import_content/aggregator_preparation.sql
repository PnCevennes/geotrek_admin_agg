----CREATION TABLE common_sourceportal POUR CONSERVER L'ORIGINE DES DONNEES
CREATE TABLE common_sourceportal
(id SERIAL PRIMARY KEY,
"name" varchar);

INSERT INTO common_sourceportal("name") VALUES
('pnc'),('pne');

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
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
ALTER TABLE core_topology ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE trekking_trek ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE trekking_poi ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_informationdesk ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE feedback_report ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_touristiccontent ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_touristicevent ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE common_attachment ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();


----INSTALLER EXTENSION POUR GENERER UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

---- Création d'un uuid préalable à l'import, requêtes à lancer dans la/les BDD source
-- (étape rendue nécessaire par son absence pour l'instant dans les données sources)
-- à faire avant la création du FDW car définition de celui-ci ne change pas (colonnes créées ne sont pas ajoutées)
WITH
A (table_name) AS (
	VALUES
		('core_topology'),
		('trekking_orderedtrekchild'),
		('trekking_trekrelationship'),
		('trekking_trek_accessibilities'),
		('tourism_informationdesk'),
		('trekking_trek_information_desks'),
		('trekking_trek_networks'),
		('trekking_trek_portal'),
		('trekking_trek_source'),
		('trekking_trek_themes'),
		('trekking_weblink'),
		('trekking_trek_web_links'),
		('trekking_trek_labels'),
		('trekking_trek_pois_excluded'),
		('feedback_report'),
		('tourism_touristiccontent'),
		('tourism_touristiccontenttype'),
		('tourism_touristiccontent_portal'),
		('tourism_touristiccontent_source'),
		('tourism_touristiccontent_themes'),
		('tourism_touristiccontent_type1'),
		('tourism_touristiccontent_type2'),
		('tourism_touristicevent'),
		('tourism_touristicevent_portal'),
		('tourism_touristicevent_source'),
		('tourism_touristicevent_themes'),
		('common_filetype'),
		('common_attachment'),
		('core_path'),
		('core_pathaggregation')
	)
SELECT
	'ALTER TABLE ' || table_name ||
	'
ADD COLUMN IF NOT EXISTS uuid uuid;' AS add_uuid_column,
	'UPDATE ' || table_name ||
    '
SET uuid = uuid_generate_v4()
WHERE uuid IS NULL;' AS generate_uuid
FROM a;

----Même chose pour trekking_trek et poi, dont l'uuid est censé être le même que celui des core_topology
-- (reprise de la clef étrangère trekking_trek.topo_object_id = core_topology.id)
WITH
A (table_name) AS (
	VALUES
		('trekking_trek'), ('trekking_poi')
	)
SELECT
	'ALTER TABLE ' || table_name ||
	'
ADD COLUMN IF NOT EXISTS uuid uuid;' AS add_uuid_column,
	'UPDATE ' || table_name ||
    ' t
SET uuid = uuid_generate_v4()
FROM core_topology ct
WHERE ct.id = t.topo_object_id
AND t.uuid IS NULL;' AS generate_uuid
FROM a;



----MISE EN PLACE FDW

CREATE EXTENSION IF NOT EXISTS postgres_fdw;

--DROP SERVER IF EXISTS server_pnc CASCADE;
CREATE SERVER IF NOT EXISTS server_pnc
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host 'localhost', port '5432', dbname 'geotrek_pnc');

CREATE USER MAPPING FOR dbadmin
    SERVER server_pnc
    OPTIONS (user 'dbadmin', password '24121994');

--DROP SCHEMA IF EXISTS pnc;
CREATE SCHEMA pnc;
IMPORT FOREIGN SCHEMA public
    FROM SERVER server_pnc
    INTO pnc;

--DROP SERVER IF EXISTS server_pne CASCADE;
CREATE SERVER IF NOT EXISTS server_pne
        FOREIGN DATA WRAPPER postgres_fdw
        OPTIONS (host 'localhost', port '5432', dbname 'geotrek_pne');

CREATE USER MAPPING FOR dbadmin
    SERVER server_pne
    OPTIONS (user 'dbadmin', password '24121994');

--DROP SCHEMA IF EXISTS pne;
CREATE SCHEMA pne;
IMPORT FOREIGN SCHEMA public
    FROM SERVER server_pne
    INTO pne;


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