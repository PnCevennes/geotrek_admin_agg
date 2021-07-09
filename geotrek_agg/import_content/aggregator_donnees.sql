TRUNCATE core_topology CASCADE;
TRUNCATE trekking_poi CASCADE;
TRUNCATE trekking_trek CASCADE;
TRUNCATE trekking_orderedtrekchild CASCADE;
TRUNCATE trekking_trekrelationship CASCADE;
TRUNCATE trekking_trek_accessibilities CASCADE;
TRUNCATE tourism_informationdesk CASCADE;
TRUNCATE trekking_trek_information_desks CASCADE;
TRUNCATE trekking_trek_networks CASCADE;
TRUNCATE trekking_trek_portal CASCADE;
TRUNCATE trekking_trek_source CASCADE;
TRUNCATE trekking_trek_themes CASCADE;
TRUNCATE trekking_weblink CASCADE;
TRUNCATE trekking_trek_web_links CASCADE;
TRUNCATE trekking_trek_labels CASCADE;
TRUNCATE trekking_trek_pois_excluded CASCADE;
TRUNCATE feedback_report CASCADE;
TRUNCATE tourism_touristiccontent CASCADE;
TRUNCATE tourism_touristiccontenttype CASCADE;
TRUNCATE tourism_touristiccontent_portal CASCADE;
TRUNCATE tourism_touristiccontent_source CASCADE;
TRUNCATE tourism_touristiccontent_themes CASCADE;
TRUNCATE tourism_touristiccontent_type1 CASCADE;
TRUNCATE tourism_touristiccontent_type2 CASCADE;
TRUNCATE tourism_touristicevent CASCADE;
TRUNCATE tourism_touristicevent_portal CASCADE;
TRUNCATE tourism_touristicevent_source CASCADE;
TRUNCATE tourism_touristicevent_themes CASCADE;
TRUNCATE common_filetype CASCADE;
TRUNCATE common_attachment CASCADE;
TRUNCATE core_path CASCADE;
TRUNCATE core_pathaggregation CASCADE;

-- Insertion CORE_TOPOLOGY (trek et poi), "pnc." à remplacer par nom générique comme "bdd_source." dès le FDW
INSERT INTO core_topology
	(date_insert, date_update, deleted, geom_3d, length, ascent, descent,
	min_elevation, max_elevation, slope, "offset", kind, geom, geom_need_update, uuid)
SELECT
	date_insert, date_update, deleted, geom_3d, length, ascent, descent,
	min_elevation, max_elevation, slope, "offset", kind, geom, geom_need_update, uuid
FROM pnc.core_topology "source"
WHERE kind ILIKE 'poi' OR kind ILIKE 'trek';



-- Insertion TREKKING_POI
INSERT INTO trekking_poi
	(published, publication_date, "name", review,
	topo_object_id, description, eid, structure_id, type_id,
	published_fr, published_en, description_fr,
	description_en, name_fr, name_en,
	uuid)
SELECT
	published, publication_date, "source"."name", review,
	ct.id, description, eid, st.id, tp.id,
	published_fr, published_en, description_fr,
	description_en, name_fr, name_en,
	"source".uuid
FROM pnc.trekking_poi "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON "source".uuid = ct.uuid
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM trekking_poitype a
		   LEFT JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'trekking_poitype' AND a."label" ILIKE cc.name_new) tp
ON tp.bdd_source ILIKE csp."name" AND "source".type_id = tp.id_old::integer;
		  
		  
-- Insertion TREKKING_TREK
INSERT INTO trekking_trek
	(published, publication_date, "name", review, topo_object_id, departure, arrival,
	description_teaser, description, ambiance, "access", disabled_infrastructure, duration,
	advised_parking, parking_location, public_transport, advice, points_reference, eid,
	eid2, difficulty_id, practice_id, route_id, structure_id, reservation_id, reservation_system_id,
	arrival_fr, arrival_en, ambiance_fr, ambiance_en, departure_fr, departure_en, access_fr, access_en,
	advised_parking_fr, advised_parking_en, disabled_infrastructure_fr, disabled_infrastructure_en,
	published_fr, published_en, advice_fr, advice_en, name_fr, name_en,
	public_transport_fr, public_transport_en, description_fr, description_en,
	description_teaser_fr, description_teaser_en, uuid)
