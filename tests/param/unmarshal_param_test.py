# -*- coding: utf-8 -*-
import datetime

import pytest
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from bravado_core.operation import Operation
from bravado_core.param import Param
from bravado_core.param import unmarshal_param
from bravado_core.request import IncomingRequest
from bravado_core.spec import Spec


@pytest.fixture
def string_param_spec():
    return {
        'name': 'username',
        'in': 'query',
        'description': 'Short name of the user',
        'type': 'string',
    }


@pytest.fixture
def array_param_spec():
    return {
        'name': 'animals',
        'in': 'query',
        'description': 'List of animals',
        'type': 'array',
        'items': {
            'type': 'string',
        },
        'collectionFormat': 'multi',
    }


@pytest.fixture
def int_array_param_spec():
    return {
        'name': 'numbers',
        'in': 'query',
        'description': 'List of numbers',
        'type': 'array',
        'items': {
            'type': 'integer',
            'format': 'int64',
        },
        'collectionFormat': 'multi',
    }


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


@pytest.fixture
def boolean_param_spec():
    return {
        'name': 'isPet',
        'in': 'query',
        'description': 'True if resource is a pet, False otherwise.',
        'type': 'boolean',
    }


def test_path_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'path'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, path={'petId': '34'})
    assert 34 == unmarshal_param(param, request)


def test_query_string(empty_swagger_spec, string_param_spec):
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    request = Mock(spec=IncomingRequest, query={'username': 'darwin'})
    assert 'darwin' == unmarshal_param(param, request)


def test_optional_query_string_with_default(empty_swagger_spec, string_param_spec):
    string_param_spec['required'] = False
    string_param_spec['default'] = 'bozo'
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    request = Mock(spec=IncomingRequest, query={})
    assert 'bozo' == unmarshal_param(param, request)


def test_optional_query_string_with_no_default_and_value_is_None(empty_swagger_spec, string_param_spec):
    string_param_spec['required'] = False
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    request = Mock(spec=IncomingRequest, query={})
    assert unmarshal_param(param, request) is None


def test_optional_query_string_enum_with_no_default_and_value_is_None(empty_swagger_spec, string_param_spec):
    string_param_spec['required'] = False
    string_param_spec['enum'] = ['encrypted', 'plaintext']
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    request = Mock(spec=IncomingRequest, query={})
    assert unmarshal_param(param, request) is None


def test_query_array(empty_swagger_spec, array_param_spec):
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    request = Mock(
        spec=IncomingRequest,
        query={'animals': ['cat', 'dog', 'mouse']},
    )
    assert ['cat', 'dog', 'mouse'] == unmarshal_param(param, request)


def test_optional_query_array_with_no_default(empty_swagger_spec, array_param_spec):
    array_param_spec['required'] = False
    # Set to something other than 'multi' because 'multi' is a no-op in
    # unmarshal_collection_format()
    array_param_spec['collectionFormat'] = 'csv'
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    request = Mock(spec=IncomingRequest, query={})
    assert unmarshal_param(param, request) is None


def test_optional_query_array_with_default(empty_swagger_spec, array_param_spec):
    array_param_spec['required'] = False
    array_param_spec['default'] = ['bird', 'fish']
    array_param_spec.pop('collectionFormat')
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    request = Mock(spec=IncomingRequest, query={})
    assert ['bird', 'fish'] == unmarshal_param(param, request)


def test_optional_query_array_with_default_empty(empty_swagger_spec, array_param_spec):
    array_param_spec['required'] = False
    array_param_spec['default'] = []
    array_param_spec.pop('collectionFormat')
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    request = Mock(spec=IncomingRequest, query={})
    assert [] == unmarshal_param(param, request)


@pytest.mark.parametrize(
    "test_input,expected", [
        (["4", "2", "3"], [4, 2, 3]),
        ("23", [23]),
        (None, None),
    ],
)
def test_query_int_array(test_input, expected, empty_swagger_spec, int_array_param_spec):
    param = Param(
        empty_swagger_spec,
        Mock(spec=Operation),
        int_array_param_spec,
    )
    request = Mock(
        spec=IncomingRequest,
        query={'numbers': test_input},
    )
    assert expected == unmarshal_param(param, request)


