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