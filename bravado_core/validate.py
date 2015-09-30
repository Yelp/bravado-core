"""
Delegate as much validation as possible out to jsonschema. This module serves
as the single point of entry for validations should we need to further
customize the behavior.
"""

from bravado_core.exception import SwaggerMappingError
from bravado_core.schema import SWAGGER_PRIMITIVES
from bravado_core.formatter import get_format_checker
from bravado_core.swagger20_validator import Swagger20Validator


def validate_schema_object(spec, value):
    """
    :raises ValidationError: when validation error found by jsonschema.
    :raises SwaggerMappingError: when `type` of value is not as per spec v2.0
    :raises SwaggerValidationError: when user format's `validate` raises error.
    """
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


def validate_primitive(spec, value):
    """
    :param spec: spec for a swagger primitive type in dict form
    :type value: int, string, float, long, etc
    """
    Swagger20Validator(
        spec, format_checker=get_format_checker()).validate(value)


def validate_array(spec, value):
    """
    :param spec: spec for an 'array' type in dict form
    :type value: list
    """
    Swagger20Validator(
        spec, format_checker=get_format_checker()).validate(value)


def validate_object(spec, value):
    """
    :param spec: spec for an 'object' type in dict form
    :type value: dict
    """
    Swagger20Validator(
        spec, format_checker=get_format_checker()).validate(value)
