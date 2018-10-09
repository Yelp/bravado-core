# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import _collect_models
from bravado_core.model import create_model_type
from bravado_core.spec import Spec


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


@pytest.mark.parametrize(
    'origin_url', [None, 'origin_url'],
)
def test_simple(minimal_swagger_dict, pet_model_spec, origin_url):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict, origin_url=origin_url)
    models = {}
    json_reference = '{}#/definitions/Pet'.format(origin_url or '')
    _collect_models(
        minimal_swagger_dict['definitions']['Pet'],
        models=models,
        swagger_spec=swagger_spec,
        json_reference=json_reference + '/x-model',
    )
    assert 'Pet' in models
    assert models['Pet']._json_reference == json_reference


def test_no_model_type_generation_for_not_object_type(minimal_swagger_dict):
    """
    Ensure that models types are generated only for swagger objects (type: object)

    This is needed because even if "x-model" is present it could be related to a not object type
    (ie. array or string) and for those cases it does not make sense to generate a python model type.
    Additionally, even if this type has been generated it won't be used by bravado-core during
    marshaling/unmarshaling process.

    Ensuring that for those cases a model type is not generated simplifies type checking.
    """
    minimal_swagger_dict['definitions']['Pets'] = {
        'type': 'array',
        'items': {
            '$ref': '#/definitions/Pet'
        },
        'x-model': 'Pets'
    }
    swagger_spec = Spec(minimal_swagger_dict)
    models = {}
    _collect_models(
        minimal_swagger_dict['definitions']['Pets'],
        models=models,
        swagger_spec=swagger_spec,
        json_reference='#/definitions/Pets/x-model',
    )
    assert 'Pets' not in models


def test_raise_error_if_duplicate_models_are_identified(minimal_swagger_dict, pet_model_spec):
    model_name = 'Pet'
    minimal_swagger_dict['definitions'][model_name] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    models = {
        model_name: create_model_type(
            swagger_spec=swagger_spec,
            model_name=model_name,
            model_spec={},
        )
    }

    json_reference = '#/definitions/{model_name}/x-model'.format(model_name=model_name)
    with pytest.raises(ValueError) as excinfo:
        _collect_models(
            minimal_swagger_dict['definitions'][model_name],
            models=models,
            swagger_spec=swagger_spec,
            json_reference=json_reference,
        )

    expected_lines = [
        'Identified duplicated model: model_name "{mod_name}", uri: {json_reference}.'.format(
            mod_name=model_name,
            json_reference=json_reference,
        ),
        'Known model spec: "{}"',
        'New model spec: "{pet_model_spec}"'.format(pet_model_spec=pet_model_spec),
        'TIP: enforce different model naming by using {MODEL_MARKER}'.format(MODEL_MARKER='x-model'),
    ]
    assert all(l in str(excinfo.value) for l in expected_lines)
