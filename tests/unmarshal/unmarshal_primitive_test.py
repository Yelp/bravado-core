# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.unmarshal import unmarshal_primitive


def test_integer():
    integer_spec = {
        'type': 'integer'
    }
    assert 10 == unmarshal_primitive(integer_spec, 10)


def test_string():
    string_spec = {
        'type': 'string'
    }
    assert 'foo' == unmarshal_primitive(string_spec, 'foo')
    assert u'Ümlaut' == unmarshal_primitive(string_spec, u'Ümlaut')


def test_booean():
    boolean_spec = {
        'type': 'boolean'
    }
    result = unmarshal_primitive(boolean_spec, True)
    assert isinstance(result, bool)
    assert result

    result = unmarshal_primitive(boolean_spec, False)
    assert isinstance(result, bool)
    assert not result


def test_number():
    number_spec = {
        'type': 'number'
    }
    assert 3.1 == unmarshal_primitive(number_spec, 3.1)


def test_required_success():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 10 == unmarshal_primitive(integer_spec, 10)


def test_required_failure():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_primitive(integer_spec, None)
    assert 'is a required value' in str(excinfo.value)
