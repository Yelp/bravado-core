# -*- coding: utf-8 -*-
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from bravado_core.param import cast_request_param


@patch('bravado_core.param.log')
def test_logs_cast_failure(mock_logger):
    cast_request_param('integer', 'gimme_int', 'not_int')
    assert mock_logger.warning.call_count == 1


@patch('bravado_core.param.log')
def test_cast_failures_return_untouched_value(mock_logger):
    initial_val = 'not_int'
    result_val = cast_request_param('integer', 'gimme_int', initial_val)
    assert result_val == initial_val


@patch('bravado_core.param.log')
def test_type_error_returns_untouched_value_and_logs(mock_logger):
    initial_val = ['123', '456']
    result_val = cast_request_param('integer', 'gimme_int', initial_val)
    assert result_val == initial_val
    assert result_val is initial_val
    assert mock_logger.warning.call_count == 1


def test_unknown_type_returns_untouched_value():
    assert 'abc123' == cast_request_param('unknown_type', 'blah', 'abc123')


def test_none_returns_none():
    assert cast_request_param('integer', 'biz_id', None) is None


def test_integer_cast():
    assert 34 == cast_request_param('integer', 'biz_id', '34')


def test_number_cast():
    assert 2.34 == cast_request_param('number', 'score', '2.34')


def test_empty_string_becomes_none_for_type_integer():
    assert cast_request_param('integer', 'biz_id', '') is None


def test_empty_string_becomes_none_for_type_number():
    assert cast_request_param('number', 'score', '') is None


def test_empty_string_becomes_none_for_type_boolean():
    assert cast_request_param('boolean', 'is_open', '') is None


def test_empty_string_stays_empty_string_for_type_string():
    assert '' == cast_request_param('string', 'address3', '')