SELECT
	published, publication_date, "source"."name", review, ct.id, departure, arrival, description_teaser,
	"source".description, ambiance, "access", disabled_infrastructure, duration,
	advised_parking, parking_location,public_transport, advice, points_reference, eid,
	eid2, dl.id, tp.id, tr.id, st.id, reservation_id, crs.id,
	arrival_fr, arrival_en, ambiance_fr,ambiance_en, departure_fr, departure_en, access_fr, access_en,
	advised_parking_fr, advised_parking_en, disabled_infrastructure_fr, disabled_infrastructure_en,
	published_fr, published_en, advice_fr, advice_en, "source".name_fr, "source".name_en,
	public_transport_fr, public_transport_en, "source".description_fr, "source".description_en,
	description_teaser_fr, description_teaser_en, "source".uuid
FROM pnc.trekking_trek "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON "source".uuid = ct.uuid
LEFT JOIN (SELECT a.id, cc.* FROM trekking_difficultylevel a
		   LEFT JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'trekking_difficultylevel' AND a.difficulty ILIKE cc.name_new) dl
ON dl.bdd_source ILIKE csp."name" AND "source".difficulty_id = dl.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM trekking_practice a
		   LEFT JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'trekking_practice' AND a."name" ILIKE cc.name_new) tp
ON tp.bdd_source ILIKE csp."name" AND "source".practice_id = tp.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM trekking_route a
		   LEFT JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'trekking_route' AND a.route ILIKE cc.name_new) tr
ON tr.bdd_source ILIKE csp."name" AND "source".route_id = tr.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM common_reservationsystem a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'common_reservationsystem' AND a."name" ILIKE cc.name_new) crs
ON crs.bdd_source ILIKE csp."name" AND "source".structure_id = crs.id_old::integer;
		   


---------- Jusqu'ici les requêtes d'insertion fonctionnent avec la nouvelle structure des uuid
---------- En-dessous les requêtes doivent encore être mises à jour sur ce point (certaines fonctionnent déjà mais pas toutes)
---------- Autre évolution nécessaire : la mise sous forme de fonction des nombreuses jointures récurrentes
---------- (authent_structure, etc.)

		   
-- Insertion TREKKING_ORDEREDTREKCHILD
INSERT INTO trekking_orderedtrekchild
	("order", child_id, parent_id, uuid)
SELECT
	"order", ct1.id, ct2.id, "source".uuid
FROM pnc.trekking_orderedtrekchild "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct1 ON "source".uuid = ct1.uuid
LEFT JOIN core_topology ct2 ON "source".uuid = ct2.uuid;



-- Insertion TREKKING_TREKRELATIONSHIP
INSERT INTO trekking_trekrelationship
	(has_common_departure, has_common_edge, is_circuit_step, trek_a_id, trek_b_id, uuid)
SELECT
	has_common_departure, has_common_edge, is_circuit_step, ct1.id, ct2.id, "source".uuid
FROM pnc.trekking_trekrelationship "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct1 ON "source".uuid = ct1.uuid
LEFT JOIN core_topology ct2 ON "source".uuid = ct2.uuid;



-- Insertion TREKKING_TREK_ACCESSIBILITIES
INSERT INTO trekking_trek_accessibilities
	(trek_id, accessibility_id, uuid)
SELECT
	ct.id, accessibility_id, "source".uuid
FROM pnc.trekking_trek_accessibilities "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON "source".uuid = ct.uuid
LEFT JOIN (SELECT a.id, cc.* FROM trekking_accessibility a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'trekking_accessibility' AND a."name" ILIKE cc.name_new) ta
ON ta.bdd_source ILIKE csp."name" AND "source".accessibility_id = ta.id_old::integer;
		  
		  

