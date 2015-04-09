import base64

import bravado.core.formatter
from bravado.core.formatter import register_format, to_wire, to_python


def test_success():
    register_format('base64', base64.b64encode, base64.b64decode, "Base64")
    try:
        spec = {
            'name': 'username',
            'type': 'string',
            'format': 'base64',
        }
        assert 'darwin' == to_python(spec, to_wire(spec, 'darwin'))
    finally:
        # I know, icky!
        del bravado.core.formatter._formatters['base64']
