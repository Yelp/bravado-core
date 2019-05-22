# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_schema_object
from tests.conftest import get_url


def test_unmarshal_schema_object_allOf(composition_dict, composition_abspath):
    composition_spec = Spec.from_dict(composition_dict, origin_url=get_url(composition_abspath))
    pongClone_spec = composition_spec.spec_dict['definitions']['pongClone']
    pongClone = composition_spec.definitions['pongClone']

    result = unmarshal_schema_object(
        composition_spec,
        pongClone_spec,
        {
            'additionalFeature': 'Badges',
            'gameSystem': 'NES',
            'pang': 'value',
            'releaseDate': 'October',
        },
    )
    assert isinstance(result, pongClone)


def test_use_models_true(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict, config={'use_models': True})
    Category = petstore_spec.definitions['Category']
    category_spec = petstore_spec.spec_dict['definitions']['Category']

    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': 200, 'name': 'short-hair'},
    )

    assert isinstance(result, Category)


def test_use_models_false(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict, config={'use_models': False})
    category_spec = petstore_spec.spec_dict['definitions']['Category']

    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': 200, 'name': 'short-hair'},
    )

    assert isinstance(result, dict)


def test_missing_object_spec(petstore_dict):
    # without a type, do no validation
    category_spec = petstore_dict['definitions']['Category']
    category_spec['properties']['id'] = {}
    petstore_spec = Spec.from_dict(petstore_dict, config={'use_models': False})

    # so id can be a string...
    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': 'blahblah', 'name': 'short-hair'},
    )

    assert result == {'id': 'blahblah', 'name': 'short-hair'}

    # ...or anything else
    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': {'foo': 'bar'}, 'name': 'short-hair'},
    )

    assert result == {'id': {'foo': 'bar'}, 'name': 'short-hair'}


def test_missing_object_spec_defaulting_on(petstore_dict):
    """When default_type_to_object config option is set to True,
    then missing types default to object
    """
    category_spec = petstore_dict['definitions']['Category']
    # now a missing type will default to object type
    category_spec['properties']['id'].pop('type')

    petstore_spec = Spec.from_dict(petstore_dict, config={'use_models': False, 'default_type_to_object': True})

    result = unmarshal_schema_object(
        petstore_spec,
        category_spec,
        {'id': {'foo': 'bar'}, 'name': 'short-hair'},
    )

    assert result == {'id': {'foo': 'bar'}, 'name': 'short-hair'}

    # so a different type will fail
    with pytest.raises(SwaggerMappingError):
        unmarshal_schema_object(
            petstore_spec,
            category_spec,
            {'id': 'blahblah', 'name': 'short-hair'},
        )


def test_invalid_type(petstore_dict):
    category_spec = petstore_dict['definitions']['Category']
    category_spec['properties']['id']['type'] = 'notAValidType'
    petstore_spec = Spec.from_dict(
        petstore_dict,
        config={'use_models': False, 'validate_swagger_spec': False},
    )

    with pytest.raises(SwaggerMappingError):
        unmarshal_schema_object(
            petstore_spec,
            category_spec,
            {'id': 200, 'name': 'short-hair'},
        )
