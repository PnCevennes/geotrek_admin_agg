import logging


CAT_TABLE = {
    'authent_structure': {"label_field": "name"},
    'common_label': {"label_field": "name"},
    'common_reservationsystem': {"label_field": "name"},
    'common_targetportal': {"label_field": "name"},
    'common_theme': {"label_field": "label"},
    'common_recordsource': {"label_field": "name"},
    'common_organism': {"label_field": "organism"},
    'common_filetype':  {"label_field": "type"},
    'feedback_reportstatus': {"label_field": "label"},
    'feedback_reportactivity': {"label_field": "label"},
    'feedback_reportproblemmagnitude': {"label_field": "label"},
    'feedback_reportcategory': {"label_field": "label"},
    'trekking_weblinkcategory': {"label_field": "label"},
    'trekking_difficultylevel': {"label_field": "difficulty"},
    'trekking_practice': {"label_field": "name"},
    'trekking_accessibility': {"label_field": "name"},
    'trekking_treknetwork': {"label_field": "network"},
    'trekking_route': {"label_field": "route"},
    'trekking_poitype': {"label_field": "label"},
    'tourism_touristiceventtype': {"label_field": "type"},
    'tourism_informationdesktype': {"label_field": "label"},
    'tourism_touristiccontentcategory': {"label_field": "label"},
    'tourism_touristiccontenttype': {"label_field": "label"},
    'signage_sealing': {"label_field": "label"},
    'signage_signagetype': {"label_field": "label"},
    'signage_color': {"label_field": "label"},
    'signage_direction': {"label_field": "label"},
    'signage_bladetype': {"label_field": "label"},
    'infrastructure_infrastructurecondition': {"label_field": "label"},
    'django_content_type': {"label_field": "model"}
}


