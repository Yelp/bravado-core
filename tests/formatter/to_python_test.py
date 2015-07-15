from datetime import date, datetime

import six

from bravado_core.formatter import to_python


def test_none():
    spec = {'type': 'string', 'format': 'date'}
    assert to_python(spec, None) is None


def test_no_format_returns_value():
    spec = {'type': 'string'}
    assert 'boo' == to_python(spec, 'boo')


def test_date():
    spec = {'type': 'string', 'format': 'date'}
    assert date(2015, 4, 1) == to_python(spec, '2015-04-01')


def test_datetime():
    spec = {'type': 'string', 'format': 'date-time'}
    result = to_python(spec, '2015-03-22T13:19:54')
    assert datetime(2015, 3, 22, 13, 19, 54) == result


def test_no_registered_format_returns_value_as_is():
    spec = {'type': 'foo', 'format': 'bar'}
    assert 'baz' == to_python(spec, 'baz')


def test_int64_long():
    spec = {'type': 'integer', 'format': 'int64'}
    if six.PY3:
        result = to_python(spec, 999)
        assert 999 == result
    else:
        result = to_python(spec, long(999))
        assert long(999) == result


def test_int64_int():
    spec = {'type': 'integer', 'format': 'int64'}
    result = to_python(spec, 999)
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
    result = to_python(spec, long(999))
    assert 999 == result
    assert isinstance(result, int)


def test_int32_int():
    spec = {'type': 'integer', 'format': 'int32'}
    result = to_python(spec, 999)
    assert 999 == result
    assert isinstance(result, int)


def test_float():
    spec = {'type': 'number', 'format': 'float'}
    result = to_python(spec, float(3.14))
    assert 3.14 == result
    assert isinstance(result, float)


def test_double():
    spec = {'type': 'number', 'format': 'double'}
    result = to_python(spec, float(3.14))
    assert 3.14 == result
    assert isinstance(result, float)


def test_byte():
    spec = {'type': 'string', 'format': 'byte'}
    result = to_python(spec, 'x')
    assert 'x' == result
    assert isinstance(result, str)
