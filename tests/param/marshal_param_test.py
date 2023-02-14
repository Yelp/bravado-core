# -*- coding: utf-8 -*-
import copy
import datetime
from json import loads

import pytest
from jsonschema import ValidationError
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from bravado_core.content_type import APP_JSON
from bravado_core.operation import Operation
from bravado_core.param import encode_request_param
from bravado_core.param import marshal_param
from bravado_core.param import Param
from bravado_core.param import unmarshal_param
from bravado_core.request import IncomingRequest
from bravado_core.spec import Spec


@pytest.fixture
def request_dict():
    return {
        'params': {},
    }


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
    }


@pytest.fixture
def param_spec():
    return {
        'name': 'petId',
        'description': 'ID of pet that needs to be fetched',
        'type': 'integer',
        'format': 'int64',
    }


def test_query_string(empty_swagger_spec, string_param_spec, request_dict):
    param = Param(empty_swagger_spec, Mock(spec=Operation), string_param_spec)
    expected = copy.deepcopy(request_dict)
    expected['params']['username'] = 'darwin'
    marshal_param(param, 'darwin', request_dict)
    assert expected == request_dict


def test_query_array(empty_swagger_spec, array_param_spec, request_dict):
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    value = ['cat', 'dog', 'bird']
    expected = copy.deepcopy(request_dict)
    expected['params']['animals'] = ','.join(value)
    marshal_param(param, value, request_dict)
    assert expected == request_dict


def test_optional_query_array_with_no_value(
    empty_swagger_spec,
    array_param_spec, request_dict,
):
    array_param_spec['required'] = False
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    expected = copy.deepcopy(request_dict)
    marshal_param(param, value=None, request=request_dict)
    assert expected == request_dict


def test_required_query_array_with_no_value(
    empty_swagger_spec,
    array_param_spec, request_dict,
):
    array_param_spec['required'] = True
    param = Param(empty_swagger_spec, Mock(spec=Operation), array_param_spec)
    with pytest.raises(ValidationError) as excinfo:
        marshal_param(param, value=None, request=request_dict)
    assert 'is a required parameter' in str(excinfo.value)


def test_path_integer(empty_swagger_spec, param_spec):
    param_spec['in'] = 'path'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {'url': '/pet/{petId}'}
    marshal_param(param, 34, request)
    # verify integer coerceced to str
    assert '/pet/34' == request['url']


@pytest.mark.parametrize(
    'string_param, expected_path',
    [
        ('34', '/pet/34'),
        ('a value', '/pet/a%20value'),
        (u'Ümlaut', '/pet/%C3%9Cmlaut'),
        ('/\\%?=', '/pet/%2F%5C%25%3F%3D'),
    ],
)
def test_path_string(empty_swagger_spec, param_spec, string_param, expected_path):
    param_spec['in'] = 'path'
    param_spec['type'] = 'string'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {'url': '/pet/{petId}'}
    marshal_param(param, string_param, request)
    assert expected_path == request['url']


def test_header_string(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param_spec['type'] = 'string'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {},
    }
    marshal_param(param, '34', request)
    assert {'petId': '34'} == request['headers']


def test_header_integer(empty_swagger_spec, param_spec):
    param_spec['in'] = 'header'
    param_spec['type'] = 'integer'
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {},
    }
    marshal_param(param, 34, request)
    assert {'petId': '34'} == request['headers']


def test_body(empty_swagger_spec, param_spec):
    param_spec['in'] = 'body'
    param_spec['schema'] = {
        'type': 'integer',
    }
    del param_spec['type']
    del param_spec['format']
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {
        },
    }
    marshal_param(param, 34, request)
    assert '34' == request['data']
    assert APP_JSON == request['headers']['Content-Type']


def test_formData_integer(empty_swagger_spec, param_spec):
    param_spec['in'] = 'formData'
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    request = {
        'headers': {
        },
    }
    marshal_param(param, 34, request)
    assert 34 == request['data']['petId']


def test_formData_file(empty_swagger_spec, param_spec, request_dict):
    param_spec['in'] = 'formData'
    param_spec['type'] = 'file'
    param = Param(
        empty_swagger_spec,
        Mock(spec=Operation, consumes=['multipart/form-data']),
        param_spec,
    )
    marshal_param(param, "i am the contents of a file", request_dict)
    expected = {
        'params': {},
        'files': [('petId', ('petId', "i am the contents of a file"))],
    }
    assert expected == request_dict


