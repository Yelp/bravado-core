import json
import jsonref

from bravado_core.spec import replace_jsonref_proxies


def test_simple():
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
    assert isinstance(json_obj['foo'], jsonref.JsonRef)

    replace_jsonref_proxies(json_obj)
    assert isinstance(json_obj['foo'], dict)


def test_nested():
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
    assert isinstance(json_obj['foo'], jsonref.JsonRef)
    assert isinstance(json_obj['foo']['properties']['address'], jsonref.JsonRef)

    replace_jsonref_proxies(json_obj)
    assert isinstance(json_obj['foo'], dict)
    assert isinstance(json_obj['foo']['properties']['address'], dict)
