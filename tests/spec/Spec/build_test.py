# -*- coding: utf-8 -*-
import pytest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
from six import iterkeys
from six.moves.urllib.request import pathname2url
from swagger_spec_validator.common import SwaggerValidationError

from bravado_core.spec import Spec
from tests.conftest import get_url
from tests.conftest import get_url_path
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
    ],
)
def test_build_with_internally_dereference_refs(petstore_abspath, petstore_dict, internally_dereference_refs):
    spec = Spec(
        petstore_dict,
        origin_url=get_url(petstore_abspath),
        config={'internally_dereference_refs': internally_dereference_refs},
    )
    assert spec.deref == spec._force_deref
    spec.build()
    assert (spec.deref == spec._force_deref) == (not internally_dereference_refs)


@pytest.mark.parametrize(
    'use_spec_url_for_base_path',
    [
        True,
        False,
    ],
)
def test_build_using_spec_url_for_base_path(petstore_abspath, petstore_dict, use_spec_url_for_base_path):
    # use_spec_url_for_base_path is only effective when basePath is not present
    # in the spec, so remove it
    del petstore_dict['basePath']

    origin_url = get_url(petstore_abspath)
    spec = Spec(
        petstore_dict,
        origin_url=origin_url,
        config={'use_spec_url_for_base_path': use_spec_url_for_base_path},
    )

    spec.build()

    base_url = 'http://' + petstore_dict['host']
    if not use_spec_url_for_base_path:
        assert spec.api_url == base_url + '/'
    else:
        petstore_path = get_url_path(origin_url)
        assert spec.api_url == '{}/{}'.format(base_url, pathname2url(petstore_path).lstrip('/'))


def test_not_object_x_models_are_not_generating_models(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Pets'] = {
        'type': 'array',
        'items': {
            'type': 'string',
        },
        'x-model': 'Pets',
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
                    'x-model': 'x-model_model1',
                },
            },
            {'x-model_model1'},
        ),
        (
            {
                'model1': {
                    'type': 'object',
                    'title': 'title_model1',
                },
            },
            {'title_model1'},
        ),
        (
            {
                'model1': {
                    'type': 'object',
                },
            },
            {'model1'},
        ),
    ),
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


def test_build_raises_in_case_of_duplicated_models_in_definitions(minimal_swagger_dict):
    """This test ensures that inline schemas gets tagged as models they have title attribute"""

    minimal_swagger_dict['definitions'] = {
        'model': {
            'type': 'object',
        },
        'duplicated_model': {
            'type': 'object',
            'title': 'model',
        },
    }
    with pytest.raises(ValueError) as exinfo:
        Spec.from_dict(minimal_swagger_dict)

    expected_exception_string = (
        'Duplicate "model" model found at "{new_json_reference}". '
        'Original "model" model at "{old_json_reference}"'.format(
            new_json_reference='#/definitions/model',
            old_json_reference='#/definitions/duplicated_model',
        )
    )
    assert expected_exception_string == str(exinfo.value)


def test_build_raises_in_case_of_duplicated_models_in_paths(minimal_swagger_dict):
    """This test ensures that inline schemas gets tagged as models they have title attribute"""
    model_name = 'model'
    model_200 = {
        'type': 'object',
        'x-location': '200',
        'x-model': model_name,
    }
    model_201 = {
        'type': 'object',
        'x-location': '201',
        'x-model': model_name,
    }
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'get': {
                'responses': {
                    '200': {
                        'description': '200 description',
                        'schema': model_200,
                    },
                    '201': {
                        'description': '201 description',
                        'schema': model_201,
                    },
                },
            },
        },
    }
    with pytest.raises(ValueError) as exinfo:
        Spec.from_dict(minimal_swagger_dict)

    # NOTE: the exception depends on the descending order
    expected_exception_string = (
        'Identified duplicated model: model_name "{mod_name}", uri: {json_reference}.\n'
        '    Known model spec: "{known_model}"\n'
        '    New model spec: "{new_model}"\n'
        'TIP: enforce different model naming by using {MODEL_MARKER}'.format(
            known_model=model_200,
            mod_name=model_name,
            MODEL_MARKER='x-model',
            new_model=model_201,
            json_reference='#/paths//endpoint/get/responses/201/schema/x-model',
        )
    )

    assert expected_exception_string == str(exinfo.value)


def test_build_raises_in_case_of_duplicated_models_between_paths_and_definitions(minimal_swagger_dict):
    """This test ensures that inline schemas gets tagged as models they have title attribute"""
    model_name = 'model'
    definition_model = {
        'type': 'object',
        'x-location': 'definitions',
    }
    response_model = {
        'type': 'object',
        'x-location': 'paths',
        'x-model': model_name,
    }
    minimal_swagger_dict['definitions'] = {
        model_name: definition_model,
    }
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'get': {
                'responses': {
                    '200': {
                        'description': '200 description',
                        'schema': response_model,
                    },
                },
            },
        },
    }
    with pytest.raises(ValueError) as exinfo:
        Spec.from_dict(minimal_swagger_dict)

    # NOTE: the exception depends on the descending order
    expected_exception_string = (
        'Identified duplicated model: model_name "{mod_name}", uri: {json_reference}.\n'
        '    Known model spec: "{known_model}"\n'
        '    New model spec: "{new_model}"\n'
        'TIP: enforce different model naming by using {MODEL_MARKER}'.format(
            known_model=definition_model,
            mod_name=model_name,
            MODEL_MARKER='x-model',
            new_model=response_model,
            json_reference='#/paths//endpoint/get/responses/200/schema/x-model',
        )
    )

    assert expected_exception_string == str(exinfo.value)
