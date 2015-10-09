import json
import jsonref

from bravado_core.spec import post_process_spec
from bravado_core.spec import replace_jsonref_proxies_callback


def test_dict():
    d = {
        'foo': {
            "$ref": "#/definitions/user"
        },
        'definitions': {
            'user': {
                'properties': {
                    'first_name': {
                        'type': 'string'
                    }
                }
            }
        }
    }
    json_obj = jsonref.loads(json.dumps(d))
    assert type(json_obj['foo']) == jsonref.JsonRef

    post_process_spec(
        json_obj, on_container_callbacks=(replace_jsonref_proxies_callback,))
    assert type(json_obj['foo']) == dict

    assert d['definitions']['user'] == json_obj['foo']


def test_nested_dict():
    d = {
        'foo': {
            "$ref": "#/definitions/user"
        },
        'definitions': {
            'user': {
                'type': 'object',
                'properties': {
                    'first_name': {
                        'type': 'string'
                    },
                    'address': {
                        '$ref': '#/definitions/address',
                    }
                }
            },
            'address': {
                'type': 'object',
                'properties': {
                    'street': {
                        'type': 'string'
                    }
                }
            }
        }
    }
    json_obj = jsonref.loads(json.dumps(d))
    assert type(json_obj['foo']) == jsonref.JsonRef
    assert type(json_obj['foo']['properties']['address']) == jsonref.JsonRef

    post_process_spec(
        json_obj, on_container_callbacks=(replace_jsonref_proxies_callback,))
    assert type(json_obj['foo']) == dict
    assert type(json_obj['foo']['properties']['address']) == dict

    assert d['definitions']['address'] == \
        json_obj['foo']['properties']['address']


def test_list():
    d = {
        'foo': [
            {
                "$ref": "#/definitions/user"
            }
        ],
        'definitions': {
            'user': {
                'properties': {
                    'first_name': {
                        'type': 'string'
                    }
                }
            }
        }
    }
    json_obj = jsonref.loads(json.dumps(d))
    assert type(json_obj['foo'][0]) == jsonref.JsonRef

    post_process_spec(
        json_obj, on_container_callbacks=(replace_jsonref_proxies_callback,))
    assert type(json_obj['foo'][0]) == dict

    assert d['definitions']['user'] == json_obj['foo'][0]
