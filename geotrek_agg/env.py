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
    'tourism_touristiccontentcategory': {"label_field": "label"},
    'common_filetype':  {"label_field": "type"}
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


# Liste "ordonnée" des tables à importer
# excluded : () liste des champs à exclure de l'import TODO devrait être une liste voir
#   si l'absence de la clé ne pourrait pas juste signaler que la colonne à exclure est id
# correspondances_keys : table_dictionaire = liste des champs relié à un élément de "vocabulaire"
# foreign_key TODO gestion des clés étrangères de type table d'import (exemple topo_object_id)
IMPORT_MODEL = {
    "core_topology": {
        "excluded": "id"
    },
    "tourism_informationdesk": {
        "excluded": "id",
        "correspondances_keys": {
            "type_id": "tourism_informationdesktype"
        },
        "filters": {
            "not_null": ["type_id"]
        },
    },
    "trekking_poi": {
        "correspondances_keys": {
            "structure_id": "authent_structure",
            "type_id": "trekking_poitype"
        },
        "filters": {
            "not_null": ["type_id", "structure_id"]
        },
        "foreign_keys": {
            "topo_object_id": {
                "table": "core_topology",
                "col": "id"
            }
        }
    },
    "trekking_trek": {
        "primary_key" : "topo_object_id",
        "correspondances_keys": {
            "practice_id": "trekking_practice",
            "difficulty_id": "trekking_difficultylevel",
            "route_id": "trekking_route",
            "structure_id": "authent_structure",
            "reservation_system_id": "common_reservationsystem"
        },
        "filters": {
        },
        "foreign_keys": {
            "topo_object_id": {
                "table": "core_topology",
                "col": "id"
            }
        },
        "cor_tables": {
           "trekking_trek_accessibilities": {
               "key": "trek_id",
                "correspondances_keys": {
                    "accessibility_id": "trekking_accessibility",
                },
           },
           "trekking_trek_information_desks" : {
               "key": "trek_id",
                "correspondances_keys": {
                    "informationdesk_id": "tourism_informationdesk",
                },
           },
           "trekking_trek_networks" : {
               "key": "trek_id",
                "correspondances_keys": {
                    "treknetwork_id": "trekking_treknetwork",
                },
           },
           "trekking_trek_portal" : {
               "key": "trek_id",
                "correspondances_keys": {
                    "targetportal_id": "common_targetportal",
                },
           },
           "trekking_trek_source" : {
               "key": "trek_id",
                "correspondances_keys": {
                    "recordsource_id": "common_recordsource",
                },
           },
           "trekking_trek_themes" : {
               "key": "trek_id",
                "correspondances_keys": {
                    "theme_id": "common_theme",
                },
           },
           "trekking_trek_web_links" : {
               "key": "weblink_id",
                "correspondances_keys": {
                    "weblink_id": "common_sourceportal",
                },
           },
           "trekking_trek_labels" : {
               "key": "trek_id",
                "correspondances_keys": {
                    "label_id": "common_label",
                },
           },
        }
    },
    "trekking_orderedtrekchild": {
        "excluded": "id",
        "foreign_keys": {
            "child_id": {
                "table": "trekking_trek",
                "col": "topo_object_id"
            },
            "parent_id": {
                "table": "trekking_trek",
                "col": "topo_object_id"
            }
        },
        "filters": {
            "not_null": ["child_id", "parent_id"]
        },
    },
    "trekking_trekrelationship": {
        "excluded": "id",
        "foreign_keys": {
            "trek_a_id": {
                "table": "trekking_trek",
                "col": "topo_object_id"
            },
            "trek_b_id": {
                "table": "trekking_trek",
                "col": "topo_object_id"
            }
        },
        "filters": {
            "not_null": ["trek_a_id", "trek_b_id"]
        },
    },
    "trekking_trek_pois_excluded": {
        "excluded": "id",
        "foreign_keys": {
            "trek_id": {
                "table": "trekking_trek",
                "col": "topo_object_id"
            },
            "poi_id": {
                "table": "trekking_poi",
                "col": "topo_object_id"
            }
        },
        "filters": {
            "not_null": ["trek_id", "poi_id"]
        },
    },
    "tourism_touristiccontent": {
        "excluded": "id",
        "correspondances_keys": {
            "reservation_system_id": "common_reservationsystem",
            "category_id": "tourism_touristiccontentcategory",
            "structure_id": "authent_structure",
        },
        "filters": {
            "not_null": ["category_id", "structure_id"]
        },
    },
}