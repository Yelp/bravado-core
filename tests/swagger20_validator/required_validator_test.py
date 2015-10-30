import mock

from jsonschema.exceptions import ValidationError

from bravado_core.swagger20_validator import required_validator


def test_fail_if_required_parameter_but_not_present(minimal_swagger_spec):
    param_schema = {'name': 'foo', 'in': 'query', 'required': True}
    result = required_validator(
        minimal_swagger_spec,
        validator=None,
        required=param_schema['required'],
        instance=None,
        schema=param_schema)
    error = result[0]
    assert isinstance(error, ValidationError)
    assert 'foo is required' in str(error)


def test_pass_if_not_required_parameter_and_not_present(minimal_swagger_spec):
    param_schema = {'name': 'foo', 'in': 'query', 'required': False}
    assert required_validator(
        minimal_swagger_spec, None, param_schema['required'], None,
        param_schema) is None


def test_call_to_jsonschema_if_not_param(minimal_swagger_spec):
    param_schema = {'name': 'foo', 'required': True}
    with mock.patch('jsonschema._validators.required_draft4') as m:
        required_validator(minimal_swagger_spec, 'a', 'b', 'c', param_schema)
    m.assert_called_once_with('a', 'b', 'c', param_schema)
