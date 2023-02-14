# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import ValidationError
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from bravado_core.swagger20_validator import required_validator


@pytest.fixture
def param_spec():
    return {
        'name': 'foo',
        'in': 'query',
        'required': True,
    }


def test_fail_if_required_parameter_but_not_present(
    minimal_swagger_spec, param_spec,
):
    errors = list(
        required_validator(
            minimal_swagger_spec,
            validator=None,
            required=param_spec['required'],
            instance=None,
            schema=param_spec,
        ),
    )
    error = errors[0]
    assert isinstance(error, ValidationError)
    assert 'foo is a required parameter' in str(error)


def test_pass_if_not_required_parameter_and_not_present(
    minimal_swagger_spec, param_spec,
):
    param_spec['required'] = False
    errors = list(
        required_validator(
            minimal_swagger_spec,
            validator=None,
            required=param_spec['required'],
            instance=None,
            schema=param_spec,
        ),
    )
    assert len(errors) == 0


@patch('bravado_core.swagger20_validator._DRAFT4_REQUIRED_VALIDATOR')
def test_call_to_jsonschema_if_not_param(jsonschema_required_validator, minimal_swagger_spec):
    property_spec = {'type': 'integer'}
    validator = Mock()
    required = True
    instance = 34
    list(
        required_validator(
            minimal_swagger_spec,
            validator,
            required,
            instance,
            property_spec,
        ),
    )
    jsonschema_required_validator.assert_called_once_with(validator, required, instance, property_spec)
