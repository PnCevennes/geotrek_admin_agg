# coding: utf-8


# Insertion CORE_TOPOLOGY (trek et poi)
core_topology="""
INSERT INTO core_topology
	(id_origine, date_insert, date_update, deleted, geom_3d, length, ascent, descent,
	min_elevation, max_elevation, slope, "offset", kind, geom, geom_need_update, sourceportal_id)
SELECT
	p.id, date_insert, date_update, deleted, geom_3d, length, ascent, descent,
	min_elevation, max_elevation, slope, "offset", kind, geom, geom_need_update, c.id
FROM {source}.core_topology p
JOIN common_sourceportal c ON (kind ILIKE 'poi' OR kind ILIKE 'trek') AND c."name" ILIKE '{source}';
"""

# Insertion TREKKING_POI
trekking_poi="""
INSERT INTO trekking_poi
	(published, publication_date, "name", review,
	topo_object_id, description, eid, structure_id, type_id,
	published_fr, published_en, description_fr,
	description_en, name_fr, name_en,
	id_origine, sourceportal_id)
SELECT
	published, publication_date, "source"."name", review,
	ct.id, description, eid, st.id, tp.id,
	published_fr, published_en, description_fr,
	description_en, name_fr, name_en,
	ct.id_origine, csp.id
FROM {source}.trekking_poi "source"
LEFT JOIN core_topology ct ON ct.id_origine = "source".topo_object_id
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM trekking_poitype a
		   LEFT JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'trekking_poitype' AND a."label" ILIKE cc.name_new) tp
ON tp.bdd_source ILIKE csp."name" AND "source".type_id = tp.id_old::integer;
"""

# Insertion TREKKING_TREK
trekking_trek="""
INSERT INTO trekking_trek
	(published, publication_date, "name", review, topo_object_id, departure, arrival,
	description_teaser, description, ambiance, "access", disabled_infrastructure, duration,
	advised_parking, parking_location, public_transport, advice, points_reference,
	eid, eid2, difficulty_id, practice_id, route_id, structure_id, reservation_id, reservation_system_id,
	arrival_fr, arrival_en, ambiance_fr, ambiance_en, departure_fr, departure_en, access_fr, access_en,
	advised_parking_fr, advised_parking_en, disabled_infrastructure_fr, disabled_infrastructure_en,
	published_fr, published_en, advice_fr, advice_en, name_fr, name_en,
	public_transport_fr, public_transport_en, description_fr, description_en,
	description_teaser_fr, description_teaser_en, id_origine, sourceportal_id)
SELECT
	published, publication_date, "source"."name", review, ct.id, departure, arrival, description_teaser,
	"source".description, ambiance, "access", disabled_infrastructure, duration,
	advised_parking, parking_location,public_transport, advice, points_reference,
	eid, eid2, dl.id, tp.id, tr.id, st.id, reservation_id, crs.id,
	arrival_fr, arrival_en, ambiance_fr,ambiance_en, departure_fr, departure_en, access_fr, access_en,
	advised_parking_fr, advised_parking_en, disabled_infrastructure_fr, disabled_infrastructure_en,
	published_fr, published_en, advice_fr, advice_en, "source".name_fr, "source".name_en,
	public_transport_fr, public_transport_en, "source".description_fr, "source".description_en,
	description_teaser_fr, description_teaser_en, topo_object_id, csp.id
FROM {source}.trekking_trek "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".topo_object_id
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
ON crs.bdd_source ILIKE csp."name" AND "source".structure_id = crs.id_old::integer
"""



# Insertion TREKKING_ORDEREDTREKCHILD
trekking_orderedtrekchild="""
INSERT INTO trekking_orderedtrekchild
	("order", child_id, parent_id, id_origine, sourceportal_id)
SELECT
	"order", ct1.id, ct2.id, "source".id, csp.id
FROM {source}.trekking_orderedtrekchild "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct1 ON ct1.id_origine = "source".child_id AND ct1.sourceportal_id = csp.id
LEFT JOIN core_topology ct2 ON ct2.id_origine = "source".parent_id AND ct2.sourceportal_id = csp.id;
"""


# Insertion TREKKING_TREKRELATIONSHIP
trekking_trekrelationship="""
INSERT INTO trekking_trekrelationship
	(has_common_departure, has_common_edge, is_circuit_step, trek_a_id, trek_b_id, id_origine, sourceportal_id)
SELECT
	has_common_departure, has_common_edge, is_circuit_step, ct1.id, ct2.id, "source".id, csp.id
FROM {source}.trekking_trekrelationship "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct1 ON ct1.id_origine = "source".trek_a_id AND ct1.sourceportal_id = csp.id
LEFT JOIN core_topology ct2 ON ct2.id_origine = "source".trek_b_id AND ct2.sourceportal_id = csp.id;
"""


