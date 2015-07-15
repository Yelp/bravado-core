import base64
import pytest

import bravado_core.formatter
from bravado_core.formatter import register_format, to_wire
from bravado_core.validate import validate_user_format, ValidationError


@pytest.fixture
def base64_spec():
    return {'type': 'string', 'format': 'base64'}


@pytest.fixture
def register_base64_format():
    base64_format = bravado_core.formatter.SwaggerFormat(
        format='base64',
        to_wire=base64.b64encode,
        to_python=base64.b64decode,
        validate=base64.b64decode,
        description='Base64')
    register_format(base64_format)


def test_success_validate(base64_spec, register_base64_format):
    try:
        validate_user_format(base64_spec, to_wire(base64_spec, b'darwin'))
    finally:
        del bravado_core.formatter._formatters['base64']


def test_failure_validate_gets_wrapped(base64_spec, register_base64_format):
    try:
        validate_user_format(base64_spec, b'darwin')
    except ValidationError as e:
        assert 'Incorrect padding' == e.message
    finally:
        del bravado_core.formatter._formatters['base64']


def test_unregisterd_format_is_ignored(base64_spec):
    validate_user_format(base64_spec, b'darwin')
