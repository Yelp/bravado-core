from mock import patch
import pytest

from bravado_core.param import cast_request_param
from bravado_core.param import string_to_boolean


@patch('bravado_core.param.log')
def test_logs_cast_failure(mock_logger):
    cast_request_param('integer', 'gimme_int', 'not_int')
    assert mock_logger.warn.call_count == 1


@patch('bravado_core.param.log')
def test_cast_failures_return_unchanged_value(unused_logger):
    initial_val = 'not_int'
    result_val = cast_request_param('integer', 'gimme_int', initial_val)
    assert result_val == initial_val


def test_integer():
    assert 34 == cast_request_param('integer', 'biz_id', '34')


def test_empty_string_becomes_none_for_type_integer():
    assert cast_request_param('integer', 'biz_id', '') is None


def test_boolean_true_is_true_or_1():
    assert string_to_boolean('true')
    assert string_to_boolean('tRUe')
    assert string_to_boolean('1')


def test_boolean_false_is_false_or_0():
    assert not string_to_boolean('false')
    assert not string_to_boolean('faLSe')
    assert not string_to_boolean('0')


def test_boolean_cast_failure_raises_value_error():
    with pytest.raises(ValueError):
        string_to_boolean('PIZZA')


def test_empty_string_becomes_none_for_type_boolean():
    assert cast_request_param('boolean', 'is_open', '') is None


def test_number():
    assert 2.34 == cast_request_param('number', 'score', '2.34')


def test_empty_string_becomes_none_for_type_number():
    assert cast_request_param('number', 'score', '') is None


def test_unknown_type_returns_untouched_value():
    assert 'abc123' == cast_request_param('unknown_type', 'blah', 'abc123')


def test_none_returns_none():
    assert cast_request_param('integer', 'biz_id', None) is None


@patch('bravado_core.param.log.warn')
def test_cast_failure_returns_untouched_value(_):
    assert 'i_cant_be_casted_to_an_integer' == cast_request_param(
        'integer', 'biz_id', 'i_cant_be_casted_to_an_integer')
