from mock import patch

from bravado_core.param import cast_request_param


def test_integer():
    assert 34 == cast_request_param('integer', 'biz_id', '34')


def test_boolean():
    assert cast_request_param('boolean', 'is_open', 1)
    assert not cast_request_param('boolean', 'is_open', 0)


def test_number():
    assert 2.34 == cast_request_param('number', 'score', '2.34')


def test_unknown_type_returns_untouched_value():
    assert 'abc123' == cast_request_param('unknown_type', 'blah', 'abc123')


def test_none_returns_none():
    assert cast_request_param('integer', 'biz_id', None) is None


@patch('bravado_core.param.log.warn')
def test_cast_failure_returns_untouched_value(_):
    assert 'i_cant_be_casted_to_an_integer' == cast_request_param(
        'integer', 'biz_id', 'i_cant_be_casted_to_an_integer')
