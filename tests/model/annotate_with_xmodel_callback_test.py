import pytest

from jsonref import JsonRef

from bravado_core.model import annotate_with_xmodel_callback, MODEL_MARKER


@pytest.fixture
def pet_model_spec():
    return {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        }
    }


@pytest.fixture
def response_spec(pet_model_spec):
    return {
        'description': 'A pet',
        'schema': 'Unit test will fill in this value'
    }


def build_pet_proxy(ref, pet_model_spec):
    ref_obj = {'$ref': ref}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    return pet_proxy


def test_annotates_local_ref(response_spec, pet_model_spec):
    response_spec['schema'] = build_pet_proxy(
        '#/definitions/Pet', pet_model_spec)
    annotate_with_xmodel_callback(response_spec, key='schema')
    assert pet_model_spec[MODEL_MARKER] == 'Pet'


def test_annotates_external_ref(response_spec, pet_model_spec):
    response_spec['schema'] = build_pet_proxy(
        'pet.json#/definitions/Pet', pet_model_spec)
    annotate_with_xmodel_callback(response_spec, key='schema')
    assert pet_model_spec[MODEL_MARKER] == 'Pet'


def test_noop_when_not_jsonref(response_spec, pet_model_spec):
    annotate_with_xmodel_callback(response_spec, key='schema')
    assert MODEL_MARKER not in pet_model_spec


def test_noop_when_ref_target_path_doesnt_match(response_spec, pet_model_spec):
    # Not a model because the ref path doesn't match `#/definitions/<blah>`
    response_spec['schema'] = build_pet_proxy(
        '#/i_am_not_a_model/Pet', pet_model_spec)
    annotate_with_xmodel_callback(response_spec, key='schema')
    assert MODEL_MARKER not in pet_model_spec


def test_noop_when_model_already_marked(response_spec, pet_model_spec):
    pet_model_spec[MODEL_MARKER] = 'Pet'
    response_spec['schema'] = build_pet_proxy(
        '#/definitions/Pet', pet_model_spec)
    annotate_with_xmodel_callback(response_spec, key='schema')
    assert pet_model_spec[MODEL_MARKER] == 'Pet'