# Insertion TREKKING_TREK_ACCESSIBILITIES
trekking_trek_accessibilities="""
INSERT INTO trekking_trek_accessibilities
	(trek_id, accessibility_id, id_origine, sourceportal_id)
SELECT
	ct.id, accessibility_id, "source".id, csp.id
FROM {source}.trekking_trek_accessibilities "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM trekking_accessibility a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'trekking_accessibility' AND a."name" ILIKE cc.name_new) ta
ON ta.bdd_source ILIKE csp."name" AND "source".accessibility_id = ta.id_old::integer;
"""


# Insertion TOURISM_INFORMATIONDESK
tourism_informationdesk="""
INSERT INTO tourism_informationdesk
	("name", description, phone, email, website, photo,
	street, postal_code, municipality, geom, type_id,
	description_fr, description_en, name_fr, name_en,
	id_origine, sourceportal_id)
SELECT
	"source"."name", description, phone, email, website, photo,
	street, postal_code, municipality, geom, tid.id,
	description_fr, description_en, name_fr, name_en,
	"source".id, csp.id
FROM {source}.tourism_informationdesk "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN (SELECT a.id, cc.* FROM tourism_informationdesktype a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'tourism_informationdesktype' AND a."label" ILIKE cc.name_new) tid
ON tid.bdd_source ILIKE csp."name" AND "source".type_id = tid.id_old::integer;
"""


# Insertion TREKKING_TREK_INFORMATIONDESKS
trekking_trek_information_desks="""
INSERT INTO trekking_trek_information_desks
	(trek_id, informationdesk_id, id_origine, sourceportal_id)
SELECT
	ct.id, tid.id, "source".id, csp.id
FROM {source}.trekking_trek_information_desks "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN tourism_informationdesk tid ON tid.id_origine = "source".informationdesk_id AND tid.sourceportal_id = csp.id;
"""


# Insertion TREKKING_TREK_NETWORKS
trekking_trek_networks="""
INSERT INTO trekking_trek_networks
	(trek_id, treknetwork_id, id_origine, sourceportal_id)
SELECT
	ct.id, ttn.id, "source".id, csp.id
FROM {source}.trekking_trek_networks "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM trekking_treknetwork a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'trekking_treknetwork' AND a."network" ILIKE cc.name_new) ttn
ON ttn.bdd_source ILIKE csp."name" AND "source".treknetwork_id = ttn.id_old::integer;
"""


# Insertion TREKKING_TREK_PORTAL
trekking_trek_portal="""
INSERT INTO trekking_trek_portal
	(trek_id, targetportal_id, id_origine, sourceportal_id)	
SELECT
	ct.id, ctp.id, "source".id, csp.id
FROM {source}.trekking_trek_portal "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_targetportal a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_targetportal' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".targetportal_id = ctp.id_old::integer;
"""


# Insertion TREKKING_TREK_SOURCE
trekking_trek_source="""
INSERT INTO trekking_trek_source
	(trek_id, recordsource_id, id_origine, sourceportal_id)		
SELECT
	ct.id, ctp.id, "source".id, csp.id
FROM {source}.trekking_trek_source "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_recordsource a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_recordsource' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".recordsource_id = ctp.id_old::integer;
"""


# Insertion TREKKING_TREK_THEMES
trekking_trek_themes="""
INSERT INTO trekking_trek_themes
	(trek_id, theme_id, id_origine, sourceportal_id)
SELECT
	ct.id, cth.id, "source".id, csp.id
FROM {source}.trekking_trek_themes "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_theme a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_theme' AND a."label" ILIKE cc.name_new) cth
ON cth.bdd_source ILIKE csp."name" AND "source".theme_id = cth.id_old::integer;
"""


# Insertion TREKKING_WEBLINK
trekking_weblink="""
INSERT INTO trekking_weblink
	("name", url, category_id, name_en, name_fr, id_origine, sourceportal_id)
SELECT
	"source"."name", url, twl.id, name_en, name_fr, "source".id, csp.id
FROM {source}.trekking_weblink "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN (SELECT a.id, cc.* FROM trekking_weblinkcategory a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'trekking_weblinkcategory' AND a."label" ILIKE cc.name_new) twl
ON twl.bdd_source ILIKE csp."name" AND "source".category_id = twl.id_old::integer;
"""


