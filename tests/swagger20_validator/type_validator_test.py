# -*- coding: utf-8 -*-
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from bravado_core.swagger20_validator import type_validator


@patch('bravado_core.swagger20_validator._DRAFT4_TYPE_VALIDATOR')
def test_skip_when_validating_a_parameter_schema_and_parameter_value_is_None(
    m_draft4_type_validator, minimal_swagger_spec,
):
    param_schema = {'name': 'foo', 'in': 'query', 'type': 'string'}
    list(
        type_validator(
            minimal_swagger_spec,
            validator=None,
            types=param_schema['type'],
            instance=None,  # parameter value
            schema=param_schema,
        ),
    )
    assert m_draft4_type_validator.call_count == 0


@patch('bravado_core.swagger20_validator._DRAFT4_TYPE_VALIDATOR')
def test_validate_when_parameter_schema_and_parameter_value_is_not_None(
    m_draft4_type_validator, minimal_swagger_spec,
):
    param_schema = {'name': 'foo', 'in': 'query', 'type': 'string'}
    args = (
        None, param_schema['type'], 'foo',
        param_schema,
    )
    list(type_validator(minimal_swagger_spec, *args))
    m_draft4_type_validator.assert_called_once_with(*args)


@patch('bravado_core.swagger20_validator._DRAFT4_TYPE_VALIDATOR')
def test_validate_when_not_a_parameter_schema(
    m_draft4_type_validator, minimal_swagger_spec,
):
    string_schema = {'name': 'foo', 'type': 'string'}
    args = (
        None, string_schema['type'], 'foo',
        string_schema,
    )
    list(type_validator(minimal_swagger_spec, *args))
    m_draft4_type_validator.assert_called_once_with(*args)


@patch('bravado_core.swagger20_validator._DRAFT4_TYPE_VALIDATOR')
def test_skip_when_nullable_property_schema_and_value_is_None(
    m_draft4_type_validator, minimal_swagger_spec,
):
    prop_schema = {'x-nullable': True, 'type': 'string'}
    list(
        type_validator(
            minimal_swagger_spec,
            validator=None,
            types=prop_schema['type'],
            instance=None,  # property value
            schema=prop_schema,
        ),
    )
    assert m_draft4_type_validator.call_count == 0


@patch('bravado_core.swagger20_validator._DRAFT4_TYPE_VALIDATOR')
def test_validate_when_not_nullable_property_schema_and_value_is_None(
    m_draft4_type_validator, minimal_swagger_spec,
):
    prop_schema = {'x-nullable': False, 'type': 'string'}
    args = (None, prop_schema['type'], None, prop_schema)
    list(type_validator(minimal_swagger_spec, *args))
    m_draft4_type_validator.assert_called_once_with(*args)
