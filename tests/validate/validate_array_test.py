# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import ValidationError

from bravado_core.validate import validate_array
from tests.validate.conftest import email_address_format


@pytest.fixture
def int_array_spec():
    return {
        'type': 'array',
        'items': {
            'type': 'integer',
        }
    }


def test_minItems_success(minimal_swagger_spec, int_array_spec):
    int_array_spec['minItems'] = 2
    validate_array(minimal_swagger_spec, int_array_spec, [1, 2, 3])


def test_minItems_failure(minimal_swagger_spec, int_array_spec):
    int_array_spec['minItems'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_array(minimal_swagger_spec, int_array_spec, [1])
    assert 'is too short' in str(excinfo)


def test_maxItems_success(minimal_swagger_spec, int_array_spec):
    int_array_spec['maxItems'] = 2
    validate_array(minimal_swagger_spec, int_array_spec, [1])


def test_maxItems_failure(minimal_swagger_spec, int_array_spec):
    int_array_spec['maxItems'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_array(minimal_swagger_spec, int_array_spec, [1, 2, 3, 4])
    assert 'is too long' in str(excinfo)


def test_unqiueItems_true_success(minimal_swagger_spec, int_array_spec):
    int_array_spec['uniqueItems'] = True
    validate_array(minimal_swagger_spec, int_array_spec, [1, 2, 3])


def test_uniqueItems_true_failure(minimal_swagger_spec, int_array_spec):
    int_array_spec['uniqueItems'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_array(minimal_swagger_spec, int_array_spec, [1, 2, 1, 4])
    assert 'has non-unique elements' in str(excinfo)


def test_uniqueItems_false(minimal_swagger_spec, int_array_spec):
    int_array_spec['uniqueItems'] = False
    validate_array(minimal_swagger_spec, int_array_spec, [1, 2, 3])
    validate_array(minimal_swagger_spec, int_array_spec, [1, 2, 1, 4])


@pytest.fixture
def email_address_array_spec():
    return {
        'type': 'array',
        'items': {
            'type': 'string',
            'format': 'email_address',
        }
    }


def test_user_defined_format_success(minimal_swagger_spec,
                                     email_address_array_spec):
    request_body = ['foo@bar.com']
    minimal_swagger_spec.register_format(email_address_format)
    # No exception thrown == success
    validate_array(minimal_swagger_spec, email_address_array_spec, request_body)


def test_user_defined_format_failure(minimal_swagger_spec,
                                     email_address_array_spec):
    request_body = ['i_am_not_a_valid_email_address']
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_array(minimal_swagger_spec, email_address_array_spec,
                       request_body)
    assert "'i_am_not_a_valid_email_address' is not a 'email_address'" in \
        str(excinfo.value)


def test_builtin_format_still_works_when_user_defined_format_used(
        minimal_swagger_spec):
    ipaddress_array_spec = {
        'type': 'array',
        'items': {
            'type': 'string',
            'format': 'ipv4',
        }
    }
    request_body = ['not_an_ip_address']
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_array(minimal_swagger_spec, ipaddress_array_spec, request_body)
    assert "'not_an_ip_address' is not a 'ipv4'" in str(excinfo.value)
