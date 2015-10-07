import pytest

from jsonref import JsonRef

from bravado_core.model import fix_models_with_no_type_callback


@pytest.fixture
def pet_model_spec():
    return {
        'x-model': 'Pet',
        'properties': {
            'name': {
                'type': 'string'
            }
        }
    }


def test_inserts_missing_type(pet_model_spec):
    ref_obj = {'$ref': '#/definitions/Pet'}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    fix_models_with_no_type_callback(pet_proxy)
    assert pet_model_spec['type'] == 'object'
