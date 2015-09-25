from contextlib import contextmanager

from jsonschema.exceptions import ValidationError
import pytest
from bravado_core.exception import SwaggerValidationError

from bravado_core.formatter import SwaggerFormat
from bravado_core.formatter import unregister_format
from bravado_core.formatter import register_format
from bravado_core.validate import validate_object


@pytest.fixture
def address_spec():
    return {
        'type': 'object',
        'properties': {
            'number': {
                'type': 'number'
            },
            'street_name': {
                'type': 'string'
            },
            'street_type': {
                'type': 'string',
                'enum': [
                    'Street',
                    'Avenue',
                    'Boulevard']
            }
        }
    }


def test_success(address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(address_spec, address)


def test_leaving_out_property_OK(address_spec):
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(address_spec, address)


def test_additional_property_OK(address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
        'city': 'Swaggerville'
    }
    validate_object(address_spec, address)


def test_required_OK(address_spec):
    address_spec['required'] = ['number']
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_object(address_spec, address)
    assert 'is a required property' in str(excinfo.value)


@pytest.fixture
def email_address_spec():
    return {
        'type': 'object',
        'required': ['email_address'],
        'properties': {
            'email_address': {
                'type': 'string',
                'format': 'email_address',
            }
        }
    }


def validate_email_address(email_address):
    if '@' not in email_address:
        raise SwaggerValidationError('dude, you need an @')


email_address_format = SwaggerFormat(
    format='email_address',
    to_wire=lambda x: x,
    to_python=lambda x: x,
    validate=validate_email_address,
    description='blah')


@contextmanager
def registered_format(swagger_format):
    register_format(swagger_format)
    try:
        yield
    finally:
        unregister_format(swagger_format)


def test_validates_user_defined_format_success(email_address_spec):
    request_body = {
        'email_address': 'foo@bar.com'
    }
    with registered_format(email_address_format):
        # No exception thrown == success
        validate_object(email_address_spec, request_body)


def test_validates_user_defined_format_failure(email_address_spec):
    request_body = {
        'email_address': 'i_am_not_a_valid_email_address'
    }
    with registered_format(email_address_format):
        with pytest.raises(ValidationError) as excinfo:
            validate_object(email_address_spec, request_body)
        assert "'i_am_not_a_valid_email_address' is not a 'email_address'" in \
            str(excinfo.value)
