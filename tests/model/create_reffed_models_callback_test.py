from jsonref import JsonRef
import pytest

from bravado_core.model import create_reffed_models_callback, MODEL_MARKER


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


@pytest.mark.xfail(run=False)
def test_model_type_created(response_spec, pet_model_spec):
    models = {}
    response_spec['schema'] = build_pet_proxy(pet_model_spec)
    create_reffed_models_callback(models, response_spec, key='schema')
    assert 'Pet' in models
    pet = models['Pet'](name='sumi')
    assert pet.name == 'sumi'


def test_noop_when_not_jsonref(response_spec, pet_model_spec):
    models = {}
    response_spec['schema'] = pet_model_spec
    create_reffed_models_callback(models, response_spec, key='schema')
    assert len(models) == 0


def test_noop_when_not_a_model(response_spec, pet_model_spec):
    models = {}
    del pet_model_spec[MODEL_MARKER]
    response_spec['schema'] = build_pet_proxy(pet_model_spec)
    create_reffed_models_callback(models, response_spec, key='schema')
    assert len(models) == 0
