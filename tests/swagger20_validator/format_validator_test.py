# -*- coding: utf-8 -*-
import pytest
from jsonschema import ValidationError
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from bravado_core.exception import SwaggerValidationError
from bravado_core.formatter import SwaggerFormat
from bravado_core.swagger20_validator import format_validator
from bravado_core.validate import validate_object


@patch('bravado_core.swagger20_validator._DRAFT4_FORMAT_VALIDATOR')
def test_skip_when_validating_a_parameter_schema_and_parameter_value_is_None(
    m_format_validator, minimal_swagger_spec,
):
    param_schema = {
        'name': 'foo',
        'in': 'query',
        'type': 'string',
        'format': 'url',
    }
    list(
        format_validator(
            minimal_swagger_spec,
            validator=None,
            format=param_schema['format'],
            instance=None,  # parameter value
            schema=param_schema,
        ),
    )
    assert m_format_validator.call_count == 0


@patch('bravado_core.swagger20_validator._DRAFT4_FORMAT_VALIDATOR')
def test_validate_when_parameter_schema_and_parameter_value_is_not_None(
    m_format_validator, minimal_swagger_spec,
):
    param_schema = {
        'name': 'foo',
        'in': 'query',
        'type': 'string',
        'format': 'url',
    }
    args = (
        None, param_schema['format'], 'foo',
        param_schema,
    )
    list(format_validator(minimal_swagger_spec, *args))
    m_format_validator.assert_called_once_with(*args)


@patch('bravado_core.swagger20_validator._DRAFT4_FORMAT_VALIDATOR')
def test_validate_when_not_a_parameter_schema(
    m_format_validator, minimal_swagger_spec,
):
    string_schema = {
        'name': 'foo',
        'type': 'string',
        'format': 'url',
    }
    args = (
        None, string_schema['format'], 'foo',
        string_schema,
    )
    list(format_validator(minimal_swagger_spec, *args))
    m_format_validator.assert_called_once_with(*args)


@patch('bravado_core.swagger20_validator._DRAFT4_FORMAT_VALIDATOR')
def test_skip_when_nullable_property_schema_and_value_is_None(
    m_format_validator, minimal_swagger_spec,
):
    prop_schema = {
        'x-nullable': True,
        'type': 'string',
        'format': 'url',
    }
    list(
        format_validator(
            minimal_swagger_spec,
            validator=None,
            format=prop_schema['format'],
            instance=None,  # property value
            schema=prop_schema,
        ),
    )
    assert m_format_validator.call_count == 0


@patch('bravado_core.swagger20_validator._DRAFT4_FORMAT_VALIDATOR')
def test_validate_when_not_nullable_property_schema_and_value_is_None(
    m_format_validator, minimal_swagger_spec,
):
    prop_schema = {
        'x-nullable': False,
        'type': 'string',
        'format': 'url',
    }
    args = (None, prop_schema['format'], None, prop_schema)
    list(format_validator(minimal_swagger_spec, *args))
    m_format_validator.assert_called_once_with(*args)


def validate_dummy(dummy_string):
    if dummy_string != 'dummy':
        raise SwaggerValidationError('dummy')


DummyFormat = SwaggerFormat(
    format="dummy",
    to_wire=lambda x: x,  # type: ignore
    to_python=lambda x: x,  # type: ignore
    validate=validate_dummy,
    description="dummy format",
)


@pytest.mark.parametrize(
    'value, format_, x_nullable, expect_exception',
    (
        [{'prop': 'dummy'}, 'dummy', False, False],
        [{'prop': 'hello'}, 'dummy', False, True],
        [{'prop': None}, 'dummy', False, True],
        [{'prop': None}, 'dummy', True, False],
    ),
)
def test_validate_object_with_different_format_configurations(
    minimal_swagger_spec, value, format_, x_nullable, expect_exception,
):
    minimal_swagger_spec.spec_dict['definitions']['obj'] = {
        'properties': {
            'prop': {
                'type': 'string',
                'format': format_,
                'x-nullable': x_nullable,
            },
        },
    }
    minimal_swagger_spec.register_format(DummyFormat)
    captured_exception = None
    try:
        validate_object(
            swagger_spec=minimal_swagger_spec,
            object_spec=minimal_swagger_spec.spec_dict['definitions']['obj'],
            value=value,
        )
    except ValidationError as e:
        captured_exception = e

    if not expect_exception:
        assert captured_exception is None
    else:
        assert (
            captured_exception.message == '{0} is not a \'dummy\''.format(repr(value['prop'])) or
            captured_exception.message == '{0} is not of type \'string\''.format(repr(value['prop']))
        )
