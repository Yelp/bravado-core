from mock import patch

from bravado_core.swagger20_validator import format_validator


@patch('jsonschema._validators.format')
def test_skip_when_validating_a_parameter_schema_and_parameter_value_is_None(
        m_format_validator, minimal_swagger_spec):
    param_schema = {'name': 'foo', 'in': 'query', 'type': 'string', 'format': 'url'}
    list(format_validator(
        minimal_swagger_spec,
        validator=None,
        format=param_schema['format'],
        instance=None,  # parameter value
        schema=param_schema))
    assert m_format_validator.call_count == 0


@patch('jsonschema._validators.format')
def test_validate_when_parameter_schema_and_parameter_value_is_not_None(
        m_format_validator, minimal_swagger_spec):
    param_schema = {'name': 'foo', 'in': 'query', 'type': 'string', 'format': 'url'}
    args = (None, param_schema['format'], 'foo',
            param_schema)
    list(format_validator(minimal_swagger_spec, *args))
    m_format_validator.assert_called_once_with(*args)


@patch('jsonschema._validators.format')
def test_validate_when_not_a_parameter_schema(m_format_validator,
                                              minimal_swagger_spec):
    string_schema = {'name': 'foo', 'type': 'string', 'format': 'url'}
    args = (None, string_schema['format'], 'foo',
            string_schema)
    list(format_validator(minimal_swagger_spec, *args))
    m_format_validator.assert_called_once_with(*args)


@patch('jsonschema._validators.format')
def test_skip_when_nullable_property_schema_and_value_is_None(
        m_format_validator, minimal_swagger_spec):
    prop_schema = {'x-nullable': True, 'type': 'string', 'format': 'url'}
    list(format_validator(
        minimal_swagger_spec,
        validator=None,
        format=prop_schema['format'],
        instance=None,  # property value
        schema=prop_schema))
    assert m_format_validator.call_count == 0


@patch('jsonschema._validators.format')
def test_validate_when_not_nullable_property_schema_and_value_is_None(
        m_format_validator, minimal_swagger_spec):
    prop_schema = {'x-nullable': False, 'type': 'string', 'format': 'url'}
    args = (None, prop_schema['format'], None, prop_schema)
    list(format_validator(minimal_swagger_spec, *args))
    m_format_validator.assert_called_once_with(*args)
