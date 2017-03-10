# -*- coding: utf-8 -*-
import pytest

from bravado_core.schema import collapsed_properties
from bravado_core.spec import Spec


@pytest.fixture
def users_spec():
    return {
        "User": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64"
                },
                "username": {
                    "type": "string"
                },
                "email": {
                    "type": "string"
                },
                "password": {
                    "type": "string"
                }
            }
        },
        "VIP": {
            "allOf": [
                {
                    "$ref": "#/definitions/User"
                },
                {
                    "properties": {
                        "vip_pass_no": {
                            "type": "string"
                        }
                    }
                }
            ]
        },
        "Admin": {
            "allOf": [
                {
                    "$ref": "#/definitions/User"
                },
                {
                    "type": "object",
                    "properties": {
                        "permissions": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    }
                }
            ]
        },
        "SuperUser": {
            "allOf": [
                {
                    "$ref": "#/definitions/Admin"
                },
                {
                    "$ref": "#/definitions/VIP"
                }
            ]
        }
    }


@pytest.fixture
def users_swagger_spec(minimal_swagger_dict, users_spec):
    minimal_swagger_dict['definitions'] = users_spec
    return Spec.from_dict(minimal_swagger_dict)


def test_allOf(users_spec, users_swagger_spec):
    """Test allOf functionality, including:
     - multiple levels of allOf
     - multiple references within one allOf
     - referencing the same model multiple times across the
       allOf-hierarchy
    """
    superuser_spec = users_spec['SuperUser']
    props = collapsed_properties(superuser_spec, users_swagger_spec)

    expected_props = {
        # User properties
        'id': {'type': 'integer', 'format': 'int64'},
        'username': {'type': 'string'},
        'email': {'type': 'string'},
        'password': {'type': 'string'},
        # VIP additional properties
        'vip_pass_no': {'type': 'string'},
        # Admin additional properties
        'permissions': {'items': {'type': 'string'}, 'type': 'array'}
    }
    assert props == expected_props


def test_recursive_ref(node_spec, recursive_swagger_spec):
    props = collapsed_properties(node_spec, recursive_swagger_spec)

    expected_props = {
        'name': {'type': 'string'},
        'child': {'$ref': '#/definitions/Node'}
    }
    assert props == expected_props
