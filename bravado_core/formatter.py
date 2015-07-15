"""
Support for the 'format' key in the swagger spec as outlined in
https://github.com/swagger-api/swagger-spec/blob/master/versions/2.0.md#dataTypeFormat
"""

import collections

import six
import dateutil.parser

from bravado_core import schema

if six.PY3:
    long = int


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
    """
    Register a swagger_format to a global _formatters cache.

    :type format: string
    :param to_wire: single argument callable that converts a value to wire
        format
    :param to_python: single argument callable that converts a value to python
    :param description: useful description
    """
    global _formatters
    _formatters[swagger_format.format] = swagger_format


def get_format(format):
    return _formatters.get(format)


# validate should check the correctness of `wire` value
SwaggerFormat = collections.namedtuple(
    'SwaggerFormat', 'format to_python to_wire validate description')


_formatters = {
    'byte': SwaggerFormat(
        format='byte',
        to_wire=lambda b: b if isinstance(b, str) else str(b),
        to_python=(
            lambda s: s if isinstance(s, str) else str(s)),
        validate=lambda x: None,  # jsonschema validates string
        description='Converts [wire]string:byte <=> python byte'),
    'date': SwaggerFormat(
        format='date',
        to_wire=lambda d: d.isoformat(),
        to_python=lambda d: dateutil.parser.parse(d).date(),
        validate=lambda x: None,  # jsonschema validates date
        description='Converts [wire]string:date <=> python datetime.date'),
    # Python has no double. float is C's double in CPython
    'double': SwaggerFormat(
        format='double',
        to_wire=lambda d: d if isinstance(d, float) else float(d),
        to_python=lambda d: d if isinstance(d, float) else float(d),
        validate=lambda x: None,  # jsonschema validates number
        description='Converts [wire]number:double <=> python float'),
    'date-time': SwaggerFormat(
        format='date-time',
        to_wire=lambda dt: dt.isoformat(),
        to_python=lambda dt: dateutil.parser.parse(dt),
        validate=lambda x: None,  # jsonschema validates date-time
        description=(
            'Converts string:date-time <=> python datetime.datetime')),
    'float': SwaggerFormat(
        format='float',
        to_wire=lambda f: f if isinstance(f, float) else float(f),
        to_python=lambda f: f if isinstance(f, float) else float(f),
        validate=lambda x: None,  # jsonschema validates number
        description='Converts [wire]number:float <=> python float'),
    'int32': SwaggerFormat(
        format='int32',
        to_wire=lambda i: i if isinstance(i, int) else int(i),
        to_python=lambda i: i if isinstance(i, int) else int(i),
        validate=lambda x: None,  # jsonschema validates integer
        description='Converts [wire]integer:int32 <=> python int'),
    'int64': SwaggerFormat(
        format='int64',
        to_wire=lambda i: i if isinstance(i, long) else long(i),
        to_python=lambda i: i if isinstance(i, long) else long(i),
        validate=lambda x: None,  # jsonschema validates integer
        description='Converts [wire]integer:int64 <=> python long'),
    }
