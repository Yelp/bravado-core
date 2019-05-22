# -*- coding: utf-8 -*-
import datetime

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
        minimal_swagger_spec, string_spec, 'foo',
    )
    assert u'Ümlaut' == unmarshal_primitive(
        minimal_swagger_spec, string_spec, u'Ümlaut',
    )


def test_boolean(minimal_swagger_spec):
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


def test_datetime_string(minimal_swagger_spec):
    from datetime import datetime
    date_spec = {
        'type': 'string',
        'format': 'date-time',
    }
    # the validator requires a time zone, but that's a pain to scaffold:
    # this just tests that naive date parsing happens as expected
    input_date = "2016-06-07T20:59:00.480"
    expected_date = datetime(2016, 6, 7, 20, 59, 0, 480000)
    assert expected_date == unmarshal_primitive(
        minimal_swagger_spec,
        date_spec, input_date,
    )


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


def test_default(minimal_swagger_spec):
    integer_spec = {
        'type': 'integer',
        'default': 42,
    }

    assert 42 == unmarshal_primitive(minimal_swagger_spec, integer_spec, None)


def test_default_with_format(minimal_swagger_spec):
    integer_spec = {
        'type': 'string',
        'format': 'date',
        'default': '2019-05-22',
    }

    assert datetime.date(2019, 5, 22) == unmarshal_primitive(minimal_swagger_spec, integer_spec, None)


def test_ref(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['SpecialInteger'] = {'type': 'integer'}
    special_integer_spec = {'$ref': '#/definitions/SpecialInteger'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert 10 == unmarshal_primitive(swagger_spec, special_integer_spec, 10)


@pytest.mark.parametrize(
    ['nullable', 'value'],
    [(False, 'x'), (True, 'x'), (True, None)],
)
def test_nullable(minimal_swagger_spec, value, nullable):
    string_spec = {
        'type': 'string',
        'x-nullable': nullable,
    }
    result = unmarshal_primitive(minimal_swagger_spec, string_spec, value)
    assert value == result
