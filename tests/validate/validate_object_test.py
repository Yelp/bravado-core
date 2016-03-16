from jsonschema.exceptions import ValidationError
import pytest

from bravado_core.validate import validate_object
from tests.validate.conftest import email_address_format


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
                    'Boulevard',
                ]
            }
        }
    }


def test_success(minimal_swagger_spec, address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(minimal_swagger_spec, address_spec, address)


def test_leaving_out_property_OK(minimal_swagger_spec, address_spec):
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    validate_object(minimal_swagger_spec, address_spec, address)


def test_additional_property_OK(minimal_swagger_spec, address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
        'city': 'Swaggerville'
    }
    validate_object(minimal_swagger_spec, address_spec, address)


def test_required_OK(minimal_swagger_spec, address_spec):
    address_spec['required'] = ['number']
    address = {
        'street_name': 'Main',
        'street_type': 'Street',
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, address_spec, address)
    assert 'is a required property' in str(excinfo.value)


def test_property_with_no_schema(minimal_swagger_spec, address_spec):
    address = {
        'number': 1000,
        'street_name': 'Main',
        'street_type': 'Street',
    }
    del address_spec['properties']['street_name']['type']
    validate_object(minimal_swagger_spec, address_spec, address)


@pytest.fixture
def email_address_object_spec():
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


def test_user_defined_format_success(minimal_swagger_spec,
                                     email_address_object_spec):
    request_body = {'email_address': 'foo@bar.com'}
    minimal_swagger_spec.register_format(email_address_format)
    # No exception thrown == success
    validate_object(minimal_swagger_spec,
                    email_address_object_spec, request_body)


def test_user_defined_format_failure(minimal_swagger_spec,
                                     email_address_object_spec):
    request_body = {'email_address': 'i_am_not_a_valid_email_address'}
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, email_address_object_spec,
                        request_body)
    assert "'i_am_not_a_valid_email_address' is not a 'email_address'" in \
        str(excinfo.value)


def test_builtin_format_still_works_when_user_defined_format_used(
        minimal_swagger_spec):
    ipaddress_spec = {
        'type': 'object',
        'required': ['ipaddress'],
        'properties': {
            'ipaddress': {
                'type': 'string',
                'format': 'ipv4',
            }
        }
    }
    request_body = {'ipaddress': 'not_an_ip_address'}
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_object(minimal_swagger_spec, ipaddress_spec, request_body)
    assert "'not_an_ip_address' is not a 'ipv4'" in str(excinfo.value)


def test_recursive_ref_depth_1(recursive_swagger_spec):
    validate_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        {'name': 'foo'})


def test_recursive_ref_depth_n(recursive_swagger_spec):
    value = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'name': 'baz'
            }
        }
    }
    validate_object(
        recursive_swagger_spec,
        {'$ref': '#/definitions/Node'},
        value)


def test_recursive_ref_depth_n_failure(recursive_swagger_spec):
    value = {
        'name': 'foo',
        'child': {
            'name': 'bar',
            'child': {
                'kaboom': 'baz'  # <-- key should be 'name', not 'kabbom'
            }
        }
    }
    with pytest.raises(ValidationError) as excinfo:
        validate_object(
            recursive_swagger_spec,
            {'$ref': '#/definitions/Node'},
            value)
    assert "'name' is a required property" in str(excinfo.value)
