import base64

import bravado_core.formatter
from bravado_core.formatter import register_format, to_wire, to_python


def test_success():
    base64_format = bravado_core.formatter.SwaggerFormat(
        format='base64',
        to_wire=base64.b64encode,
        to_python=base64.b64decode,
        validate=lambda x: None,
        description='Base64')
    register_format(base64_format)
    try:
        spec = {
            'name': 'username',
            'type': 'string',
            'format': 'base64',
        }
        assert b'darwin' == to_python(spec, to_wire(spec, b'darwin'))
    finally:
        # I know, icky!
        del bravado_core.formatter._formatters['base64']
