
------CREATION UUIDs dans BDD source
ALTER TABLE core_topology ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE common_attachment ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_informationdesk ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_touristiccontent ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE tourism_touristicevent ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE feedback_report ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE trekking_trek ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE trekking_poi ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE trekking_weblink ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE signage_signage ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE signage_blade ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();
ALTER TABLE signage_line ADD COLUMN IF NOT EXISTS uuid uuid DEFAULT uuid_generate_v4();

CREATE INDEX index_core_topology_uuid ON core_topology USING btree (uuid);
CREATE INDEX index_common_attachment_uuid ON common_attachment USING btree (uuid);
CREATE INDEX index_tourism_informationdesk_uuid ON tourism_informationdesk USING btree (uuid);
CREATE INDEX index_tourism_touristiccontent_uuid ON tourism_touristiccontent USING btree (uuid);
CREATE INDEX index_tourism_touristicevent_uuid ON tourism_touristicevent USING btree (uuid);
CREATE INDEX index_feedback_report_uuid ON feedback_report USING btree (uuid);
CREATE INDEX index_trekking_trek_uuid ON trekking_trek USING btree (uuid);
CREATE INDEX index_trekking_poi_uuid ON trekking_poi USING btree (uuid);
CREATE INDEX index_trekking_weblink_uuid ON trekking_weblink USING btree (uuid);
CREATE INDEX index_signage_signage_uuid ON signage_signage USING btree (uuid);
CREATE INDEX index_signage_blade_uuid ON signage_blade USING btree (uuid);
CREATE INDEX index_signage_line_uuid ON signage_line USING btree (uuid);

-------FONCTION D'OBTENTION DU NOUVEL ID D'UNE CATEGORIE
CREATE OR REPLACE FUNCTION public.geotrekagg_get_category_id(
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
	_filter_value varchar, -- Valeur pour filtrer et retrouver la donnée

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