from mock import Mock
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation
from bravado_core.response import validate_response_body, OutgoingResponse


@pytest.fixture
def no_return_value_spec():
    """
    :return: a response_spec that has no return value
    """
    return {
        'description': 'I do not return anything hence I have no "schema" key'
    }


def test_success_spec_empty_and_body_None(minimal_swagger_spec):
    response_spec = {
        'description': 'I do not return anything hence I have no "schema" key'
    }
    response = Mock(spec=OutgoingResponse, text=None)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec={})
    # no exception raised == success
    validate_response_body(op, response_spec, response)


def test_success_spec_empty_and_body_empty(minimal_swagger_spec):
    response_spec = {
        'description': 'I do not return anything hence I have no "schema" key'
    }
    response = Mock(spec=OutgoingResponse, text='')
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec={})
    validate_response_body(op, response_spec, response)


def test_success_json_response(minimal_swagger_spec):
    response_spec = {
        'description': 'Address',
        'schema': {
            'type': 'object',
            'properties': {
                'first_name': {
                    'type': 'string',
                },
                'last_name': {
                    'type': 'string',
                }
            }
        }
    }
    op = Operation(minimal_swagger_spec, '/foo', 'get',
                   op_spec={'produces': ['application/json']})
    response = Mock(
        spec=OutgoingResponse,
        content_type='application/json',
        json=Mock(
            spec=dict,
            return_value={
                'first_name': 'darwin',
                'last_name': 'niwrad'
            }
        )
    )
    validate_response_body(op, response_spec, response)


def test_failure_spec_empty_with_body_not_empty(minimal_swagger_spec):
    response_spec = {
        'description': 'I do not return anything hence I have no "schema" key'
    }
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec={})
    response = Mock(
        spec=OutgoingResponse,
        text="I am the body and I am not empty even though the response_spec "
             "says I should be")
    with pytest.raises(SwaggerMappingError) as excinfo:
        validate_response_body(op, response_spec, response)
    assert 'should be empty' in str(excinfo.value)


def test_failure_response_content_type_not_supported_by_operation(
        minimal_swagger_spec):
    response_spec = {
        'description': 'I return an int',
        'schema': {
            'type': 'integer',
        }
    }
    op = Operation(minimal_swagger_spec, '/foo', 'get',
                   op_spec={'produces': ['application/xml']})
    response = Mock(spec=OutgoingResponse, content_type='application/json')
    with pytest.raises(SwaggerMappingError) as excinfo:
        validate_response_body(op, response_spec, response)
    assert 'is not supported' in str(excinfo.value)


def test_failure_response_content_type_not_supported_by_bravado_core(
        minimal_swagger_spec):
    response_spec = {
        'description': 'I return an int',
        'schema': {
            'type': 'integer',
        }
    }
    op = Operation(minimal_swagger_spec, '/foo', 'get',
                   op_spec={'produces': ['application/xml']})
    response = Mock(spec=OutgoingResponse, content_type='application/xml')
    with pytest.raises(SwaggerMappingError) as excinfo:
        validate_response_body(op, response_spec, response)
    assert 'Unsupported content-type' in str(excinfo.value)
