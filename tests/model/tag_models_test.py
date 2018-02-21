# -*- coding: utf-8 -*-
import mock
import pytest

from bravado_core import model
from bravado_core.model import _tag_models
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
    _tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert pet_model_spec['x-model'] == 'Pet'


def test_type_missing(minimal_swagger_dict, pet_model_spec):
    del pet_model_spec['type']
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    _tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert 'x-model' not in pet_model_spec


def test_model_not_object(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Pet'] = {
        'type': 'array',
        'items': {
            'type': 'string'
        },
    }
    swagger_spec = Spec(minimal_swagger_dict)
    _tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert 'x-model' not in minimal_swagger_dict['definitions']['Pet']


def test_path_too_short(minimal_swagger_dict, pet_model_spec):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    _tag_models(
        minimal_swagger_dict,
        'definitions',
        ['definitions'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert 'x-model' not in pet_model_spec


@pytest.mark.parametrize('use_models', [True, False])
@mock.patch.object(model, 'log', autospec=True)
def test_duplicate_model(mock_log, minimal_swagger_dict, pet_model_spec, use_models):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict, config={'use_models': use_models})

    duplicate_message = 'Duplicate "Pet" model found at path [\'definitions\', \'Pet\']. ' \
                        'Original "Pet" model at path [\'definitions\', \'Pet\']'

    raised_exception = None
    try:
        _tag_models(
            minimal_swagger_dict['definitions'],
            'Pet',
            ['definitions', 'Pet'],
            visited_models={'Pet': ['definitions', 'Pet']},
            swagger_spec=swagger_spec,
        )
    except ValueError as e:
        raised_exception = e

    if use_models:
        assert str(raised_exception) == duplicate_message
        assert not mock_log.warning.called
    else:
        assert raised_exception is None
        mock_log.warning.assert_called_once_with(duplicate_message)


def test_skip_already_tagged_models(minimal_swagger_dict, pet_model_spec):
    pet_model_spec['x-model'] = 'SpecialPet'
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    _tag_models(
        minimal_swagger_dict['definitions'],
        'Pet',
        ['definitions', 'Pet'],
        visited_models={},
        swagger_spec=swagger_spec)
    assert pet_model_spec['x-model'] == 'SpecialPet'
