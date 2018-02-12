# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import collect_models
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


def test_simple(minimal_swagger_dict, pet_model_spec):
    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    models = {}
    collect_models(
        minimal_swagger_dict['definitions']['Pet'],
        'x-model',
        ['definitions', 'Pet', 'x-model'],
        models=models,
        swagger_spec=swagger_spec)
    assert 'Pet' in models


def test_no_model_type_generation_for_not_object_type(minimal_swagger_dict, pet_model_spec):
    """
    Ensure that models types are generated only for swagger objects (type: object)

    This is needed because even if "x-model" is present it could be related to a not object type
    (ie. array or string) and for those cases it does not make sense to generate a python model type.
    Additionally, even if this type has been generated it won't be used by bravado-core during
    marshaling/unmarshaling process.

    Ensuring that for those cases a model type is not generated simplifies type checking.
    """

    minimal_swagger_dict['definitions']['Pet'] = pet_model_spec
    minimal_swagger_dict['definitions']['Pets'] = {
        'type': 'array',
        'items': {
            '$ref': '#/definitions/Pet'
        },
        'x-model': 'Pets'
    }
    swagger_spec = Spec(minimal_swagger_dict)
    models = {}
    collect_models(
        minimal_swagger_dict['definitions']['Pets'],
        'x-model',
        ['definitions', 'Pets', 'x-model'],
        models=models,
        swagger_spec=swagger_spec)
    assert 'Pets' not in models
