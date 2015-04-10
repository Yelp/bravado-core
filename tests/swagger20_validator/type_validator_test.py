from mock import patch

from bravado_core.swagger20_validator import type_validator


@patch('jsonschema._validators.type_draft4')
def test_skip_when_validating_a_parameter_schema_and_parameter_value_is_None(
        m_draft4_type_validator):
    param_schema = {'name': 'foo', 'in': 'query', 'type': 'string'}
    type_validator(
        validator=None,
        types=param_schema['type'],
        instance=None,  # parameter value
        schema=param_schema)
    assert m_draft4_type_validator.call_count == 0


@patch('jsonschema._validators.type_draft4')
def test_validate_when_parameter_schema_and_parameter_value_is_not_None(
        m_draft4_type_validator):
    param_schema = {'name': 'foo', 'in': 'query', 'type': 'string'}
    args = (None, param_schema['type'], 'foo', param_schema)
    type_validator(*args)
    m_draft4_type_validator.assert_called_once_with(*args)


@patch('jsonschema._validators.type_draft4')
def test_validate_when_not_a_parameter_schema(m_draft4_type_validator):
    string_schema = {'name': 'foo', 'type': 'string'}
    args = (None, string_schema['type'], 'foo', string_schema)
    type_validator(*args)
    m_draft4_type_validator.assert_called_once_with(*args)
