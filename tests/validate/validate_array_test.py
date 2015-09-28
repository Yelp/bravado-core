from jsonschema.exceptions import ValidationError
import pytest

from bravado_core.validate import validate_array
from tests.validate.conftest import registered_format, email_address_format


@pytest.fixture
def int_array_spec():
    return {
        'type': 'array',
        'items': {
            'type': 'integer',
        }
    }


def test_minItems_success(int_array_spec):
    int_array_spec['minItems'] = 2
    validate_array(int_array_spec, [1, 2, 3])


def test_minItems_failure(int_array_spec):
    int_array_spec['minItems'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_array(int_array_spec, [1])
    assert 'is too short' in str(excinfo)


def test_maxItems_success(int_array_spec):
    int_array_spec['maxItems'] = 2
    validate_array(int_array_spec, [1])


def test_maxItems_failure(int_array_spec):
    int_array_spec['maxItems'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_array(int_array_spec, [1, 2, 3, 4])
    assert 'is too long' in str(excinfo)


def test_unqiueItems_true_success(int_array_spec):
    int_array_spec['uniqueItems'] = True
    validate_array(int_array_spec, [1, 2, 3])


def test_uniqueItems_true_failure(int_array_spec):
    int_array_spec['uniqueItems'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_array(int_array_spec, [1, 2, 1, 4])
    assert 'has non-unique elements' in str(excinfo)


def test_uniqueItems_false(int_array_spec):
    int_array_spec['uniqueItems'] = False
    validate_array(int_array_spec, [1, 2, 3])
    validate_array(int_array_spec, [1, 2, 1, 4])


@pytest.fixture
def email_address_array_spec():
    return {
        'type': 'array',
        'items': {
            'type': 'string',
            'format': 'email_address',
        }
    }


def test_user_defined_format_success(email_address_array_spec):
    request_body = ['foo@bar.com']
    with registered_format(email_address_format):
        # No exception thrown == success
        validate_array(email_address_array_spec, request_body)


def test_user_defined_format_failure(email_address_array_spec):
    request_body = ['i_am_not_a_valid_email_address']

    with registered_format(email_address_format):
        with pytest.raises(ValidationError) as excinfo:
            validate_array(email_address_array_spec, request_body)
        assert "'i_am_not_a_valid_email_address' is not a 'email_address'" in \
            str(excinfo.value)


def test_builtin_format_still_works():
    ipaddress_array_spec = {
        'type': 'array',
        'items': {
            'type': 'string',
            'format': 'ipv4',
        }
    }
    request_body = ['not_an_ip_address']
    with pytest.raises(ValidationError) as excinfo:
        validate_array(ipaddress_array_spec, request_body)
    assert "'not_an_ip_address' is not a 'ipv4'" in str(excinfo.value)
