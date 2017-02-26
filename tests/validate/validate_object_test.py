# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import ValidationError

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


@pytest.fixture
def allOf_spec(address_spec):
    return {
        'allOf': [
            {
                'type': 'object',
                'properties': {
                    'business': {
                        'type': 'string'
                    },
                },
                'required': ['business'],
            },
            address_spec,
        ]
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


# x-nullable validation
# ---------------------
# If the value is an object, validation should pass if
# `x-nullable` is `True` and the value is `None`. `required` doesn't
# have an influence.
#
# +---------------------+-------------------------+--------------------------+
# |                     | required == False       | required == True         |
# +---------------------+-------------------------+--------------------------+
# | x-nullable == False | {}          -> pass (1) | {}          -> fail  (4) |
# |                     | {'x': 'y'}  -> pass (2) | {'x': 'y'}  -> pass  (5) |
# |                     | {'x': None} -> fail (3) | {'x': None} -> fail  (6) |
# +---------------------+-------------------------+--------------------------+
# | x-nullable == True  | {}          -> pass (7) | {}          -> fail (10) |
# |                     | {'x': 'y'}  -> pass (8) | {'x': 'y'}  -> pass (11) |
# |                     | {'x': None} -> pass (9) | {'x': None} -> pass (12) |
# +---------------------+-------------------------+--------------------------+


def content_spec_factory(required, nullable):
    return {
        'type': 'object',
        'required': ['x'] if required else [],
        'properties': {
            'x': {
                'type': 'string',
                'x-nullable': nullable,
            }
        }
    }


@pytest.mark.parametrize('nullable', [True, False])
@pytest.mark.parametrize('required', [True, False])
def test_nullable_with_value(empty_swagger_spec, nullable, required):
    """With a value set, validation should always pass: (2), (5), (8), (11)"""
    content_spec = content_spec_factory(required, nullable)
    value = {'x': 'y'}

    validate_object(empty_swagger_spec, content_spec, value)


@pytest.mark.parametrize('nullable', [True, False])
def test_nullable_required_no_value(empty_swagger_spec, nullable):
    """When the value is required but not set at all, validation
    should fail: (4), (10)
    """
    content_spec = content_spec_factory(True, nullable)
    value = {}

    with pytest.raises(ValidationError) as excinfo:
        validate_object(empty_swagger_spec, content_spec, value)
    assert excinfo.value.message == "'x' is a required property"


@pytest.mark.parametrize('nullable', [True, False])
def test_nullable_no_value(empty_swagger_spec, nullable):
    """When the value is not required and not set at all, validation
    should pass: (1), (7)
    """
    content_spec = content_spec_factory(False, nullable=nullable)
    value = {}

    validate_object(empty_swagger_spec, content_spec, value)


@pytest.mark.parametrize('required', [True, False])
def test_nullable_false_value_none(empty_swagger_spec, required):
    """When nullable is `False` and the value is set to `None`, validation
    should fail: (3), (6)
    """
    content_spec = content_spec_factory(required, False)
    value = {'x': None}

    with pytest.raises(ValidationError) as excinfo:
        validate_object(empty_swagger_spec, content_spec, value)
    assert excinfo.value.message == "None is not of type 'string'"


@pytest.mark.parametrize('required', [True, False])
def test_nullable_none_value(empty_swagger_spec, required):
    """When nullable is `True` and the value is set to `None`, validation
    should pass: (9), (12)
    """
    content_spec = content_spec_factory(required, True)
    value = {'x': None}

    validate_object(empty_swagger_spec, content_spec, value)


def test_allOf_minimal(empty_swagger_spec, allOf_spec):
    value = {
        'business': 'Yelp',
    }

    validate_object(empty_swagger_spec, allOf_spec, value)


def test_allOf_fails(empty_swagger_spec, allOf_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_object(empty_swagger_spec, allOf_spec, {})
    assert excinfo.value.message == "'business' is a required property"


def test_allOf_complex(composition_spec):
    pongclone_spec = composition_spec.spec_dict['definitions']['pongClone']

    value = {
        'additionalFeature': 'Badges',
        'gameSystem': 'NES',
        'pang': 'value',
        'releaseDate': 'October',
    }

    validate_object(composition_spec, pongclone_spec, value)


def test_allOf_complex_failure(composition_spec):
    pongclone_spec = composition_spec.spec_dict['definitions']['pongClone']

    value = {
        'additionalFeature': 'Badges',
        'pang': 'value',
        'releaseDate': 'October',
    }

    with pytest.raises(ValidationError) as excinfo:
        validate_object(composition_spec, pongclone_spec, value)
    assert excinfo.value.message == "'gameSystem' is a required property"
