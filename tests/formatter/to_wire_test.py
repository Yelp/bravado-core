from datetime import datetime, date

import six
from mock import patch

from bravado_core.formatter import to_wire


def test_none():
    spec = {'type': 'string', 'format': 'date'}
    assert to_wire(spec, None) is None


def test_no_format_returns_value():
    spec = {'type': 'string'}
    assert 'boo' == to_wire(spec, 'boo')


def test_date():
    assert '2015-04-01' == to_wire({'format': 'date'}, date(2015, 4, 1))


def test_datetime():
    result = to_wire({'format': 'date-time'}, datetime(2015, 3, 22, 13, 19, 54))
    assert '2015-03-22T13:19:54' == result


@patch('bravado_core.formatter.warnings.warn')
def test_no_registered_format_returns_value_as_is(_):
    spec = {'type': 'foo', 'format': 'bar'}
    assert 'baz' == to_wire(spec, 'baz')


@patch('bravado_core.formatter.warnings.warn')
def test_no_registered_format_throws_warning(mock_warn):
    to_wire({'type': 'foo', 'format': 'bar'}, 'baz')
    mock_warn.assert_called_once()


def test_int64_long():
    spec = {'type': 'integer', 'format': 'int64'}
    if six.PY3:
        result = to_wire(spec, 999)
        assert 999 == result
        assert isinstance(result, int)
    else:
        result = to_wire(spec, long(999))
        assert long(999) == result
        assert isinstance(result, long)


def test_int64_int():
    spec = {'type': 'integer', 'format': 'int64'}
    result = to_wire(spec, 999)
    if six.PY3:
        assert 999 == result
        assert isinstance(result, int)
    else:
        assert long(999) == result
        assert isinstance(result, long)


def test_int32_long():
    if six.PY3:  # test irrelevant in py3
        return
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_wire(spec, long(999))
    assert 999 == result
    assert isinstance(result, int)


def test_int32_int():
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_wire(spec, 999)
    assert 999 == result
    assert isinstance(result, int)


def test_float():
    spec = {'type': 'number', 'format': 'float'}
    result = to_wire(spec, 3.14)
    assert 3.14 == result
    assert isinstance(result, float)


def test_double():
    spec = {'type': 'number', 'format': 'double'}
    result = to_wire(spec, 3.14)
    assert 3.14 == result
    assert isinstance(result, float)


def test_byte_string():
    spec = {'type': 'string', 'format': 'byte'}
    result = to_wire(spec, 'x')
    assert 'x' == result
    assert isinstance(result, str)


def test_byte_unicode():
    spec = {'type': 'string', 'format': 'byte'}
    result = to_wire(spec, u'x')
    assert 'x' == result
    assert isinstance(result, str)
