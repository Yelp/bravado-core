# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import ValidationError
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bravado_core.operation import Operation
from bravado_core.response import OutgoingResponse
from bravado_core.response import validate_response_headers


@pytest.fixture
def op(minimal_swagger_spec):
    return Operation(
        minimal_swagger_spec,
        '/foo',
        'get',
        op_spec={'produces': ['application/json']},
    )


def test_no_headers(op):
    response_spec = {'description': 'I have no headers'}
    response = Mock(spec=OutgoingResponse)
    # no exception raised == success
    validate_response_headers(op, response_spec, response)


def test_empty_headers(op):
    response_spec = {
        'description': 'I have headers, but it is empty',
        'headers': {},
    }
    response = Mock(spec=OutgoingResponse)
    # no exception raised == success
    validate_response_headers(op, response_spec, response)


def test_valid_headers(op):
    response_spec = {
        'description': 'I have one header',
        'headers': {
            'X-Foo': {
                'type': 'string',
            },
        },
    }
    response = Mock(spec=OutgoingResponse, headers={'X-Foo': 'bar'})
    # no exception raised == success
    validate_response_headers(op, response_spec, response)


def test_invalid_headers(op):
    response_spec = {
        'description': 'I have one header',
        'headers': {
            'X-Foo': {
                'type': 'integer',
            },
        },
    }
    response = Mock(spec=OutgoingResponse, headers={'X-Foo': 'bar'})
    with pytest.raises(ValidationError) as excinfo:
        validate_response_headers(op, response_spec, response)
    assert "is not of type 'integer'" in str(excinfo.value)
    assert "X-Foo" in str(excinfo.value)
