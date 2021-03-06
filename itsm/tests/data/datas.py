# -*- coding: utf-8 -*-
DATA = {
    "is_deleted": False,
    "name": "\u57fa\u7840\u5ba1\u6279\u6d4b\u8bd5",
    "desc": "",
    "flow_type": "other",
    "is_enabled": True,
    "is_revocable": True,
    "revoke_config": {"type": 2, "state": 0},
    "is_draft": False,
    "is_builtin": False,
    "is_task_needed": False,
    "owners": ",admin,",
    "notify_rule": "NONE",
    "notify_freq": 0,
    "is_biz_needed": False,
    "is_auto_approve": False,
    "is_iam_used": False,
    "is_supervise_needed": False,
    "supervise_type": "EMPTY",
    "supervisor": "",
    "engine_version": "PIPELINE_V1",
    "version_number": "20211221162328",
    "table": {
        "id": 1,
        "is_deleted": False,
        "name": "\u9ed8\u8ba4",
        "desc": "\u9ed8\u8ba4\u57fa\u7840\u6a21\u578b",
        "version": "EMPTY",
        "fields": [
            {
                "id": 1,
                "is_deleted": False,
                "is_builtin": True,
                "is_readonly": False,
                "is_valid": True,
                "display": True,
                "source_type": "CUSTOM",
                "source_uri": "",
                "api_instance_id": 0,
                "kv_relation": {},
                "type": "STRING",
                "key": "title",
                "name": "\u6807\u9898",
                "layout": "COL_12",
                "validate_type": "REQUIRE",
                "show_type": 1,
                "show_conditions": {},
                "regex": "EMPTY",
                "regex_config": {},
                "custom_regex": "",
                "desc": "\u8bf7\u8f93\u5165\u6807\u9898",
                "tips": "",
                "is_tips": False,
                "default": "",
                "choice": [],
                "related_fields": {},
                "meta": {},
                "flow_type": "DEFAULT",
                "source": "BASE-MODEL",
            },
            {
                "id": 2,
                "is_deleted": False,
                "is_builtin": True,
                "is_readonly": False,
                "is_valid": True,
                "display": True,
                "source_type": "DATADICT",
                "source_uri": "IMPACT",
                "api_instance_id": 0,
                "kv_relation": {},
                "type": "SELECT",
                "key": "impact",
                "name": "\u5f71\u54cd\u8303\u56f4",
                "layout": "COL_12",
                "validate_type": "REQUIRE",
                "show_type": 1,
                "show_conditions": {},
                "regex": "EMPTY",
                "regex_config": {},
                "custom_regex": "",
                "desc": "\u8bf7\u9009\u62e9\u5f71\u54cd\u8303\u56f4",
                "tips": "",
                "is_tips": False,
                "default": "",
                "choice": [],
                "related_fields": {},
                "meta": {},
                "flow_type": "DEFAULT",
                "source": "BASE-MODEL",
            },
            {
                "id": 3,
                "is_deleted": False,
                "is_builtin": True,
                "is_readonly": False,
                "is_valid": True,
                "display": True,
                "source_type": "DATADICT",
                "source_uri": "URGENCY",
                "api_instance_id": 0,
                "kv_relation": {},
                "type": "SELECT",
                "key": "urgency",
                "name": "\u7d27\u6025\u7a0b\u5ea6",
                "layout": "COL_12",
                "validate_type": "REQUIRE",
                "show_type": 1,
                "show_conditions": {},
                "regex": "EMPTY",
                "regex_config": {},
                "custom_regex": "",
                "desc": "\u8bf7\u9009\u62e9\u7d27\u6025\u7a0b\u5ea6",
                "tips": "",
                "is_tips": False,
                "default": "",
                "choice": [],
                "related_fields": {},
                "meta": {},
                "flow_type": "DEFAULT",
                "source": "BASE-MODEL",
            },
            {
                "id": 4,
                "is_deleted": False,
                "is_builtin": True,
                "is_readonly": True,
                "is_valid": True,
                "display": True,
                "source_type": "DATADICT",
                "source_uri": "PRIORITY",
                "api_instance_id": 0,
                "kv_relation": {},
                "type": "SELECT",
                "key": "priority",
                "name": "\u4f18\u5148\u7ea7",
                "layout": "COL_12",
                "validate_type": "REQUIRE",
                "show_type": 1,
                "show_conditions": {},
                "regex": "EMPTY",
                "regex_config": {},
                "custom_regex": "",
                "desc": "\u8bf7\u9009\u62e9\u4f18\u5148\u7ea7",
                "tips": "",
                "is_tips": False,
                "default": "",
                "choice": [],
                "related_fields": {"rely_on": ["urgency", "impact"]},
                "meta": {},
                "flow_type": "DEFAULT",
                "source": "BASE-MODEL",
            },
            {
                "id": 5,
                "is_deleted": False,
                "is_builtin": True,
                "is_readonly": False,
                "is_valid": True,
                "display": True,
                "source_type": "RPC",
                "source_uri": "ticket_status",
                "api_instance_id": 0,
                "kv_relation": {},
                "type": "SELECT",
                "key": "current_status",
                "name": "\u5de5\u5355\u72b6\u6001",
                "layout": "COL_12",
                "validate_type": "REQUIRE",
                "show_type": 1,
                "show_conditions": {},
                "regex": "EMPTY",
                "regex_config": {},
                "custom_regex": "",
                "desc": "\u8bf7\u9009\u62e9\u5de5\u5355\u72b6\u6001",
                "tips": "",
                "is_tips": False,
                "default": "",
                "choice": [],
                "related_fields": {},
                "meta": {},
                "flow_type": "DEFAULT",
                "source": "BASE-MODEL",
            },
        ],
        "fields_order": [1, 2, 3, 4, 5],
        "field_key_order": ["title", "impact", "urgency", "priority", "current_status"],
    },
    "task_schemas": [],
    "creator": "admin",
    "updated_by": "admin",
    "workflow_id": 65,
    "version_message": "",
    "states": {
        "267": {
            "workflow": 65,
            "id": 267,
            "key": 267,
            "name": "\u5f00\u59cb",
            "desc": "",
            "distribute_type": "PROCESS",
            "axis": {"x": 150, "y": 150},
            "is_builtin": True,
            "variables": {"inputs": [], "outputs": []},
            "tag": "DEFAULT",
            "processors_type": "OPEN",
            "processors": "",
            "assignors": "",
            "assignors_type": "EMPTY",
            "delivers": "",
            "delivers_type": "EMPTY",
            "can_deliver": False,
            "extras": {},
            "is_draft": False,
            "is_terminable": False,
            "fields": [],
            "type": "START",
            "api_instance_id": 0,
            "is_sequential": False,
            "finish_condition": {},
            "is_multi": False,
            "is_allow_skip": False,
            "creator": None,
            "create_at": "2021-12-21 16:22:41",
            "updated_by": None,
            "update_at": "2021-12-21 16:22:41",
            "end_at": None,
            "is_first_state": False,
        },
        "268": {
            "workflow": 65,
            "id": 268,
            "key": 268,
            "name": "\u63d0\u5355",
            "desc": "",
            "distribute_type": "PROCESS",
            "axis": {"x": 285, "y": 150},
            "is_builtin": True,
            "variables": {"inputs": [], "outputs": []},
            "tag": "DEFAULT",
            "processors_type": "OPEN",
            "processors": "",
            "assignors": "",
            "assignors_type": "EMPTY",
            "delivers": "",
            "delivers_type": "EMPTY",
            "can_deliver": False,
            "extras": {},
            "is_draft": False,
            "is_terminable": False,
            "fields": [388, 389, 390, 391],
            "type": "NORMAL",
            "api_instance_id": 0,
            "is_sequential": False,
            "finish_condition": {},
            "is_multi": False,
            "is_allow_skip": False,
            "creator": None,
            "create_at": "2021-12-21 16:22:41",
            "updated_by": None,
            "update_at": "2021-12-21 16:22:41",
            "end_at": None,
            "is_first_state": False,
        },
        "269": {
            "workflow": 65,
            "id": 269,
            "key": 269,
            "name": "\u7ed3\u675f",
            "desc": "",
            "distribute_type": "PROCESS",
            "axis": {"x": 1315, "y": 155},
            "is_builtin": True,
            "variables": {"inputs": [], "outputs": []},
            "tag": "DEFAULT",
            "processors_type": "OPEN",
            "processors": "",
            "assignors": "",
            "assignors_type": "EMPTY",
            "delivers": "",
            "delivers_type": "EMPTY",
            "can_deliver": False,
            "extras": {},
            "is_draft": False,
            "is_terminable": False,
            "fields": [],
            "type": "END",
            "api_instance_id": 0,
            "is_sequential": False,
            "finish_condition": {},
            "is_multi": False,
            "is_allow_skip": False,
            "creator": None,
            "create_at": "2021-12-21 16:22:41",
            "updated_by": "admin",
            "update_at": "2021-12-21 16:22:57",
            "end_at": None,
            "is_first_state": False,
        },
        "270": {
            "workflow": 65,
            "id": 270,
            "key": 270,
            "name": "\u5ba1\u6279\u8282\u70b9",
            "desc": "",
            "distribute_type": "PROCESS",
            "axis": {"x": 755, "y": 150},
            "is_builtin": False,
            "variables": {
                "inputs": [],
                "outputs": [
                    {
                        "source": "global",
                        "state": 270,
                        "type": "STRING",
                        "key": "19566fc4268b26c6e250bf9b3465f2bc",
                        "name": "\u5ba1\u6279\u7ed3\u679c",
                        "meta": {
                            "code": "NODE_APPROVE_RESULT",
                            "type": "SELECT",
                            "choice": [
                                {"key": "false", "name": "\u62d2\u7edd"},
                                {"key": "true", "name": "\u901a\u8fc7"},
                            ],
                        },
                    }
                ],
            },
            "tag": "DEFAULT",
            "processors_type": "STARTER",
            "processors": "",
            "assignors": "",
            "assignors_type": "EMPTY",
            "delivers": "",
            "delivers_type": "EMPTY",
            "can_deliver": False,
            "extras": {"ticket_status": {"name": "", "type": "keep"}},
            "is_draft": False,
            "is_terminable": False,
            "fields": [394, 395, 396],
            "type": "APPROVAL",
            "api_instance_id": 0,
            "is_sequential": False,
            "finish_condition": {},
            "is_multi": False,
            "is_allow_skip": False,
            "creator": "admin",
            "create_at": "2021-12-21 16:22:49",
            "updated_by": "admin",
            "update_at": "2021-12-21 16:23:15",
            "end_at": None,
            "is_first_state": False,
        },
    },
    "transitions": {
        "225": {
            "workflow": 65,
            "id": 225,
            "from_state": 267,
            "to_state": 268,
            "name": "",
            "axis": {"start": "Right", "end": "Left"},
            "condition": {
                "expressions": [
                    {
                        "type": "and",
                        "expressions": [
                            {"key": "G_INT_1", "condition": "==", "value": 1}
                        ],
                    }
                ],
                "type": "and",
            },
            "condition_type": "default",
            "creator": "system",
            "create_at": "2021-12-21 16:22:41",
            "updated_by": "system",
            "update_at": "2021-12-21 16:22:41",
            "end_at": None,
        },
        "227": {
            "workflow": 65,
            "id": 227,
            "from_state": 268,
            "to_state": 270,
            "name": "\u9ed8\u8ba4",
            "axis": {"start": "Right", "end": "Left"},
            "condition": {
                "expressions": [
                    {
                        "type": "and",
                        "expressions": [
                            {"key": "G_INT_1", "condition": "==", "value": 1}
                        ],
                    }
                ],
                "type": "and",
            },
            "condition_type": "default",
            "creator": "admin",
            "create_at": "2021-12-21 16:22:51",
            "updated_by": "admin",
            "update_at": "2021-12-21 16:22:51",
            "end_at": None,
        },
        "228": {
            "workflow": 65,
            "id": 228,
            "from_state": 270,
            "to_state": 269,
            "name": "\u9ed8\u8ba4",
            "axis": {"start": "Right", "end": "Left"},
            "condition": {
                "expressions": [
                    {
                        "type": "and",
                        "expressions": [
                            {"key": "G_INT_1", "condition": "==", "value": 1}
                        ],
                    }
                ],
                "type": "and",
            },
            "condition_type": "default",
            "creator": "admin",
            "create_at": "2021-12-21 16:22:54",
            "updated_by": "admin",
            "update_at": "2021-12-21 16:22:54",
            "end_at": None,
        },
    },
    "triggers": [],
    "fields": {
        "388": {
            "id": 388,
            "is_deleted": False,
            "is_builtin": True,
            "is_readonly": False,
            "is_valid": True,
            "display": True,
            "source_type": "CUSTOM",
            "source_uri": "",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "STRING",
            "key": "title",
            "name": "\u6807\u9898",
            "layout": "COL_12",
            "validate_type": "REQUIRE",
            "show_type": 1,
            "show_conditions": {},
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "\u8bf7\u8f93\u5165\u6807\u9898",
            "tips": "",
            "is_tips": False,
            "default": "",
            "choice": [],
            "related_fields": {},
            "meta": {},
            "workflow_id": 65,
            "state_id": "",
            "source": "TABLE",
        },
        "389": {
            "id": 389,
            "is_deleted": False,
            "is_builtin": True,
            "is_readonly": False,
            "is_valid": True,
            "display": True,
            "source_type": "DATADICT",
            "source_uri": "IMPACT",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "SELECT",
            "key": "impact",
            "name": "\u5f71\u54cd\u8303\u56f4",
            "layout": "COL_12",
            "validate_type": "REQUIRE",
            "show_type": 1,
            "show_conditions": {},
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "\u8bf7\u9009\u62e9\u5f71\u54cd\u8303\u56f4",
            "tips": "",
            "is_tips": False,
            "default": "",
            "choice": [],
            "related_fields": {"be_relied": ["priority"]},
            "meta": {},
            "workflow_id": 65,
            "state_id": "",
            "source": "TABLE",
        },
        "390": {
            "id": 390,
            "is_deleted": False,
            "is_builtin": True,
            "is_readonly": False,
            "is_valid": True,
            "display": True,
            "source_type": "DATADICT",
            "source_uri": "URGENCY",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "SELECT",
            "key": "urgency",
            "name": "\u7d27\u6025\u7a0b\u5ea6",
            "layout": "COL_12",
            "validate_type": "REQUIRE",
            "show_type": 1,
            "show_conditions": {},
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "\u8bf7\u9009\u62e9\u7d27\u6025\u7a0b\u5ea6",
            "tips": "",
            "is_tips": False,
            "default": "",
            "choice": [],
            "related_fields": {"be_relied": ["priority"]},
            "meta": {},
            "workflow_id": 65,
            "state_id": "",
            "source": "TABLE",
        },
        "391": {
            "id": 391,
            "is_deleted": False,
            "is_builtin": False,
            "is_readonly": False,
            "is_valid": True,
            "display": True,
            "source_type": "DATADICT",
            "source_uri": "PRIORITY",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "SELECT",
            "key": "priority",
            "name": "\u4f18\u5148\u7ea7",
            "layout": "COL_12",
            "validate_type": "REQUIRE",
            "show_type": 1,
            "show_conditions": {},
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "\u8bf7\u9009\u62e9\u4f18\u5148\u7ea7",
            "tips": "",
            "is_tips": False,
            "default": "",
            "choice": [],
            "related_fields": {"rely_on": ["urgency", "impact"]},
            "meta": {},
            "workflow_id": 65,
            "state_id": "",
            "source": "TABLE",
        },
        "394": {
            "id": 394,
            "is_deleted": False,
            "is_builtin": False,
            "is_readonly": False,
            "is_valid": True,
            "display": True,
            "source_type": "CUSTOM",
            "source_uri": "",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "RADIO",
            "key": "2d77719940186da36ac97fb927fcc5bf",
            "name": "\u5ba1\u6279\u610f\u89c1",
            "layout": "COL_6",
            "validate_type": "REQUIRE",
            "show_type": 1,
            "show_conditions": {},
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "",
            "tips": "",
            "is_tips": False,
            "default": "true",
            "choice": [
                {"key": "true", "name": "\u901a\u8fc7"},
                {"key": "false", "name": "\u62d2\u7edd"},
            ],
            "related_fields": {},
            "meta": {"code": "APPROVE_RESULT"},
            "workflow_id": 65,
            "state_id": 270,
            "source": "CUSTOM",
        },
        "395": {
            "id": 395,
            "is_deleted": False,
            "is_builtin": False,
            "is_readonly": False,
            "is_valid": True,
            "display": False,
            "source_type": "CUSTOM",
            "source_uri": "",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "TEXT",
            "key": "69e197a5f1a0ac56a2dd3fc8b88f7527",
            "name": "\u5907\u6ce8",
            "layout": "COL_12",
            "validate_type": "OPTION",
            "show_type": 0,
            "show_conditions": {
                "expressions": [
                    {
                        "value": "false",
                        "type": "RADIO",
                        "condition": "==",
                        "key": "2d77719940186da36ac97fb927fcc5bf",
                    }
                ],
                "type": "and",
            },
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "",
            "tips": "",
            "is_tips": False,
            "default": "",
            "choice": [],
            "related_fields": {},
            "meta": {},
            "workflow_id": 65,
            "state_id": 270,
            "source": "CUSTOM",
        },
        "396": {
            "id": 396,
            "is_deleted": False,
            "is_builtin": False,
            "is_readonly": False,
            "is_valid": True,
            "display": False,
            "source_type": "CUSTOM",
            "source_uri": "",
            "api_instance_id": 0,
            "kv_relation": {},
            "type": "TEXT",
            "key": "de7848a29fd7ddff8033beef86ce7dcf",
            "name": "\u5907\u6ce8",
            "layout": "COL_12",
            "validate_type": "REQUIRE",
            "show_type": 0,
            "show_conditions": {
                "expressions": [
                    {
                        "value": "true",
                        "type": "RADIO",
                        "condition": "==",
                        "key": "2d77719940186da36ac97fb927fcc5bf",
                    }
                ],
                "type": "and",
            },
            "regex": "EMPTY",
            "regex_config": {},
            "custom_regex": "",
            "desc": "",
            "tips": "",
            "is_tips": False,
            "default": "",
            "choice": [],
            "related_fields": {},
            "meta": {},
            "workflow_id": 65,
            "state_id": 270,
            "source": "CUSTOM",
        },
    },
    "notify": [],
}
