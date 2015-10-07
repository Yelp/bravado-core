import pytest

from jsonref import JsonRef

from bravado_core.model import build_models_callback


@pytest.fixture
def pet_model_spec():
    return {
        'x-model': 'Pet',
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        }
    }


def test_simple(pet_model_spec):
    models = {}
    ref_obj = {'$ref': '#/definitions/Pet'}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    build_models_callback(models, pet_proxy)
    assert 'Pet' in models
    pet = models['Pet'](name='sumi')
    assert pet.name == 'sumi'