# Insertion TREKKING_TREK_WEB_LINKS
trekking_trek_web_links="""
INSERT INTO trekking_trek_web_links
	(trek_id, weblink_id, id_origine, sourceportal_id)	
SELECT
	ct.id, twl.id, "source".id, csp.id
FROM {source}.trekking_trek_web_links "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN trekking_weblink twl ON twl.id_origine = "source".weblink_id AND ct.sourceportal_id = csp.id;
"""


# Insertion TREKKING_TREK_LABELS
trekking_trek_labels="""
INSERT INTO trekking_trek_labels
	(trek_id, label_id, id_origine, sourceportal_id)
SELECT
	ct.id, cl.id, "source".id, csp.id
FROM {source}.trekking_trek_labels "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".trek_id AND ct.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_label a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_label' AND a."name" ILIKE cc.name_new) cl
ON cl.bdd_source ILIKE csp."name" AND "source".label_id = cl.id_old::integer;
"""


# Insertion TREKKING_TREK_POIS_EXCLUDED
trekking_trek_pois_excluded="""
INSERT INTO trekking_trek_pois_excluded
	(trek_id, poi_id, id_origine, sourceportal_id)
SELECT
	t.topo_object_id, p.topo_object_id, "source".id, csp.id
FROM {source}.trekking_trek_pois_excluded "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN trekking_trek t ON t.id_origine = "source".trek_id AND t.sourceportal_id = csp.id
LEFT JOIN trekking_poi p ON p.id_origine = "source".poi_id AND p.sourceportal_id = csp.id;
"""

# Insertion FEEDBACK_REPORT
feedback_report="""
INSERT INTO feedback_report
	(date_insert, date_update, email, "comment", geom, category_id, status_id,
	activity_id, problem_magnitude_id, related_trek_id, id_origine, sourceportal_id)	
SELECT
	"source".date_insert, "source".date_update, email, "comment", "source".geom, frc.id, frs.id,
	fra.id, frp.id, ct.id, "source".id, csp.id
FROM {source}.feedback_report "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN core_topology ct ON ct.id_origine = "source".related_trek_id AND ct.sourceportal_id = csp.id
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
"""

# Insertion TOURISM_TOURISTICCONTENT
tourism_touristiccontent="""
INSERT INTO tourism_touristiccontent
	(date_insert, date_update, deleted, published, publication_date,
	"name", review, description_teaser, description, geom, contact,
	email, website, practical_info, eid, reservation_id, approved,
	category_id, reservation_system_id, structure_id, published_fr,
	published_en, practical_info_fr, practical_info_en, name_fr,
	name_en, description_fr, description_en, description_teaser_fr, description_teaser_en, id_origine, sourceportal_id)
SELECT
	date_insert, date_update, deleted, published, publication_date,
	"source"."name", review, description_teaser, description, geom, contact,
	email, website, practical_info, eid, reservation_id, approved,
	cat.id, crs.id, st.id, published_fr,
	published_en, practical_info_fr, practical_info_en, name_fr,
	name_en, description_fr, description_en, description_teaser_fr, description_teaser_en, "source".id, csp.id
FROM {source}.tourism_touristiccontent "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
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
"""

# Insertion TOURISM_TOURISTICCONTENTTYPE
tourism_touristiccontenttype="""
INSERT INTO tourism_touristiccontenttype
	(pictogram, "label", in_list, category_id, label_fr, label_en, id_origine, sourceportal_id)
SELECT
	pictogram, "label", in_list, cat.id, label_fr, label_en, "source".id, csp.id
FROM {source}.tourism_touristiccontenttype "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN (SELECT a.id, cc.* FROM tourism_touristiccontentcategory a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'tourism_touristiccontentcategory' AND a."label" ILIKE cc.name_new) cat
ON cat.bdd_source ILIKE csp."name" AND "source".category_id = cat.id_old::integer;
"""


# Insertion TOURISM_TOURISTICCONTENT_PORTAL
tourism_touristiccontent_portal="""
INSERT INTO tourism_touristiccontent_portal
	(touristiccontent_id, targetportal_id, id_origine, sourceportal_id)
SELECT
	tc.id, ctp.id, "source".id, csp.id
FROM {source}.tourism_touristiccontent_portal "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristiccontent tc ON tc.id_origine = "source".touristiccontent_id AND tc.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_targetportal a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_targetportal' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".targetportal_id = ctp.id_old::integer;
"""


