# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import ValidationError

from bravado_core.validate import validate_primitive
from tests.validate.conftest import email_address_format


@pytest.fixture
def integer_spec():
    return {'type': 'integer'}


@pytest.fixture
def number_spec():
    return {'type': 'number'}


@pytest.fixture
def string_spec():
    return {'type': 'string'}


@pytest.fixture
def boolean_spec():
    return {'type': 'boolean'}


def test_integer_success(minimal_swagger_spec, integer_spec):
    validate_primitive(minimal_swagger_spec, integer_spec, 10)
    validate_primitive(minimal_swagger_spec, integer_spec, -10)


def test_integer_failure(minimal_swagger_spec, integer_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, integer_spec, 'i am a string')
    assert "is not of type 'integer'" in str(excinfo.value)


def test_integer_multipleOf_success(minimal_swagger_spec, integer_spec):
    integer_spec['multipleOf'] = 2
    validate_primitive(minimal_swagger_spec, integer_spec, 10)


def test_integer_multipleOf_failure(minimal_swagger_spec, integer_spec):
    integer_spec['multipleOf'] = 2
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, integer_spec, 7)
    assert "not a multiple of" in str(excinfo.value)


def test_integer_maximum_success(minimal_swagger_spec, integer_spec):
    integer_spec['maximum'] = 10
    validate_primitive(minimal_swagger_spec, integer_spec, 5)


def test_integer_maximum_failure(minimal_swagger_spec, integer_spec):
    integer_spec['maximum'] = 10
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, integer_spec, 11)
    assert "greater than the maximum" in str(excinfo.value)


def test_integer_exclusiveMaximum_success(minimal_swagger_spec, integer_spec):
    integer_spec['maximum'] = 10
    integer_spec['exclusiveMaximum'] = True
    validate_primitive(minimal_swagger_spec, integer_spec, 9)


def test_integer_exclusiveMaximum_failure(minimal_swagger_spec, integer_spec):
    integer_spec['maximum'] = 10
    integer_spec['exclusiveMaximum'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, integer_spec, 10)
    assert "greater than or equal to the maximum" in str(excinfo.value)


def test_integer_minimum_success(minimal_swagger_spec, integer_spec):
    integer_spec['minimum'] = 10
    validate_primitive(minimal_swagger_spec, integer_spec, 15)


def test_integer_minimum_failure(minimal_swagger_spec, integer_spec):
    integer_spec['minimum'] = 10
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, integer_spec, 9)
    assert "less than the minimum" in str(excinfo.value)


def test_integer_exclusiveMinimum_success(minimal_swagger_spec, integer_spec):
    integer_spec['minimum'] = 10
    integer_spec['exclusiveMinimum'] = True
    validate_primitive(minimal_swagger_spec, integer_spec, 11)


def test_integer_exclusiveMinimum_failure(minimal_swagger_spec, integer_spec):
    integer_spec['minimum'] = 10
    integer_spec['exclusiveMinimum'] = True
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, integer_spec, 10)
    assert "less than or equal to the minimum" in str(excinfo.value)


def test_boolean_success(minimal_swagger_spec, boolean_spec):
    validate_primitive(minimal_swagger_spec, boolean_spec, True)
    validate_primitive(minimal_swagger_spec, boolean_spec, False)


def test_boolean_falure(minimal_swagger_spec, boolean_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, boolean_spec, "foo")
    assert "is not of type 'boolean'" in str(excinfo.value)


def test_number_success(minimal_swagger_spec, number_spec):
    validate_primitive(minimal_swagger_spec, number_spec, 3.14)


def test_number_failure(minimal_swagger_spec, number_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, number_spec, "foo")
    assert "is not of type 'number'" in str(excinfo.value)


def test_number_multipleOf_success(minimal_swagger_spec, number_spec):
    number_spec['multipleOf'] = 2.3
    validate_primitive(minimal_swagger_spec, number_spec, 4.6)


def test_number_multipleOf_failure(minimal_swagger_spec, number_spec):
    number_spec['multipleOf'] = 2.3
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, number_spec, 9.1)
    assert "not a multiple of" in str(excinfo.value)


def test_string_success(minimal_swagger_spec, string_spec):
    validate_primitive(minimal_swagger_spec, string_spec, 'foo')
    validate_primitive(minimal_swagger_spec, string_spec, u'bar')


def test_string_failure(minimal_swagger_spec, string_spec):
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, 999)
    assert "is not of type 'string'" in str(excinfo.value)


