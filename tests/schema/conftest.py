# -*- coding: utf-8 -*-
import pytest

from bravado_core.spec import Spec


@pytest.fixture
def users_spec():
    return {
        "User": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                },
                "username": {
                    "type": "string",
                },
                "email": {
                    "type": "string",
                },
                "password": {
                    "type": "string",
                },
            },
            "required": ["id", "username", "password"],
        },
        "VIP": {
            "allOf": [
                {
                    "$ref": "#/definitions/User",
                },
                {
                    "properties": {
                        "vip_pass_no": {
                            "type": "string",
                        },
                    },
                },
            ],
        },
        "Admin": {
            "allOf": [
                {
                    "$ref": "#/definitions/User",
                },
                {
                    "type": "object",
                    "properties": {
                        "permissions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                        },
                    },
                    "required": ["permissions"],
                },
            ],
        },
        "SuperUser": {
            "allOf": [
                {
                    "$ref": "#/definitions/Admin",
                },
                {
                    "$ref": "#/definitions/VIP",
                },
            ],
        },
    }


@pytest.fixture
def users_swagger_spec(minimal_swagger_dict, users_spec):
    minimal_swagger_dict['definitions'] = users_spec
    return Spec.from_dict(minimal_swagger_dict)