def assert_validate_call_count(expected_call_count, config, petstore_dict):
    with patch('bravado_core.param.validate_schema_object') as m_validate:
        petstore_spec = Spec.from_dict(petstore_dict, config=config)
        request = {'url': '/pet/{petId}'}
        op = petstore_spec.resources['pet'].operations['getPetById']
        param = op.params['petId']
        marshal_param(param, 34, request)
        assert expected_call_count == m_validate.call_count


def test_dont_validate_requests(petstore_dict):
    assert_validate_call_count(0, {'validate_requests': False}, petstore_dict)


def test_validate_requests(petstore_dict):
    assert_validate_call_count(1, {'validate_requests': True}, petstore_dict)


def test_ref(minimal_swagger_dict, array_param_spec, request_dict):
    ref_spec = {'$ref': '#/refs/ArrayParam'}
    minimal_swagger_dict['refs'] = {
        'ArrayParam': array_param_spec,
    }
    swagger_spec = Spec(minimal_swagger_dict)
    param = Param(swagger_spec, Mock(spec=Operation), ref_spec)
    value = ['cat', 'dog', 'bird']
    expected = copy.deepcopy(request_dict)
    expected['params']['animals'] = ','.join(value)
    marshal_param(param, value, request_dict)
    assert expected == request_dict


def test_required_param(minimal_swagger_spec, string_param_spec, request_dict):
    string_param_spec['required'] = True
    value = 'abc'
    param = Param(
        minimal_swagger_spec, Mock(
            spec=Operation,
        ), string_param_spec,
    )
    expected = copy.deepcopy(request_dict)
    expected['params']['username'] = value
    marshal_param(param, value, request_dict)
    assert expected == request_dict


def test_required_param_failure(
    minimal_swagger_spec, string_param_spec,
    request_dict,
):
    string_param_spec['required'] = True
    value = None
    param = Param(
        minimal_swagger_spec, Mock(
            spec=Operation,
        ), string_param_spec,
    )
    with pytest.raises(ValidationError) as excinfo:
        marshal_param(param, value, request_dict)
    assert 'is a required parameter' in str(excinfo.value)


@pytest.mark.parametrize(
    'param_value, expected_value',
    [
        (None, None),
        ({'an-attribute': datetime.date(2018, 5, 24)}, {'an-attribute': '2018-05-24'}),
    ],
)
def test_body_parameter_not_present_not_required(empty_swagger_spec, request_dict, param_value, expected_value):
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
    request = {
        'headers': {
        },
    }
    param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
    marshal_param(param, param_value, request)
    assert expected_value == (loads(request['data']) if 'data' in request else None)


@pytest.mark.parametrize(
    'param_required, param_type, param_format, param_python_value, param_string_value',
    [
        (True, 'boolean', None, True, 'true'),
        (True, 'boolean', None, False, 'false'),
        (True, 'string', None, 'String', 'String'),
        (True, 'string', 'date', datetime.date(2018, 7, 3), '2018-07-03'),
        (False, 'string', None, 'String', 'String'),
        (False, 'string', None, None, None),
    ],
)
def test_boolean_query_params_are_lower_case(
    minimal_swagger_dict, param_required, param_type, param_format, param_python_value, param_string_value,
):
    op_spec = {
        'operationId': 'get_pet_by_id',
        # op params would go here
        'responses': {
            '200': {
            },
        },
    }
    param_spec = {
        'name': 'querry-param',
        'in': 'query',
        'required': param_required,
        'type': param_type,
    }
    if param_format is not None:
        param_spec['format'] = param_format

    path_spec = {
        'get': op_spec,
        'parameters': [param_spec],
    }

    minimal_swagger_dict['paths']['/pets'] = path_spec
    swagger_spec = Spec(minimal_swagger_dict)
    request_dictionary = {'params': {}}

    param = Param(swagger_spec, Mock(spec=Operation), param_spec)
    marshal_param(param, param_python_value, request_dictionary)

    if param_required or param_python_value is not None:
        assert request_dictionary['params'][param_spec['name']] == param_string_value
    else:
        assert param_spec['name'] not in request_dictionary['params']

    # Checks that the conversion back continues to work
    request_object = Mock(spec=IncomingRequest, query={param_spec['name']: param_string_value})
    assert unmarshal_param(param, request_object) == param_python_value


@pytest.mark.parametrize(
    'param_type, param_value, expected_param_value',
    (
        ('string', 'abc', 'abc'),
        ('string', 5, '5'),
        ('boolean', True, 'true'),
        ('boolean', False, 'false'),
        ('array', [1, 2], [1, 2]),
    ),
)
def test_encode_request_param(param_type, param_value, expected_param_value):
    value = encode_request_param(param_type, 'some_name', param_value)
    assert value == expected_param_value
