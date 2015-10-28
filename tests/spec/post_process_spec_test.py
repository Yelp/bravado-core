import json
import jsonref

from bravado_core.spec import post_process_spec, Spec
from bravado_core.spec import replace_jsonref_proxies_callback


def test_dict():
    swagger_dict = {
        'foo': {
            "$ref": "#/definitions/User"
        },
        'definitions': {
            'User': {
                'properties': {
                    'first_name': {
                        'type': 'string'
                    },
                    'children': {
                        'type': 'array',
                        'items': {
                            'type': {
                                '$ref': '#/definitions/User'
                            }
                        }
                    }
                }
            }
        },
        # 'another_file': {
        #     'definitions': {
        #         'User': {
        #             'properties': {
        #                 'first_name': {
        #                     'type': 'string'
        #                 },
        #             }
        #         }
        #     }
        # }
    }

    swagger_spec = Spec(swagger_dict)

    def tag_models(visited_models, container, key, path):
        if len(path) >= 2 and path[-2] == 'definitions':
            model_name = key
            print 'Found model: %s' % model_name
            if not model_name in visited_models:
                model_spec = swagger_spec.resolve(container, key)
                model_spec['x-model'] = model_name
                visited_models[model_name] = path
            else:
                raise ValueError('Duplicate "{0}" model found at path {1}. '
                    'Original "{0}" model at path {2}'.format(
                    model_name, path, visited_models[model_name]))

    visited = {}
    import functools
    post_process_spec(swagger_spec, [functools.partial(tag_models, visited)])
    print json.dumps(swagger_dict, indent=2)


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
