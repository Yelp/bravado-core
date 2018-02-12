# -*- coding: utf-8 -*-
import pytest
from mock import Mock
from mock import patch
from six import iterkeys
from swagger_spec_validator.common import SwaggerValidationError

from bravado_core.spec import Spec
from tests.validate.conftest import email_address_format


def assert_validate_call_count(expected_call_count, config, petstore_dict):
    spec = Spec(petstore_dict, config=config)
    with patch('bravado_core.spec.validator20.validate_spec') as m_validate:
        spec.deref = Mock(return_value={})
        spec.build()
    assert expected_call_count == m_validate.call_count


def test_validate_swagger_spec(petstore_dict):
    assert_validate_call_count(
        expected_call_count=1,
        config={'validate_swagger_spec': True},
        petstore_dict=petstore_dict,
    )


def test_dont_validate_swagger_spec(petstore_dict):
    assert_validate_call_count(
        expected_call_count=0,
        config={'validate_swagger_spec': False},
        petstore_dict=petstore_dict,
    )


def test_validate_swagger_spec_failure(petstore_dict):
    # induce failure
    del petstore_dict['swagger']
    spec = Spec(petstore_dict)
    with pytest.raises(SwaggerValidationError) as excinfo:
        spec.build()
    assert "'swagger' is a required property" in str(excinfo.value)


def test_build_with_custom_format(petstore_dict):
    assert_validate_call_count(
        expected_call_count=1,
        config={'formats': [email_address_format]},
        petstore_dict=petstore_dict,
    )


@pytest.mark.parametrize(
    'internally_dereference_refs',
    [
        True,
        False,
    ]
)
def test_build_with_internally_dereference_refs(petstore_dict, internally_dereference_refs):
    spec = Spec(
        petstore_dict,
        config={'internally_dereference_refs': internally_dereference_refs}
    )
    assert spec.deref == spec._force_deref
    spec.build()
    assert (spec.deref == spec._force_deref) == (not internally_dereference_refs)


def test_not_object_x_models_are_not_generating_models(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Pets'] = {
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'x-model': 'Pets'
    }
    swagger_spec = Spec(minimal_swagger_dict)
    swagger_spec.build()
    assert not swagger_spec.definitions


@pytest.mark.parametrize(
    'definitions, expected_models',
    (
        (
            {
                'model1': {
                    'type': 'object',
                    'x-model': 'x-model_model1'
                }
            },
            {'x-model_model1'},
        ),
        (
            {
                'model1': {
                    'type': 'object',
                    'title': 'title_model1'
                }
            },
            {'title_model1'},
        ),
        (
            {
                'model1': {
                    'type': 'object',
                }
            },
            {'model1'},
        ),
    )
)
def test_model_naming_takes_in_account_xmodel_title_key(minimal_swagger_dict, definitions, expected_models):
    minimal_swagger_dict['definitions'] = definitions
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert set(iterkeys(swagger_spec.definitions)) == expected_models


def test_model_naming_uses_title_if_present(minimal_swagger_dict):
    """This test ensures that inline schemas gets tagged as models they have title attribute"""
    response_schema = {
        'title': 'model_title',
        'type': 'object',
    }
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'get': {
                'responses': {
                    '200': {
                        'description': 'aa',
                        'schema': response_schema,
                    },
                },
            },
        },
    }
    swagger_spec = Spec.from_dict(minimal_swagger_dict)

    assert set(iterkeys(swagger_spec.definitions)) == {'model_title'}
    assert response_schema.get('x-model') == 'model_title'
