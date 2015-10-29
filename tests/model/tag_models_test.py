import pytest

from bravado_core.model import tag_models, MODEL_MARKER
from bravado_core.spec import Spec


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


def test_tags_model(minimal_swagger_dict, pet_model_spec):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert pet_model_spec[MODEL_MARKER] == 'Pet'


def test_type_missing(minimal_swagger_dict, pet_model_spec):
    del pet_model_spec['type']
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert MODEL_MARKER not in pet_model_spec


def test_model_not_object(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Pet'] = {
        'type': 'array',
        'items': {
            'type': 'string'
        },
    }
    swagger_spec = Spec(minimal_swagger_dict)
    tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert MODEL_MARKER not in minimal_swagger_dict['definitions']['Pet']


def test_path_too_short(minimal_swagger_dict, pet_model_spec):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    tag_models(
        minimal_swagger_dict,
        'definitions',
        ['definitions'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert MODEL_MARKER not in pet_model_spec


def test_duplicate_model(minimal_swagger_dict, pet_model_spec):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    with pytest.raises(ValueError) as excinfo:
        tag_models(
            minimal_swagger_dict['definitions'],
            'Pet',
            ['definitions', 'Pet'],
            visited_models={'Pet': ['definitions','Pet']},
            swagger_spec=swagger_spec)
    assert 'Duplicate' in str(excinfo.value)


def test_skip_already_tagged_models(minimal_swagger_dict, pet_model_spec):
    pet_model_spec[MODEL_MARKER] = 'SpecialPet'
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert pet_model_spec[MODEL_MARKER] == 'SpecialPet'


# def test_annotates_external_ref(response_spec, pet_model_spec):
#     response_spec['schema'] = build_pet_proxy(
#         'pet.json#/definitions/Pet', pet_model_spec)
#     annotate_with_xmodel_callback(response_spec, key='schema')
#     assert pet_model_spec[MODEL_MARKER] == 'Pet'

# def test_noop_when_ref_target_path_doesnt_match(response_spec, pet_model_spec):
#     # Not a model because the ref path doesn't match `#/definitions/<blah>`
#     response_spec['schema'] = build_pet_proxy(
#         '#/i_am_not_a_model/Pet', pet_model_spec)
#     annotate_with_xmodel_callback(response_spec, key='schema')
#     assert MODEL_MARKER not in pet_model_spec
