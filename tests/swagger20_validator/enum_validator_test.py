# -*- coding: utf-8 -*-
import pytest
from jsonschema import ValidationError
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from bravado_core.spec import Spec
from bravado_core.swagger20_validator import enum_validator
from bravado_core.validate import validate_object


def test_multiple_jsonschema_calls_if_enum_items_present_as_array():
    swagger_spec = Mock(spec=Spec)
    enums = ['a1', 'b2', 'c3']
    param_schema = {
        'type': 'array',
        'items': {
            'type': 'string',
        },
        'enum': enums,
    }
    # list() forces iteration over the generator
    errors = list(
        enum_validator(
            swagger_spec, None, enums, ['a1', 'd4'],
            param_schema,
        ),
    )
    assert len(errors) == 1
    assert "'d4' is not one of ['a1', 'b2', 'c3']" in str(errors[0])


@patch('bravado_core.swagger20_validator._DRAFT4_ENUM_VALIDATOR')
def test_single_jsonschema_call_if_enum_instance_not_array(jsonschema_enum_validator):
    enums = ['a1', 'b2', 'c3']
    param_schema = {
        'enum': enums,
    }
    swagger_spec = Mock(spec=Spec, deref=Mock(return_value=param_schema))
    # list() forces iteration over the generator
    list(enum_validator(swagger_spec, None, enums, ['a1', 'd4'], param_schema))
    jsonschema_enum_validator.assert_called_once_with(
        None, enums, ['a1', 'd4'], param_schema,
    )


@patch('bravado_core.swagger20_validator._DRAFT4_ENUM_VALIDATOR')
def test_skip_validation_for_optional_enum_with_None_value(jsonschema_enum_validator):
    enums = ['encrypted', 'plaintext']
    param_schema = {
        'type': 'string',
        'in': 'query',
        'required': False,
        'enum': enums,
    }
    swagger_spec = Mock(spec=Spec, deref=Mock(return_value=param_schema))
    param_value = None
    list(enum_validator(swagger_spec, None, enums, param_value, param_schema))
    assert jsonschema_enum_validator.call_count == 0


@pytest.mark.parametrize(
    'value, enum_values, expect_exception',
    (
        [{'prop': 'VAL'}, ['VAL'], False],
        [{'prop': None}, ['VAL'], False],
        [{'prop': 'In-Valid Value'}, ['VAL'], True],
    ),
)
def test_validate_object_with_different_enum_configurations(minimal_swagger_spec, value, enum_values, expect_exception):
    minimal_swagger_spec.spec_dict['definitions']['obj'] = {
        'properties': {
            'prop': {
                'type': 'string',
                'enum': enum_values,
                'x-nullable': True,
            },
        },
    }
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
        assert captured_exception.message == '\'{0}\' is not one of {1}'.format(value['prop'], enum_values)