def test_query_string_boolean_values(empty_swagger_spec, boolean_param_spec):
    param = Param(empty_swagger_spec, Mock(spec=Operation), boolean_param_spec)
    request = Mock(spec=IncomingRequest, query={'isPet': True})
    assert True is unmarshal_param(param, request)


def test_header_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param_spec['type'] = 'string'
    param_spec['name'] = 'X-Source-ID'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, headers={'X-Source-ID': 'foo'})
    assert 'foo' == unmarshal_param(param, request)


def test_optional_header_string_with_default(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param_spec['type'] = 'string'
    param_spec['name'] = 'X-Source-ID'
    param_spec['required'] = False
    param_spec['default'] = 'bar'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, headers={})
    assert 'bar' == unmarshal_param(param, request)


def test_formData_integer(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, form={'petId': '34'})
    assert 34 == unmarshal_param(param, request)


def test_optional_formData_integer_with_default(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param_spec['required'] = False
    param_spec['default'] = 99
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, form={})
    assert 99 == unmarshal_param(param, request)


def test_formData_file(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param_spec['type'] = 'file'
    param_spec['name'] = 'selfie'
    param = Param(
        empty_swagger_spec,
        Mock(spec=Operation, consumes=['multipart/form-data']),
        param_spec,
    )
    request = Mock(
        spec=IncomingRequest,
        files={'selfie': '<imagine binary data>'},
    )
    assert '<imagine binary data>' == unmarshal_param(param, request)


def test_body(empty_swagger_spec, param_spec):
    param_spec['in'] = 'body'
    param_spec['schema'] = {
        'type': 'integer',
    }
    del param_spec['type']
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, json=Mock(return_value=34))
    value = unmarshal_param(param, request)
    assert 34 == value


def assert_validate_call_count(expected_call_count, config, petstore_dict):
    with patch('bravado_core.param.validate_schema_object') as m_validate:
        petstore_spec = Spec.from_dict(petstore_dict, config=config)
        request = Mock(spec=IncomingRequest, path={'petId': 34})
        op = petstore_spec.resources['pet'].operations['getPetById']
        param = op.params['petId']
        unmarshal_param(param, request)
        assert expected_call_count == m_validate.call_count


def test_dont_validate_requests(petstore_dict):
    assert_validate_call_count(0, {'validate_requests': False}, petstore_dict)


def test_validate_requests(petstore_dict):
    assert_validate_call_count(1, {'validate_requests': True}, petstore_dict)


def test_ref(minimal_swagger_dict, array_param_spec):
    ref_spec = {'$ref': '#/refs/ArrayParam'}
    minimal_swagger_dict['refs'] = {
        'ArrayParam': array_param_spec,
    }
    swagger_spec = Spec(minimal_swagger_dict)
    param = Param(swagger_spec, Mock(spec=Operation), ref_spec)
    value = ['cat', 'dog', 'bird']
    request = Mock(spec=IncomingRequest, query={'animals': value})
    result = unmarshal_param(param, request)
    assert ['cat', 'dog', 'bird'] == result


@pytest.mark.parametrize(
    'body, expected_value',
    [
        (None, None),
        ({'an-attribute': '2018-05-24'}, {'an-attribute': datetime.date(2018, 5, 24)}),
    ],
)
def test_body_parameter_not_present_not_required(empty_swagger_spec, body, expected_value):
    param_spec = {
        'in': 'body',
        'name': 'body',
        'required': False,
        'schema': {
            'type': 'object',
            'properties': {
                'an-attribute': {
                    'type': 'string',
                    'format': 'date',
                },
            },
            'required': [
                'an-attribute',
            ],
        },
    }
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = Mock(spec=IncomingRequest, json=Mock(return_value=body))
    value = unmarshal_param(param, request)
    assert expected_value == value