-- Insertion TOURISM_INFORMATIONDESK
INSERT INTO tourism_informationdesk
	("name", description, phone, email, website, photo,
	street, postal_code, municipality, geom, type_id,
	description_fr, description_en, name_fr, name_en,
	uuid)
SELECT
	"source"."name", description, phone, email, website, photo,
	street, postal_code, municipality, geom, tid.id,
	description_fr, description_en, name_fr, name_en,
	"source".uuid
FROM pnc.tourism_informationdesk "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM tourism_informationdesktype a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'tourism_informationdesktype' AND a."label" ILIKE cc.name_new) tid
ON tid.bdd_source ILIKE csp."name" AND "source".type_id = tid.id_old::integer;



-- Insertion TREKKING_TREK_INFORMATIONDESKS
INSERT INTO trekking_trek_information_desks
	(trek_id, informationdesk_id, uuid)
SELECT
	tt.topo_object_id, tid.id, "source".uuid
FROM pnc.trekking_trek_information_desks "source"
LEFT JOIN pnc.trekking_trek pnc_tt ON "source".trek_id = pnc_tt.topo_object_id
LEFT JOIN trekking_trek tt ON pnc_tt.uuid = tt.uuid
LEFT JOIN pnc.tourism_informationdesk pnc_tid ON "source".informationdesk_id = pnc_tid.id
LEFT JOIN tourism_informationdesk tid ON pnc_tid.uuid = tid.uuid;

-- Insertion TREKKING_TREK_NETWORKS
INSERT INTO trekking_trek_networks
	(trek_id, treknetwork_id, uuid)
SELECT
	ct.id, ttn.id, "source".uuid
FROM pnc.trekking_trek_networks "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON csp."name" || '_' || "source".trek_id = ct.eid
LEFT JOIN (SELECT a.id, cc.* FROM trekking_treknetwork a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'trekking_treknetwork' AND a."network" ILIKE cc.name_new) ttn
ON ttn.bdd_source ILIKE csp."name" AND "source".treknetwork_id = ttn.id_old::integer;


-- Insertion TREKKING_TREK_PORTAL
INSERT INTO trekking_trek_portal
	(trek_id, targetportal_id, uuid)	
SELECT
	ct.id, ctp.id, "source".uuid
FROM pnc.trekking_trek_portal "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON csp."name" || '_' || "source".trek_id = ct.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_targetportal a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_targetportal' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".targetportal_id = ctp.id_old::integer;

-- Insertion TREKKING_TREK_SOURCE
INSERT INTO trekking_trek_source
	(trek_id, recordsource_id, uuid)		
SELECT
	ct.id, ctp.id, "source".uuid
FROM pnc.trekking_trek_source "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON csp."name" || '_' || "source".trek_id = ct.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_recordsource a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_recordsource' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".recordsource_id = ctp.id_old::integer;

-- Insertion TREKKING_TREK_THEMES
INSERT INTO trekking_trek_themes
	(trek_id, theme_id, uuid)
SELECT
	ct.id, cth.id, "source".uuid
FROM pnc.trekking_trek_themes "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON csp."name" || '_' || "source".trek_id = ct.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_theme a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_theme' AND a."label" ILIKE cc.name_new) cth
ON cth.bdd_source ILIKE csp."name" AND "source".theme_id = cth.id_old::integer;

-- Insertion TREKKING_WEBLINK
INSERT INTO trekking_weblink
	("name", url, category_id, name_en, name_fr, uuid)
SELECT
	"source"."name", url, twl.id, name_en, name_fr, "source".uuid
FROM pnc.trekking_weblink "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM trekking_weblinkcategory a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'trekking_weblinkcategory' AND a."label" ILIKE cc.name_new) twl
ON twl.bdd_source ILIKE csp."name" AND "source".category_id = twl.id_old::integer;

-- Insertion TREKKING_TREK_WEB_LINKS
INSERT INTO trekking_trek_web_links
	(trek_id, weblink_id, uuid)	
SELECT
	ct.id, twl.id, "source".uuid
FROM pnc.trekking_trek_web_links "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
JOIN core_topology ct ON csp."name" || '_' || "source".trek_id = ct.eid
LEFT JOIN trekking_weblink twl ON csp."name" || '_' || "source".weblink_id = twl.eid;

