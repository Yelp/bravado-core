from bravado_core.schema import is_prop_nullable
from bravado_core.spec import Spec


def test_true(minimal_swagger_spec):
    prop_spec = {
        'type': 'string',
        'x-nullable': True,
    }
    assert is_prop_nullable(minimal_swagger_spec, prop_spec)


def test_false(minimal_swagger_spec):
    prop_spec = {
        'type': 'string',
    }
    assert not is_prop_nullable(minimal_swagger_spec, prop_spec)


def test_false_explicit(minimal_swagger_spec):
    prop_spec = {
        'type': 'string',
        'x-nullable': False,
    }
    assert not is_prop_nullable(minimal_swagger_spec, prop_spec)


def test_ref_true(minimal_swagger_dict):
    minimal_swagger_dict['definitions'] = {
        'Pet': {
            'type': 'object',
            'x-nullable': True,
        }
    }
    param_spec = {'$ref': '#/definitions/Pet'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert is_prop_nullable(swagger_spec, param_spec)


def test_ref_false(minimal_swagger_dict):
    minimal_swagger_dict['definitions'] = {
        'Pet': {
            'type': 'object',
        }
    }
    param_spec = {'$ref': '#/definitions/Pet'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert not is_prop_nullable(swagger_spec, param_spec)
