from mock import Mock, patch

from bravado_core.spec import Spec
from bravado_core.swagger20_validator import enum_validator


@patch('jsonschema._validators.enum')
def test_multiple_jsonschema_call_ifs_enum_items_present_as_array(
        jsonschema_enum_validator):
    swagger_spec = Mock(spec=Spec)
    enums = ['a1', 'b2', 'c3']
    param_schema = {
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'enum': enums
    }
    # list() forces iteration over the generator
    list(enum_validator(swagger_spec, None, enums, ['a1', 'd4'], param_schema))
    jsonschema_enum_validator.assert_any_call(None, enums, 'a1', param_schema)
    jsonschema_enum_validator.assert_any_call(None, enums, 'd4', param_schema)


@patch('jsonschema._validators.enum')
def test_single_jsonschema_call_if_enum_instance_not_array(
        jsonschema_enum_validator):
    enums = ['a1', 'b2', 'c3']
    param_schema = {
        'enum': enums
    }
    swagger_spec = Mock(spec=Spec, deref=Mock(return_value=param_schema))
    # list() forces iteration over the generator
    list(enum_validator(swagger_spec, None, enums, ['a1', 'd4'], param_schema))
    jsonschema_enum_validator.assert_called_once_with(
        None, enums, ['a1', 'd4'], param_schema)


@patch('jsonschema._validators.enum')
def test_skip_validation_for_optional_enum_with_None_value(
        jsonschema_enum_validator):
    enums = ['encrypted', 'plaintext']
    param_schema = {
        'type': 'string',
        'in': 'query',
        'required': False,
        'enum': enums
    }
    swagger_spec = Mock(spec=Spec, deref=Mock(return_value=param_schema))
    param_value = None
    enum_validator(swagger_spec, None, enums, param_value, param_schema)
    assert jsonschema_enum_validator.call_count == 0
