"""
Delegate as much validation as possible out to jsonschema. This module serves
as the single point of entry for validations should we need to further
customize the behavior.
"""
from jsonschema.exceptions import ValidationError

from bravado_core.exception import wrap_exception, SwaggerMappingError
from bravado_core.formatter import get_formatter
from bravado_core.schema import SWAGGER_PRIMITIVES
from bravado_core.swagger20_validator import Swagger20Validator


def validate_schema_object(spec, value):
    obj_type = spec['type']

    if obj_type in SWAGGER_PRIMITIVES:
        validate_primitive(spec, value)

    elif obj_type == 'array':
        validate_array(spec, value)

    elif obj_type == 'object':
        validate_object(spec, value)

    elif obj_type == 'file':
        pass

    else:
        raise SwaggerMappingError('Unknown type {0} for value {1}'.format(
            obj_type, value))


@wrap_exception(ValidationError)
def validate_user_format(value, format):
    """value is supposed to be in the 'wire' format during this validation.
    Hence, it can be validated by running `to_python` on unmarshalled value.
    To enforce that the exception raised is ValidationError, decorator is used
    """
    formatter = get_formatter(format)
    if formatter:
        _, to_python, _ = formatter
        to_python(value)


def validate_primitive(spec, value):
    """
    :param spec: spec for a swagger primitive type in dict form
    :type value: int, string, float, long, etc
    """
    Swagger20Validator(spec).validate(value)
    validate_user_format(value, spec.get('format'))


def validate_array(spec, value):
    """
    :param spec: spec for an 'array' type in dict form
    :type value: list
    """
    Swagger20Validator(spec).validate(value)


def validate_object(spec, value):
    """
    :param spec: spec for an 'object' type in dict form
    :type value: dict
    """
    Swagger20Validator(spec).validate(value)
