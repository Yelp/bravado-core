import pytest
from mock import patch

from bravado_core.formatter import to_wire
from bravado_core.validate import validate_user_format, SwaggerValidationError


@pytest.fixture
def base64_spec():
    return {'type': 'string', 'format': 'base64'}


def test_success_validate(base64_spec, register_base64_format):
    validate_user_format(base64_spec, to_wire(base64_spec, b'darwin'))


def test_failure_validate_gets_wrapped(base64_spec, register_base64_format):
    with pytest.raises(SwaggerValidationError) as excinfo:
        validate_user_format(base64_spec, b'darwin')
    assert 'Incorrect padding' == str(excinfo.value)


@patch('bravado_core.formatter.warnings.warn')
def test_unregisterd_format_is_ignored(_, base64_spec):
    validate_user_format(base64_spec, b'darwin')