-- Insertion TREKKING_TREK_LABELS
INSERT INTO trekking_trek_labels
	(trek_id, label_id, uuid)
SELECT
	ct.id, cl.id, "source".uuid
FROM pnc.trekking_trek_labels "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON csp."name" || '_' || "source".trek_id = ct.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_label a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_label' AND a."name" ILIKE cc.name_new) cl
ON cl.bdd_source ILIKE csp."name" AND "source".label_id = cl.id_old::integer;

-- Insertion TREKKING_TREK_POIS_EXCLUDED
INSERT INTO trekking_trek_pois_excluded
	(trek_id, poi_id, uuid)
SELECT
	t.topo_object_id, p.topo_object_id, "source".uuid
FROM pnc.trekking_trek_pois_excluded "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN trekking_trek t ON csp."name" || '_' || "source".trek_id = t.eid
LEFT JOIN trekking_poi p ON csp."name" || '_' || "source".poi_id = p.eid;

-- Insertion FEEDBACK_REPORT
INSERT INTO feedback_report
	(date_insert, date_update, email, "comment", geom, category_id, status_id,
	activity_id, problem_magnitude_id, related_trek_id, uuid)	
SELECT
	"source".date_insert, "source".date_update, email, "comment", "source".geom, frc.id, frs.id,
	fra.id, frp.id, ct.id, "source".uuid
FROM pnc.feedback_report "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN core_topology ct ON csp."name" || '_' || "source".related_trek_id = ct.eid
LEFT JOIN (SELECT a.id, cc.* FROM feedback_reportcategory a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'feedback_reportcategory' AND a."label" ILIKE cc.name_new) frc			
ON frc.bdd_source ILIKE csp."name" AND "source".category_id = frc.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM feedback_reportstatus a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'feedback_reportstatus' AND a."label" ILIKE cc.name_new) frs
ON frs.bdd_source ILIKE csp."name" AND "source".status_id = frs.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM feedback_reportactivity a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'feedback_reportactivity' AND a."label" ILIKE cc.name_new) fra
ON fra.bdd_source ILIKE csp."name" AND "source".activity_id = fra.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM feedback_reportproblemmagnitude a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'feedback_reportproblemmagnitude' AND a."label" ILIKE cc.name_new) frp
ON frp.bdd_source ILIKE csp."name" AND "source".problem_magnitude_id = frp.id_old::integer;


-- Insertion TOURISM_TOURISTICCONTENT
INSERT INTO tourism_touristiccontent
	(date_insert, date_update, deleted, published, publication_date,
	"name", review, description_teaser, description, geom, contact,
	email, website, practical_info, reservation_id, approved,
	category_id, reservation_system_id, structure_id, published_fr,
	published_en, practical_info_fr, practical_info_en, name_fr,
	name_en, description_fr, description_en, description_teaser_fr, description_teaser_en, uuid)
SELECT
	date_insert, date_update, deleted, published, publication_date,
	"source"."name", review, description_teaser, description, geom, contact,
	email, website, practical_info, reservation_id, approved,
	cat.id, crs.id, st.id, published_fr,
	published_en, practical_info_fr, practical_info_en, name_fr,
	name_en, description_fr, description_en, description_teaser_fr, description_teaser_en, "source".uuid
FROM pnc.tourism_touristiccontent "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM tourism_touristiccontentcategory a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'tourism_touristiccontentcategory' AND a."label" ILIKE cc.name_new) cat
ON cat.bdd_source ILIKE csp."name" AND "source".category_id = cat.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM common_reservationsystem a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'common_reservationsystem' AND a."name" ILIKE cc.name_new) crs
ON crs.bdd_source ILIKE csp."name" AND "source".reservation_system_id = crs.id_old::integer;


-- Insertion TOURISM_TOURISTICCONTENTTYPE
INSERT INTO tourism_touristiccontenttype
	(pictogram, "label", in_list, category_id, label_fr, label_en, uuid)
