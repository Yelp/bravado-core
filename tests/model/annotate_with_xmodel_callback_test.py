import pytest

from jsonref import JsonRef

from bravado_core.model import annotate_with_xmodel_callback


@pytest.fixture
def pet_model_spec():
    return  {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        }
    }


def test_annotates_local_ref(pet_model_spec):
    ref_obj = {'$ref': '#/definitions/Pet'}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    annotate_with_xmodel_callback(pet_proxy)
    assert pet_model_spec['x-model'] == 'Pet'


def test_annotates_external_ref(pet_model_spec):
    ref_obj = {'$ref': 'pet.json#/definitions/Pet'}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    annotate_with_xmodel_callback(pet_proxy)
    assert pet_model_spec['x-model'] == 'Pet'