TEST_BEFORE_IMPORT = {
    "trekking_poi": {
        "not_null" : {
            "category_keys" : {
                "structure_id": "authent_structure",
                "type_id": "trekking_poitype"
            }
        }
    },
}
# Liste "ordonnée" des tables à importer
# excluded : () liste des champs à exclure de l'import TODO devrait être une liste voir
#   si l'absence de la clé ne pourrait pas juste signaler que la colonne à exclure est id
# category_keys : table_dictionaire = liste des champs relié à un élément de "vocabulaire"
# foreign_key TODO gestion des clés étrangères de type table d'import (exemple topo_object_id)
IMPORT_MODEL = {
    "core_topology": {
        "excluded": "id",
    },
    "tourism_informationdesk": {
        "excluded": "id",
        "category_keys": {
            "type_id": "tourism_informationdesktype"
        },
        "filters": {
            "not_null": ["type_id"]
        },
    },
    "trekking_weblink": {
        "excluded": "id",
        "category_keys": {
            "category_id": "trekking_weblinkcategory"
        },
        "filters": {
            "not_null": ["category_id"]
        },
    },
    "trekking_poi": {
        "primary_key": "topo_object_id",
        "common_attachment": "true",
        "category_keys": {
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
        "common_attachment": "true",
        "category_keys": {
            "practice_id": "trekking_practice",
            "difficulty_id": "trekking_difficultylevel",
            "route_id": "trekking_route",
            "structure_id": "authent_structure",
            "reservation_system_id": "common_reservationsystem"
        },
        "filters": {
            "not_null": ["structure_id"]
        },
        "foreign_keys": {
            "topo_object_id": {
                "table": "core_topology",
                "col": "id"
            }
        },
        "cor_tables": {
            "trekking_trek_accessibilities": {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "accessibility_id": "trekking_accessibility",
                },
            },
            "trekking_trek_information_desks" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "informationdesk_id": "tourism_informationdesk",
                },
            },
            "trekking_trek_networks" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "treknetwork_id": "trekking_treknetwork",
                },
            },
            "trekking_trek_portal" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "targetportal_id": "common_targetportal",
                },
            },
            "trekking_trek_source" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "recordsource_id": "common_recordsource",
                },
            },
            "trekking_trek_themes" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "theme_id": "common_theme",
                },
            },
            "trekking_trek_web_links" : {
                "excluded": "id",
                "key": "weblink_id",
                "category_keys": {
                    "weblink_id": "common_sourceportal",
                },
            },
            "trekking_trek_labels" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "label_id": "common_label",
                },
            },
            "trekking_trek_pois_excluded" : {
                "excluded": "id",
                "key": "trek_id",
                "category_keys": {
                    "poi_id": "trekking_poi",
                },
            },
            "trekking_orderedtrekchild" : {
                "excluded": "id",
                "key": "child_id",
                "category_keys": {
                    "parent_id": "trekking_trek",
                },
            },
            "trekking_trekrelationship" : {
                "excluded": "id",
                "key": "trek_a_id",
                "category_keys": {
                    "trek_b_id": "trekking_trek",
                },
            },
        }
    },
    "feedback_report": {
        "excluded": "id",
        "category_keys": {
            "category_id": "feedback_reportcategory",
            "status_id": "feedback_reportstatus",
            "activity_id": "feedback_reportactivity",
            "problem_magnitude_id": "feedback_reportproblemmagnitude",
            "related_trek_id": "trekking_trek",
        },
        "filters": {
            "not_null": [
                "date_insert",
                "date_update",
                "email",
                "comment",
            ]
        },
    },
    "tourism_touristiccontent": {
        "primary_key" : "id",
        "common_attachment": "true",
        "excluded": "id",
        "category_keys": {
            "reservation_system_id": "common_reservationsystem",
            "category_id": "tourism_touristiccontentcategory",
            "structure_id": "authent_structure",
        },
        "filters": {
            "not_null": [
                "reservation_id",
                "category_id"
            ]
        },
        "cor_tables": {
            "tourism_touristiccontent_portal": {
                "excluded": "id",
                "key": "touristiccontent_id",
                "category_keys": {
                    "targetportal_id": "common_targetportal",
                },
            },
            "tourism_touristiccontent_source" : {
                "excluded": "id",
                "key": "touristiccontent_id",
                "category_keys": {
                    "recordsource_id": "common_recordsource",
                },
            },
            "tourism_touristiccontent_themes" : {
                "excluded": "id",
                "key": "touristiccontent_id",
                "category_keys": {
                    "theme_id": "common_theme",
                },
            },
            "tourism_touristiccontent_type1" : {
                "excluded": "id",
                "key": "touristiccontent_id",
                "category_keys": {
                    "touristiccontenttype1_id": "tourism_touristiccontenttype",
                },
            },
            "tourism_touristiccontent_type2" : {
                "excluded": "id",
                "key": "touristiccontent_id",
                "category_keys": {
                    "touristiccontenttype2_id": "tourism_touristiccontenttype",
                },
            },
        }
    },
    "tourism_touristicevent": {
        "primary_key" : "id",
        "common_attachment": "true",
        "excluded": "id",
        "category_keys": {
            "type_id": "common_reservationsystem",
            "structure_id": "authent_structure",
        },
        "filters": {
            "not_null": [
                "structure_id"
            ]
        },
        "cor_tables": {
            "tourism_touristicevent_portal": {
                "excluded": "id",
                "key": "touristicevent_id",
                "category_keys": {
                    "targetportal_id": "common_targetportal",
                },
            },
            "tourism_touristicevent_source" : {
                "excluded": "id",
                "key": "touristicevent_id",
                "category_keys": {
                    "recordsource_id": "common_recordsource",
                },
            },
            "tourism_touristicevent_themes" : {
                "excluded": "id",
                "key": "touristicevent_id",
                "category_keys": {
                    "theme_id": "common_theme",
                },
            },
        }
    },
    "signage_signage": {
        "category_keys": {
            "manager_id": "common_organism",
            "condition_id": "infrastructure_infrastructurecondition",
            "sealing_id": "signage_sealing",
            "structure_id": "authent_structure",
            "type_id": "signage_signagetype"
        },
        "filters": {
            "not_null": [
                "topo_object_id",
                "structure_id",
                "type_id"
            ]
        },
        "foreign_keys": {
            "topo_object_id": {
                "table": "core_topology",
                "col": "id"
            }
        }
    },
    "signage_blade": {
        "excluded": "id",
        "category_keys": {
            "topology_id": "core_topology",
            "type_id": "signage_bladetype",
            "color_id": "signage_color",
            "condition_id": "infrastructure_infrastructurecondition",
            "direction_id": "signage_direction",
        },
        "filters": {
            "not_null": [
                "topology_id",
                "type_id",
                "direction_id",
                "signage_id",
            ]
        },
        "foreign_keys": {
            "signage_id": {
                "table": "signage_signage",
                "col": "topo_object_id"
            }
        }
    },
    "signage_line": {
        "excluded": "id",
        "foreign_keys": {
            "blade_id": {
                "table": "signage_blade",
                "col": "id"
            }
        },
        "filters": {
            "not_null": [
                "blade_id"
            ]
        }
    }
}