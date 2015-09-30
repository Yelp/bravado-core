"""
Support for the 'format' key in the swagger spec as outlined in
https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#dataTypeFormat
"""
import functools
import warnings
from collections import namedtuple
from jsonschema import FormatChecker

import six
import dateutil.parser

from bravado_core import schema
from bravado_core.exception import SwaggerValidationError

if six.PY3:
    long = int

NO_OP = lambda x: None


def to_wire(spec, value):
    """Converts a python primitive or object to a reasonable wire
    representation given the 'format' in the given spec.

    :param spec: spec for a primitive type as a dict
    :type value: int, long, float, boolean, string, unicode, etc
    :rtype: int, long, float, boolean, string, unicode, etc
    """
    if value is None or not schema.has_format(spec):
        return value
    formatter = get_format(schema.get_format(spec))
    return formatter.to_wire(value) if formatter else value


def to_python(spec, value):
    """Converts a value in wire format to its python representation given
    the 'format' in the given spec.

    :param spec: spec for a primitive type as a dict
    :type value: int, long, float, boolean, string, unicode, etc
    :rtype: int, long, float, boolean, string, object, etc
    """
    if value is None or not schema.has_format(spec):
        return value
    formatter = get_format(schema.get_format(spec))
    return formatter.to_python(value) if formatter else value


def register_format(swagger_format):
    """Register a user-defined format with bravado-core.

    :type swagger_format: :class:`SwaggerFormat`
    """
    global _formatters
    _formatters[swagger_format.format] = swagger_format

    # Need to maintain a separate list of UDFs for jsonschema validation
    global _user_defined_formats
    _user_defined_formats.append(swagger_format)


def unregister_format(swagger_format):
    """Unregister an existing user-defined format.

    :type swagger_format: :class:`SwaggerFormat`
    """
    global _formatters
    del _formatters[swagger_format.format]

    global _user_defined_formats
    _user_defined_formats.remove(swagger_format)

    # Invalidate so it is rebuilt
    global _format_checker
    _format_checker = None


def get_format(format):
    """Get registered formatter mapped to given format.

    :param format: Format name like int32, base64, etc.
    :type format: str
    :rtype: :class:`SwaggerFormat` or None
    """
    formatter = _formatters.get(format)
    if format and not formatter:
        warnings.warn(
            "%s format is not registered with bravado-core!" % format, Warning)
    return formatter


# validate should check the correctness of `wire` value
class SwaggerFormat(namedtuple('SwaggerFormat',
                    'format to_python to_wire validate description')):
    """It defines a user defined format which can be registered with
    bravado-core and then can be used for marshalling/unmarshalling data
    as per the user defined methods. User can also add `validate` method
    which is invoked during bravado-core's validation flow.

    :param format: Name for the user format.
    :param to_python: function to unmarshal a value of this format.
                      Eg. lambda val_str: base64.b64decode(val_str)
    :param to_wire: function to marshal a value of this format
                    Eg. lambda val_py: base64.b64encode(val_py)
    :param validate: function to validate the marshalled value. Raises
                     :class:`bravado_core.exception.SwaggerValidationError`
                     if value does not conform to the format.
    :param description: Short description of the format and conversion logic.
    """


def return_true_wrapper(validate_func):
    """Decorator for the SwaggerFormat.validate function to always return True.

    The contract for `SwaggerFormat.validate` is to raise an exception
    when validation fails. However, the contract for jsonschema's
    validate function is to raise an exception or return True. This wrapper
    bolts-on the `return True` part.

    :param validate_func: SwaggerFormat.validate function
    :return: wrapped callable
    """
    @functools.wraps(validate_func)
    def wrapper(validatable_primitive):
        validate_func(validatable_primitive)
        return True

    return wrapper


# jsonschema.FormatChecker
_format_checker = None


# List of newly registered user-defined SwaggerFormats
_user_defined_formats = []


def get_format_checker():
    """
    Build and cache a :class:`jsonschema.FormatChecker` for validating
    user-defined Swagger formats.

    :rtype: :class:`jsonschema.FormatChecker`
    """
    global _format_checker
    if _format_checker is None:
        _format_checker = FormatChecker()
        for swagger_format in _user_defined_formats:
            validate = return_true_wrapper(swagger_format.validate)
            # `checks` is a function decorator, hence the unusual registration
            # mechanism.
            _format_checker.checks(
                swagger_format.format,
                raises=(SwaggerValidationError,))(validate)
    return _format_checker


_formatters = {
    'byte': SwaggerFormat(
        format='byte',
        to_wire=lambda b: b if isinstance(b, str) else str(b),
        to_python=(
            lambda s: s if isinstance(s, str) else str(s)),
        validate=NO_OP,  # jsonschema validates string
        description='Converts [wire]string:byte <=> python byte'),
    'date': SwaggerFormat(
        format='date',
        to_wire=lambda d: d.isoformat(),
        to_python=lambda d: dateutil.parser.parse(d).date(),
        validate=NO_OP,  # jsonschema validates date
        description='Converts [wire]string:date <=> python datetime.date'),
    # Python has no double. float is C's double in CPython
    'double': SwaggerFormat(
        format='double',
        to_wire=lambda d: d if isinstance(d, float) else float(d),
        to_python=lambda d: d if isinstance(d, float) else float(d),
        validate=NO_OP,  # jsonschema validates number
        description='Converts [wire]number:double <=> python float'),
    'date-time': SwaggerFormat(
        format='date-time',
        to_wire=lambda dt: dt.isoformat(),
        to_python=lambda dt: dateutil.parser.parse(dt),
        validate=NO_OP,  # jsonschema validates date-time
        description=(
            'Converts string:date-time <=> python datetime.datetime')),
    'float': SwaggerFormat(
        format='float',
        to_wire=lambda f: f if isinstance(f, float) else float(f),
        to_python=lambda f: f if isinstance(f, float) else float(f),
        validate=NO_OP,  # jsonschema validates number
        description='Converts [wire]number:float <=> python float'),
    'int32': SwaggerFormat(
        format='int32',
        to_wire=lambda i: i if isinstance(i, int) else int(i),
        to_python=lambda i: i if isinstance(i, int) else int(i),
        validate=NO_OP,  # jsonschema validates integer
        description='Converts [wire]integer:int32 <=> python int'),
    'int64': SwaggerFormat(
        format='int64',
        to_wire=lambda i: i if isinstance(i, long) else long(i),
        to_python=lambda i: i if isinstance(i, long) else long(i),
        validate=NO_OP,  # jsonschema validates integer
        description='Converts [wire]integer:int64 <=> python long'),
    }
