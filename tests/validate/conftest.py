from contextlib import contextmanager

from bravado_core.exception import SwaggerValidationError
from bravado_core.formatter import SwaggerFormat
from bravado_core.formatter import register_format
from bravado_core.formatter import unregister_format


def validate_email_address(email_address):
    if '@' not in email_address:
        raise SwaggerValidationError('dude, you need an @')


email_address_format = SwaggerFormat(
    format='email_address',
    to_wire=lambda x: x,
    to_python=lambda x: x,
    validate=validate_email_address,
    description='blah')


@contextmanager
def registered_format(swagger_format):
    register_format(swagger_format)
    try:
        yield
    finally:
        unregister_format(swagger_format)
