# -*- coding: utf-8 -*-
import datetime

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
        minimal_swagger_spec, string_spec, u'Ümlaut',
    )


@pytest.mark.parametrize(
    'value, expected_value',
    [
        (None, '2019-05-23'),
        (datetime.date(2019, 5, 24), '2019-05-24'),
    ],
)
def test_skips_default(minimal_swagger_spec, value, expected_value):
    date_spec = {
        'type': 'string',
        'format': 'date',
        'default': '2019-05-23',
    }
    assert marshal_primitive(
        minimal_swagger_spec, date_spec, value,
    ) == expected_value


def test_ref(minimal_swagger_dict):
    integer_spec = {
        'type': 'integer',
        'format': 'int32',
    }
    minimal_swagger_dict['definitions']['Integer'] = integer_spec
    ref_spec = {'$ref': '#/definitions/Integer'}
    swagger_spec = Spec(minimal_swagger_dict)
    assert 10 == marshal_primitive(swagger_spec, ref_spec, 10)


def test_nullable_primitive(empty_swagger_spec):
    string_spec = {
        'type': 'string',
        'x-nullable': True,
    }
    assert marshal_primitive(empty_swagger_spec, string_spec, None) is None


def test_not_nullable_primitive(empty_swagger_spec):
    string_spec = {
        'type': 'string',
    }
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_primitive(empty_swagger_spec, string_spec, None)
    assert 'is a required value' in str(excinfo.value)
