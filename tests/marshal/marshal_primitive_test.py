# -*- coding: utf-8 -*-
import mock
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.marshal import marshal_primitive
from bravado_core.spec import Spec


def test_integer(minimal_swagger_spec):
    integer_spec = {'type': 'integer'}
    assert 10 == marshal_primitive(minimal_swagger_spec, integer_spec, 10)


def test_string(minimal_swagger_spec):
    string_spec = {'type': 'string'}
    assert 'foo' == marshal_primitive(minimal_swagger_spec, string_spec, 'foo')
    assert u'Ümlaut' == marshal_primitive(
        minimal_swagger_spec, string_spec, u'Ümlaut')


@mock.patch('bravado_core.marshal.formatter.to_wire')
def test_uses_default_and_skips_formatting(mock_to_wire, minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 10 == marshal_primitive(minimal_swagger_spec, integer_spec, None)
    assert mock_to_wire.call_count == 0


@mock.patch('bravado_core.marshal.formatter.to_wire', return_value=99)
def test_skips_default(mock_to_wire, minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'default': 10,
    }
    assert 99 == marshal_primitive(minimal_swagger_spec, integer_spec, 99)
    assert mock_to_wire.call_count == 1


def test_required(minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 99 == marshal_primitive(minimal_swagger_spec, integer_spec, 99)


def test_required_failure(minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_primitive(minimal_swagger_spec, integer_spec, None)
    assert 'is a required value' in str(excinfo.value)


def test_ref(minimal_swagger_dict):
    integer_spec = {
        'type': 'integer',
        'format': 'int32',
    }
    minimal_swagger_dict['definitions']['Integer'] = integer_spec
    ref_spec = {'$ref': '#/definitions/Integer'}
    swagger_spec = Spec(minimal_swagger_dict)
    assert 10 == marshal_primitive(swagger_spec, ref_spec, 10)