def test_string_minLength_success(minimal_swagger_spec, string_spec):
    string_spec['minLength'] = 2
    validate_primitive(minimal_swagger_spec, string_spec, 'abc')


def test_string_minLength_failure(minimal_swagger_spec, string_spec):
    string_spec['minLength'] = 3
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, 'ab')
    assert "is too short" in str(excinfo.value)


def test_string_maxLength_success(minimal_swagger_spec, string_spec):
    string_spec['maxLength'] = 2
    validate_primitive(minimal_swagger_spec, string_spec, 'ab')


def test_string_maxLength_failure(minimal_swagger_spec, string_spec):
    string_spec['maxLength'] = 3
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, 'abcdef')
    assert "is too long" in str(excinfo.value)


def test_string_pattern_success(minimal_swagger_spec, string_spec):
    string_spec['pattern'] = 'foo'
    validate_primitive(minimal_swagger_spec, string_spec, 'feefiefoofum')


def test_string_pattern_failure(minimal_swagger_spec, string_spec):
    string_spec['pattern'] = 'foo'
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, 'abcdef')
    assert "does not match" in str(excinfo.value)


def test_string_enum_success(minimal_swagger_spec, string_spec):
    string_spec['enum'] = ['inky', 'dinky', 'doo']
    validate_primitive(minimal_swagger_spec, string_spec, 'dinky')


def test_string_enum_failure(minimal_swagger_spec, string_spec):
    string_spec['enum'] = ['inky', 'dinky', 'doo']
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, 'abc')
    assert "is not one of" in str(excinfo.value)


def test_string_datetime_success(minimal_swagger_spec, string_spec):
    string_spec['format'] = 'date-time'
    datestring = "2016-06-07T20:59:00.480Z"
    validate_primitive(minimal_swagger_spec, string_spec, datestring)


def test_string_datetime_invalid_exception(minimal_swagger_spec, string_spec):
    string_spec['format'] = 'date-time'
    datestring = "nope nope nope"
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, datestring)
    assert "is not a 'date-time'" in str(excinfo.value)


def test_doesnt_blow_up_when_spec_has_a_required_key(minimal_swagger_spec):
    string_spec = {
        'type': 'string',
        'required': True,
    }
    validate_primitive(minimal_swagger_spec, string_spec, 'foo')


@pytest.fixture
def email_address_spec():
    return {
        'type': 'string',
        'format': 'email_address',
    }


def test_user_defined_format_success(minimal_swagger_spec, email_address_spec):
    request_body = 'foo@bar.com'
    minimal_swagger_spec.register_format(email_address_format)
    # No exception thrown == success
    validate_primitive(minimal_swagger_spec, email_address_spec, request_body)


def test_user_defined_format_failure(minimal_swagger_spec, email_address_spec):
    request_body = 'i_am_not_a_valid_email_address'
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, email_address_spec,
                           request_body)
    assert "'i_am_not_a_valid_email_address' is not a 'email_address'" in \
        str(excinfo.value)


def test_builtin_format_still_works_when_user_defined_format_used(
        minimal_swagger_spec):
    ipaddress_spec = {
        'type': 'string',
        'format': 'ipv4',
    }
    request_body = 'not_an_ip_address'
    minimal_swagger_spec.register_format(email_address_format)
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, ipaddress_spec, request_body)
    assert "'not_an_ip_address' is not a 'ipv4'" in str(excinfo.value)


# Tests related to x-nullable

# Validation should pass if `x-nullable` is `True` and the value is `None`.
# `required` is not possible in this scenario.
#
# +---------------------+------------------+
# | x-nullable == False | 'x'  -> pass (1) |
# |                     | None -> fail (2) |
# +---------------------+------------------+
# | x-nullable == True  | 'x'  -> pass (3) |
# |                     | None -> pass (4) |
# +---------------------+------------------+


@pytest.mark.parametrize(['nullable', 'value'],
                         [(False, 'x'), (True, 'x'), (True, None)])
def test_nullable_pass(minimal_swagger_spec, string_spec, value, nullable):
    """Test scenarios in which validation should pass: (1), (3), (4)"""
    string_spec['x-nullable'] = nullable

    validate_primitive(minimal_swagger_spec, string_spec, value)


def test_nullable_fail(minimal_swagger_spec, string_spec):
    """Test scenarios in which validation should fail: (2)"""

    string_spec['x-nullable'] = False
    with pytest.raises(ValidationError) as excinfo:
        validate_primitive(minimal_swagger_spec, string_spec, None)
    assert excinfo.value.message == "None is not of type 'string'"
