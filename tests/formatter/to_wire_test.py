# -*- coding: utf-8 -*-
from datetime import date
from datetime import datetime

import pytest
import six
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
from pytz import timezone

from bravado_core.exception import SwaggerMappingError
from bravado_core.formatter import SwaggerFormat
from bravado_core.formatter import to_wire
from bravado_core.spec import Spec


if not six.PY2:
    long = int
    StringType = str
else:
    from types import StringType


def test_none(minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'date'}
    assert to_wire(minimal_swagger_spec, string_spec, None) is None


def test_no_format_returns_value(minimal_swagger_spec):
    string_spec = {'type': 'string'}
    assert 'boo' == to_wire(minimal_swagger_spec, string_spec, 'boo')


def test_date(minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'date'}
    assert '2015-04-01' == to_wire(
        minimal_swagger_spec, string_spec, date(2015, 4, 1),
    )


def test_naive_datetime(minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'date-time'}
    assert '2015-03-22T13:19:54+00:00' == to_wire(
        minimal_swagger_spec, string_spec, datetime(2015, 3, 22, 13, 19, 54),
    )


def test_localized_datetime(minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'date-time'}
    assert '2015-03-22T13:19:54-07:00' == to_wire(
        minimal_swagger_spec,
        string_spec,
        timezone('America/Los_Angeles').localize(datetime(2015, 3, 22, 13, 19, 54)),
    )


@patch('bravado_core.spec.warnings.warn')
def test_no_registered_format_returns_value_as_is(mock_warn, minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'bar'}
    assert 'baz' == to_wire(minimal_swagger_spec, string_spec, 'baz')
    assert mock_warn.call_count == 1


def test_int64_long(minimal_swagger_spec):
    integer_spec = {'type': 'integer', 'format': 'int64'}
    result = to_wire(minimal_swagger_spec, integer_spec, long(999))
    assert long(999) == result
    assert isinstance(result, long)


def test_int64_int(minimal_swagger_spec):
    integer_spec = {'type': 'integer', 'format': 'int64'}
    result = to_wire(minimal_swagger_spec, integer_spec, 999)
    assert long(999) == result
    assert isinstance(result, long)


def test_int32_long(minimal_swagger_spec):
    integer_spec = {'type': 'integer', 'format': 'int32'}
    result = to_wire(minimal_swagger_spec, integer_spec, long(999))
    assert 999 == result
    assert isinstance(result, int)


def test_int32_int(minimal_swagger_spec):
    integer_spec = {'type': 'integer', 'format': 'int32'}
    result = to_wire(minimal_swagger_spec, integer_spec, 999)
    assert 999 == result
    assert isinstance(result, int)


def test_float(minimal_swagger_spec):
    number_spec = {'type': 'number', 'format': 'float'}
    result = to_wire(minimal_swagger_spec, number_spec, 3.14)
    assert 3.14 == result
    assert isinstance(result, float)


def test_double(minimal_swagger_spec):
    number_spec = {'type': 'number', 'format': 'double'}
    result = to_wire(minimal_swagger_spec, number_spec, 3.14)
    assert 3.14 == result
    assert isinstance(result, float)


def test_byte_string(minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'byte'}
    result = to_wire(minimal_swagger_spec, string_spec, 'x')
    assert 'x' == result
    assert isinstance(result, str)


def test_byte_unicode(minimal_swagger_spec):
    string_spec = {'type': 'string', 'format': 'byte'}
    result = to_wire(minimal_swagger_spec, string_spec, u'x')
    assert 'x' == result
    assert isinstance(result, str)


def test_byte_base64(minimal_swagger_dict):
    swagger_spec = Spec.from_dict(
        minimal_swagger_dict, config={'use_base64_for_byte_format': True},
    )
    schema = {'type': 'string', 'format': 'byte'}
    result = to_wire(swagger_spec, schema, b'abc\xff')
    assert 'YWJj/w==' == result
    assert isinstance(result, str)


def test_ref(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Int32'] = {
        'type': 'integer', 'format': 'int32',
    }
    int_ref_spec = {'$ref': '#/definitions/Int32'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    result = to_wire(swagger_spec, int_ref_spec, 999)
    assert 999 == result
    assert isinstance(result, int)


def test_override(minimal_swagger_dict):
    class Byte(object):
        def __init__(self, x):
            self.x = x

        def __str__(self):
            return str(self.x)

        def __repr__(self):
            return '%s(%r)' % (self.__class__, self.x)

    byteformat = SwaggerFormat(
        format='byte',
        to_wire=lambda x: str(x),
        to_python=lambda x: Byte(x),
        validate=lambda x: isinstance(x, str),
        description=None,
    )

    number_spec = {'type': 'string', 'format': 'byte'}

    swagger_spec = Spec.from_dict(minimal_swagger_dict, config={'formats': [byteformat]})
    result = to_wire(swagger_spec, number_spec, '8bits')

    assert '8bits' == result
    assert isinstance(result, str)
    assert type(result) is StringType


def test_to_wire_with_wrong_format(minimal_swagger_spec):
    with pytest.raises(SwaggerMappingError, match="Error while marshalling value=random-test to type=string/date."):
        to_wire(minimal_swagger_spec, {'type': 'string', 'format': 'date'}, 'random-test')
