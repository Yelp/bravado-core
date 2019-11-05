# -*- coding: utf-8 -*-
from bravado_core.schema import collapsed_properties


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
        'permissions': {'items': {'type': 'string'}, 'type': 'array'},
    }
    assert props == expected_props


def test_recursive_ref(node_spec, recursive_swagger_spec):
    props = collapsed_properties(node_spec, recursive_swagger_spec)

    expected_props = {
        'name': {'type': 'string'},
        'date': {'type': 'string', 'format': 'date'},
        'child': {'$ref': '#/definitions/Node'},
    }
    assert props == expected_props
