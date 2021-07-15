import logging


COR_TABLE = {
    'trekking_weblinkcategory': {"label_field": "label"},
    'feedback_reportstatus': {"label_field": "label"},
    'trekking_difficultylevel': {"label_field": "difficulty"},
    'common_theme': {"label_field": "label"},
    'common_recordsource': {"label_field": "name"},
    'tourism_touristiceventtype': {"label_field": "type"},
    'trekking_practice': {"label_field": "name"},
    'feedback_reportactivity': {"label_field": "label"},
    'trekking_accessibility': {"label_field": "name"},
    'common_reservationsystem': {"label_field": "name"},
    'tourism_informationdesktype': {"label_field": "label"},
    'trekking_treknetwork': {"label_field": "network"},
    'common_label': {"label_field": "name"},
    'trekking_route': {"label_field": "route"},
    'authent_structure': {"label_field": "name"},
    'common_targetportal': {"label_field": "name"},
    'trekking_poitype': {"label_field": "label"},
    'feedback_reportproblemmagnitude': {"label_field": "label"},
    'feedback_reportcategory': {"label_field": "label"},
    'tourism_touristiccontentcategory': {"label_field": "label"}
}


TEST_BEFORE_IMPORT =  {
    "trekking_poi": {
        "not_null" : {
            "correspondances_keys" : {
                "structure_id": "authent_structure",
                "type_id": "trekking_poitype"
            }
        }
    },
}

IMPORT_MODEL = {
    "core_topology" : {
        "excluded" : "id"
    },
    "tourism_informationdesk": {
        "excluded" : "id",
        "correspondances_keys" : {
            "type_id" : "tourism_informationdesktype"
        }
    },
    "trekking_poi": {
        "excluded" : "id",
        "correspondances_keys" : {
            "structure_id": "authent_structure",
            "type_id": "trekking_poitype"
        }
    },
    "tourism_touristiccontent": {
        "excluded" : "id",
        "correspondances_keys" : {
            "reservation_system_id": "common_reservationsystem",
            "category_id": "tourism_touristiccontentcategory",
            "structure_id": "authent_structure",
        }
    },
}