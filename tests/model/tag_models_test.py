# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import MODEL_MARKER
from bravado_core.model import tag_models
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
    """We default to object when type is missing"""
    del pet_model_spec['type']
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert MODEL_MARKER in pet_model_spec


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
            visited_models={'Pet': ['definitions', 'Pet']},
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
