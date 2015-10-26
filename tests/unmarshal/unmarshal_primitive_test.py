# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_primitive


def test_integer(minimal_swagger_spec):
    integer_spec = {'type': 'integer'}
    assert 10 == unmarshal_primitive(minimal_swagger_spec, integer_spec, 10)


def test_string(minimal_swagger_spec):
    string_spec = {'type': 'string'}
    assert 'foo' == unmarshal_primitive(
        minimal_swagger_spec, string_spec, 'foo')
    assert u'Ümlaut' == unmarshal_primitive(
        minimal_swagger_spec, string_spec, u'Ümlaut')


def test_booean(minimal_swagger_spec):
    boolean_spec = {'type': 'boolean'}
    result = unmarshal_primitive(minimal_swagger_spec, boolean_spec, True)
    assert isinstance(result, bool)
    assert result

    result = unmarshal_primitive(minimal_swagger_spec, boolean_spec, False)
    assert isinstance(result, bool)
    assert not result


def test_number(minimal_swagger_spec):
    number_spec = {'type': 'number'}
    assert 3.1 == unmarshal_primitive(minimal_swagger_spec, number_spec, 3.1)


def test_required_success(minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    assert 10 == unmarshal_primitive(minimal_swagger_spec, integer_spec, 10)


def test_required_failure(minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'required': True,
    }
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_primitive(minimal_swagger_spec, integer_spec, None)
    assert 'is a required value' in str(excinfo.value)


def test_ref(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['SpecialInteger'] = {'type': 'integer'}
    special_integer_spec = {'$ref': '#/definitions/SpecialInteger'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert 10 == unmarshal_primitive(swagger_spec, special_integer_spec, 10)