# Insertion TOURISM_TOURISTICCONTENT_SOURCE
tourism_touristiccontent_source="""
INSERT INTO tourism_touristiccontent_source
	(touristiccontent_id, recordsource_id, id_origine, sourceportal_id)
SELECT
	tc.id, crs.id, "source".id, csp.id
FROM {source}.tourism_touristiccontent_source "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristiccontent tc ON tc.id_origine = "source".touristiccontent_id AND tc.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_recordsource a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_recordsource' AND a."name" ILIKE cc.name_new) crs
ON crs.bdd_source ILIKE csp."name" AND "source".recordsource_id = crs.id_old::integer;
"""


# Insertion TOURISM_TOURISTICCONTENT_THEMES
tourism_touristiccontent_themes="""
INSERT INTO tourism_touristiccontent_themes
	(touristiccontent_id, theme_id, id_origine, sourceportal_id)
SELECT
	tc.id, cth.id, "source".id, csp.id
FROM {source}.tourism_touristiccontent_themes "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristiccontent tc ON tc.id_origine = "source".touristiccontent_id AND tc.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_theme a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_theme' AND a."label" ILIKE cc.name_new) cth
ON cth.bdd_source ILIKE csp."name" AND "source".theme_id = cth.id_old::integer;
"""


# Insertion TOURISM_TOURISTICCONTENT_TYPE1
tourism_touristiccontent_type1="""
INSERT INTO tourism_touristiccontent_type1
	(touristiccontent_id, touristiccontenttype1_id, id_origine, sourceportal_id)
SELECT
	tc.id, tp.id, "source".id, csp.id
FROM {source}.tourism_touristiccontent_type1 "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristiccontent tc ON tc.id_origine = "source".touristiccontent_id AND tc.sourceportal_id = csp.id
LEFT JOIN tourism_touristiccontenttype tp ON tp.id_origine = "source".touristiccontenttype1_id AND tp.sourceportal_id = csp.id;
"""


# Insertion TOURISM_TOURISTICCONTENT_TYPE2
tourism_touristiccontent_type2="""
INSERT INTO tourism_touristiccontent_type2
	(touristiccontent_id, touristiccontenttype2_id, id_origine, sourceportal_id)
SELECT
	tc.id, tp.id, "source".id, csp.id
FROM {source}.tourism_touristiccontent_type2 "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristiccontent tc ON tc.id_origine = "source".touristiccontent_id AND tc.sourceportal_id = csp.id
LEFT JOIN tourism_touristiccontenttype tp ON tp.id_origine = "source".touristiccontenttype2_id AND tp.sourceportal_id = csp.id;
"""


# Insertion TOURISM_TOURISTICEVENT
tourism_touristicevent="""
INSERT INTO public.tourism_touristicevent
(date_insert, date_update, deleted, published, publication_date, "name",
review, description_teaser, description, geom, begin_date, end_date, duration,
meeting_point, meeting_time, contact, email, website, organizer, speaker,
accessibility, participant_number, booking, target_audience, practical_info,
eid, approved, structure_id, type_id, target_audience_fr, target_audience_en,
booking_fr, booking_en, published_fr, published_en, practical_info_fr, practical_info_en,
accessibility_fr, accessibility_en, name_fr, name_en, description_fr, description_en,
description_teaser_fr, description_teaser_en, meeting_point_fr, meeting_point_en,
id_origine, sourceportal_id)
SELECT
date_insert, date_update, deleted, published, publication_date, "source"."name",
review, description_teaser, description, geom, begin_date, end_date, duration,
meeting_point, meeting_time, contact, email, website, organizer, speaker,
accessibility, participant_number, booking, target_audience, practical_info,
eid, approved, st.id, t.id, target_audience_fr, target_audience_en,
booking_fr, booking_en, published_fr, published_en, practical_info_fr, practical_info_en,
accessibility_fr, accessibility_en, name_fr, name_en, description_fr, description_en,
description_teaser_fr, description_teaser_en, meeting_point_fr, meeting_point_en,
"source".id, csp.id
FROM {source}.tourism_touristicevent "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer
LEFT JOIN (SELECT a.id, cc.* FROM tourism_touristiceventtype a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'tourism_touristiceventtype' AND a."type" ILIKE cc.name_new) t
ON t.bdd_source ILIKE csp."name" AND "source".type_id = t.id_old::integer;
"""


# Insertion TOURISM_TOURISTICEVENT_PORTAL
tourism_touristicevent_portal="""
INSERT INTO tourism_touristicevent_portal
	(touristicevent_id, targetportal_id, id_origine, sourceportal_id)
SELECT
	tc.id, ctp.id, "source".id, csp.id
FROM {source}.tourism_touristicevent_portal "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristicevent tc ON tc.id_origine = "source".touristicevent_id AND tc.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_targetportal a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_targetportal' AND a."name" ILIKE cc.name_new) ctp
ON ctp.bdd_source ILIKE csp."name" AND "source".targetportal_id = ctp.id_old::integer;
"""