SELECT
	pictogram, "label", in_list, cat.id, label_fr, label_en, "source".uuid
FROM pnc.tourism_touristiccontenttype "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM tourism_touristiccontentcategory a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'tourism_touristiccontentcategory' AND a."label" ILIKE cc.name_new) cat
ON cat.bdd_source ILIKE csp."name" AND "source".category_id = cat.id_old::integer;


-- Insertion TOURISM_TOURISTICCONTENT_PORTAL
INSERT INTO tourism_touristiccontent_portal
	(touristiccontent_id, targetportal_id, uuid)
SELECT
	tc.id, ctp.id, "source".uuid
FROM pnc.tourism_touristiccontent_portal "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristiccontent tc ON csp."name" || '_' || "source".touristiccontent_id = tc.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_targetportal a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_targetportal' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".targetportal_id = ctp.id_old::integer;

-- Insertion TOURISM_TOURISTICCONTENT_SOURCE
INSERT INTO tourism_touristiccontent_source
	(touristiccontent_id, recordsource_id, uuid)
SELECT
	tc.id, crs.id, "source".uuid
FROM pnc.tourism_touristiccontent_source "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristiccontent tc ON csp."name" || '_' || "source".touristiccontent_id = tc.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_recordsource a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_recordsource' AND a."name" ILIKE cc.name_new) crs
ON crs.bdd_source ILIKE csp."name" AND "source".recordsource_id = crs.id_old::integer;

-- Insertion TOURISM_TOURISTICCONTENT_THEMES
INSERT INTO tourism_touristiccontent_themes
	(touristiccontent_id, theme_id, uuid)
SELECT
	tc.id, cth.id, "source".uuid
FROM pnc.tourism_touristiccontent_themes "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristiccontent tc ON csp."name" || '_' || "source".touristiccontent_id = tc.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_theme a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_theme' AND a."label" ILIKE cc.name_new) cth
ON cth.bdd_source ILIKE csp."name" AND "source".theme_id = cth.id_old::integer;

-- Insertion TOURISM_TOURISTICCONTENT_TYPE1
INSERT INTO tourism_touristiccontent_type1
	(touristiccontent_id, touristiccontenttype1_id, uuid)
SELECT
	tc.id, tp.id, "source".uuid
FROM pnc.tourism_touristiccontent_type1 "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristiccontent tc ON csp."name" || '_' || "source".touristiccontent_id = tc.eid
LEFT JOIN tourism_touristiccontenttype tp ON csp."name" || '_' || "source".touristiccontenttype1_id = tp.eid;

-- Insertion TOURISM_TOURISTICCONTENT_TYPE2
INSERT INTO tourism_touristiccontent_type2
	(touristiccontent_id, touristiccontenttype2_id, uuid)
SELECT
	tc.id, tp.id, "source".uuid
FROM pnc.tourism_touristiccontent_type2 "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristiccontent tc ON csp."name" || '_' || "source".touristiccontent_id = tc.eid
LEFT JOIN tourism_touristiccontenttype tp ON csp."name" || '_' || "source".touristiccontenttype2_id = tp.eid;

-- Insertion TOURISM_TOURISTICEVENT
INSERT INTO public.tourism_touristicevent
(date_insert, date_update, deleted, published, publication_date, "name",
review, description_teaser, description, geom, begin_date, end_date, duration,
meeting_point, meeting_time, contact, email, website, organizer, speaker,
accessibility, participant_number, booking, target_audience, practical_info,
approved, structure_id, type_id, target_audience_fr, target_audience_en,
booking_fr, booking_en, published_fr, published_en, practical_info_fr, practical_info_en,
accessibility_fr, accessibility_en, name_fr, name_en, description_fr, description_en,
description_teaser_fr, description_teaser_en, meeting_point_fr, meeting_point_en,
uuid)
SELECT
date_insert, date_update, deleted, published, publication_date, "source"."name",
review, description_teaser, description, geom, begin_date, end_date, duration,
meeting_point, meeting_time, contact, email, website, organizer, speaker,
accessibility, participant_number, booking, target_audience, practical_info,
approved, st.id, t.id, target_audience_fr, target_audience_en,
booking_fr, booking_en, published_fr, published_en, practical_info_fr, practical_info_en,
accessibility_fr, accessibility_en, name_fr, name_en, description_fr, description_en,
description_teaser_fr, description_teaser_en, meeting_point_fr, meeting_point_en,
"source".uuid
FROM pnc.tourism_touristicevent "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM tourism_touristiceventtype a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'tourism_touristiceventtype' AND a."type" ILIKE cc.name_new) t
ON t.bdd_source ILIKE csp."name" AND "source".type_id = t.id_old::integer;


