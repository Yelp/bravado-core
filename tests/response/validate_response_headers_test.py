from jsonschema.exceptions import ValidationError
from mock import Mock
import pytest

from bravado_core.response import validate_response_headers, OutgoingResponse


def test_no_headers():
    response_spec = {'description': 'I have no headers'}
    response = Mock(spec=OutgoingResponse)
    # no exception raised == success
    validate_response_headers(response_spec, response)


def test_empty_headers():
    response_spec = {
        'description': 'I have headers, but it is empty',
        'headers': {},
    }
    response = Mock(spec=OutgoingResponse)
    # no exception raised == success
    validate_response_headers(response_spec, response)


def test_valid_headers():
    response_spec = {
        'description': 'I have one header',
        'headers': {
            'X-Foo': {
                'type': 'string'
            }
        },
    }
    response = Mock(spec=OutgoingResponse, headers={'X-Foo': 'bar'})
    # no exception raised == success
    validate_response_headers(response_spec, response)


def test_invalid_headers():
    response_spec = {
        'description': 'I have one header',
        'headers': {
            'X-Foo': {
                'type': 'integer'
            }
        },
    }
    response = Mock(spec=OutgoingResponse, headers={'X-Foo': 'bar'})
    with pytest.raises(ValidationError) as excinfo:
        validate_response_headers(response_spec, response)
    assert "is not of type 'integer'" in str(excinfo.value)
