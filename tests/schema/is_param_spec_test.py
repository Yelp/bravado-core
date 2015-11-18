from bravado_core.schema import is_param_spec
from bravado_core.spec import Spec


def test_true(minimal_swagger_spec):
    param_spec = {
        'in': 'path',
        'name': 'petId',
        'type': 'integer',
    }
    assert is_param_spec(minimal_swagger_spec, param_spec)


def test_false(minimal_swagger_spec):
    response_spec = {'description': 'Invalid input'}
    assert not is_param_spec(minimal_swagger_spec, response_spec)


def test_ref_true(minimal_swagger_dict):
    minimal_swagger_dict['parameters'] = {
        'PetId': {
            'in': 'path',
            'name': 'petId',
            'type': 'integer',
        }
    }
    param_spec = {'$ref': '#/parameters/PetId'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert is_param_spec(swagger_spec, param_spec)


def test_ref_false(minimal_swagger_dict):
    minimal_swagger_dict['responses'] = {
        'InvalidInput': {
            'description': 'Invalid input'
        }
    }
    response_spec = {'$ref': '#/responses/InvalidInput'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert not is_param_spec(swagger_spec, response_spec)
