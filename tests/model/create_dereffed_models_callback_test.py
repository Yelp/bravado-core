from jsonref import JsonRef
import pytest

from bravado_core.model import create_reffed_models_callback
from bravado_core.model import create_dereffed_models_callback
from bravado_core.model import MODEL_MARKER


@pytest.fixture
def response_spec():
    return {
        'description': 'A pet',
        'schema': 'Unit test will fill in a value here'
    }


@pytest.fixture
def pet_model_spec():
    return {
        MODEL_MARKER: 'Pet',
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        }
    }


def build_pet_proxy(pet_model_spec):
    ref_obj = {'$ref': '#/definitions/Pet'}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    return pet_proxy


def test_model_type_created(pet_model_spec):
    models = {}
    create_dereffed_models_callback(models, pet_model_spec, key=MODEL_MARKER)
    assert 'Pet' in models
    pet = models['Pet'](name='sumi')
    assert pet.name == 'sumi'


def test_noop_when_not_model(pet_model_spec):
    models = {}
    create_reffed_models_callback(models, pet_model_spec, key='type')
    assert len(models) == 0