-- Insertion TOURISM_TOURISTICEVENT_PORTAL
INSERT INTO tourism_touristicevent_portal
	(touristicevent_id, targetportal_id, uuid)
SELECT
	tc.id, ctp.id, "source".uuid
FROM pnc.tourism_touristicevent_portal "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristicevent tc ON csp."name" || '_' || "source".touristicevent_id = tc.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_targetportal a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_targetportal' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".targetportal_id = ctp.id_old::integer;

-- Insertion TOURISM_TOURISTICEVENT_SOURCE
INSERT INTO tourism_touristicevent_source
	(touristicevent_id, recordsource_id, uuid)
SELECT
	tc.id, crs.id, "source".uuid
FROM pnc.tourism_touristicevent_source "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristicevent tc ON csp."name" || '_' || "source".touristicevent_id = tc.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_recordsource a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_recordsource' AND a."name" ILIKE cc.name_new) crs
ON crs.bdd_source ILIKE csp."name" AND "source".recordsource_id = crs.id_old::integer;

-- Insertion TOURISM_TOURISTICEVENT_THEMES
INSERT INTO tourism_touristicevent_themes
	(touristicevent_id, theme_id, uuid)
SELECT
	tc.id, cth.id, "source".uuid
FROM pnc.tourism_touristicevent_themes "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN tourism_touristicevent tc ON csp."name" || '_' || "source".touristicevent_id = tc.eid
LEFT JOIN (SELECT a.id, cc.* FROM common_theme a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_theme' AND a."label" ILIKE cc.name_new) cth
ON cth.bdd_source ILIKE csp."name" AND "source".theme_id = cth.id_old::integer;


-- Insertion COMMON_FILETYPE
INSERT INTO common_filetype
	("type", structure_id, uuid)
SELECT "type", st.id, "source".uuid
FROM pnc.common_filetype "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer;


-- Insertion COMMON_ATTACHMENT
INSERT INTO common_attachment
	(object_id, attachment_file, attachment_video, auteur,
	titre, legende, marque, date_insert, date_update,
	content_type_id, creator_id, filetype_id,
	attachment_link, creation_date, is_image,
	uuid)	
SELECT
	ct.id, attachment_file, attachment_video, auteur,
	titre, legende, marque, "source".date_insert, "source".date_update,
	d.id, (SELECT id FROM auth_user WHERE username ILIKE '__internal__') AS creator_id, t.id,
	attachment_link, creation_date, is_image,
	"source".uuid
FROM pnc.common_attachment "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
JOIN core_topology ct ON csp."name" || '_' || "source".object_id = ct.eid
LEFT JOIN pnc.django_content_type d ON d.id = "source".content_type_id
LEFT JOIN common_filetype t ON csp."name" || '_' || "source".filetype_id = t.eid;

-- Insertion CORE_PATH
INSERT INTO core_path
	(date_insert, date_update, geom_3d, length, ascent, descent,
	min_elevation, max_elevation, slope, geom, geom_cadastre, "valid",
	visible, "name", "comments", departure, arrival,
	comfort_id, source_id, stake_id, structure_id, draft, uuid)
SELECT
	date_insert, date_update, geom_3d, length, ascent, descent,
	min_elevation, max_elevation, slope, geom, geom_cadastre, "valid",
	visible, "source"."name", "comments", departure, arrival,
	comfort_id, source_id, stake_id, st.id, draft, "source".uuid
FROM pnc.core_path "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE 'pnc'
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer;