# Insertion TOURISM_TOURISTICEVENT_SOURCE
tourism_touristicevent_source="""
INSERT INTO tourism_touristicevent_source
	(touristicevent_id, recordsource_id, id_origine, sourceportal_id)
SELECT
	tc.id, crs.id, "source".id, csp.id
FROM {source}.tourism_touristicevent_source "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristicevent tc ON tc.id_origine = "source".touristicevent_id AND tc.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_recordsource a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_recordsource' AND a."name" ILIKE cc.name_new) crs
ON crs.bdd_source ILIKE csp."name" AND "source".recordsource_id = crs.id_old::integer;
"""


# Insertion TOURISM_TOURISTICEVENT_THEMES
tourism_touristicevent_themes="""
INSERT INTO tourism_touristicevent_themes
	(touristicevent_id, theme_id, id_origine, sourceportal_id)
SELECT
	tc.id, cth.id, "source".id, csp.id
FROM {source}.tourism_touristicevent_themes "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN tourism_touristicevent tc ON tc.id_origine = "source".touristicevent_id AND tc.sourceportal_id = csp.id
LEFT JOIN (SELECT a.id, cc.* FROM common_theme a
			JOIN common_correspondances cc
			ON cc.table_name ILIKE 'common_theme' AND a."label" ILIKE cc.name_new) cth
ON cth.bdd_source ILIKE csp."name" AND "source".theme_id = cth.id_old::integer;
"""


# Insertion COMMON_FILETYPE
common_filetype="""
INSERT INTO common_filetype
	("type", structure_id, id_origine, sourceportal_id)
SELECT "type", st.id, "source".id, csp.id
FROM {source}.common_filetype "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN (SELECT a.id, cc.* FROM authent_structure a
		   JOIN common_correspondances cc
		   ON cc.table_name ILIKE 'authent_structure' AND a."name" ILIKE cc.name_new) st
ON st.bdd_source ILIKE csp."name" AND "source".structure_id = st.id_old::integer;
"""


# Insertion AUTH_USER
auth_user="""
INSERT INTO auth_user
	("password", last_login, is_superuser, username,
	first_name, last_name, email, is_staff, is_active,
	date_joined, id_origine, sourceportal_id)	
SELECT
	"password", last_login, is_superuser, "source".username,
	first_name, last_name, email, is_staff, is_active,
	date_joined, "source".id, csp.id
FROM {source}.auth_user "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
JOIN (SELECT username FROM auth_user) a ON a.username NOT LIKE "source".username;
"""


# Insertion COMMON_ATTACHMENT
common_attachment="""
INSERT INTO public.common_attachment
	(object_id, attachment_file, attachment_video, auteur,
	titre, legende, marque, date_insert, date_update,
	content_type_id, creator_id, filetype_id,
	attachment_link, creation_date, is_image,
	id_origine, sourceportal_id)	
SELECT
	object_id, attachment_file, attachment_video, auteur,
	titre, legende, marque, date_insert, date_update,
	d.id, us.id, t.id,
	attachment_link, creation_date, is_image,
	"source".id, csp.id
FROM {source}.common_attachment "source"
LEFT JOIN common_sourceportal csp ON csp."name" ILIKE '{source}'
LEFT JOIN {source}.django_content_type d ON d.id = "source".content_type_id
LEFT JOIN auth_user us ON us.id_origine = "source".creator_id AND us.sourceportal_id = csp.id
LEFT JOIN common_filetype t ON t.id_origine = "source".filetype_id AND t.sourceportal_id = csp.id;
"""


queries = [core_topology, trekking_poi, trekking_trek,
trekking_orderedtrekchild, trekking_trekrelationship, trekking_trek_accessibilities,
tourism_informationdesk, trekking_trek_information_desks, trekking_trek_networks,
trekking_trek_portal, trekking_trek_source, trekking_trek_themes, trekking_weblink,
trekking_trek_web_links, trekking_trek_labels, trekking_trek_pois_excluded, feedback_report,
tourism_touristiccontent, tourism_touristiccontenttype, tourism_touristiccontent_portal,
tourism_touristiccontent_source, tourism_touristiccontent_themes, tourism_touristiccontent_type1,
tourism_touristiccontent_type2, tourism_touristicevent, tourism_touristicevent_portal,
tourism_touristicevent_source,tourism_touristicevent_themes, common_filetype, auth_user, common_attachment]