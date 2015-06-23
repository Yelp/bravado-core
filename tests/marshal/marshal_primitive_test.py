# -*- coding: utf-8 -*-
import mock
import pytest
from bravado_core.exception import SwaggerMappingError

from bravado_core.marshal import marshal_primitive


def test_integer():
    integer_spec = {
        'type': 'integer'
    }
    assert 10 == marshal_primitive(integer_spec, 10)


def test_string():
    string_spec = {
        'type': 'string'
    }
    assert 'foo' == marshal_primitive(string_spec, 'foo')
    assert u'Ümlaut' == marshal_primitive(string_spec, u'Ümlaut')


@mock.patch('bravado_core.marshal.formatter.to_wire')
def test_uses_default_and_skips_formatting(mock_to_wire):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 10 == marshal_primitive(integer_spec, None)
    assert mock_to_wire.call_count == 0


@mock.patch('bravado_core.marshal.formatter.to_wire', return_value=99)
def test_skips_default(mock_to_wire):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 99 == marshal_primitive(integer_spec, 99)
    assert mock_to_wire.call_count == 1


def test_required():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 99 == marshal_primitive(integer_spec, 99)


def test_required_failure():
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_primitive(integer_spec, None)
    assert 'is a required value' in str(excinfo.value)
