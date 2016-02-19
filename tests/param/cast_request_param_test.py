from mock import patch

from bravado_core.param import cast_request_param


@patch('bravado_core.param.log')
def test_logs_cast_failure(mock_logger):
    cast_request_param('integer', 'gimme_int', 'not_int')
    assert mock_logger.warn.call_count == 1


def test_integer():
    assert 34 == cast_request_param('integer', 'biz_id', '34')


def test_empty_string_becomes_none_for_type_integer():
    assert cast_request_param('integer', 'biz_id', '') is None


def test_boolean():
    assert cast_request_param('boolean', 'is_open', 'true')
    assert cast_request_param('boolean', 'is_open', 'tRUe')
    assert not cast_request_param('boolean', 'is_open', 'false')
    assert not cast_request_param('boolean', 'is_open', 'faLSe')


@patch('bravado_core.param.log')
def test_boolean_returns_unchanged_string_for_non_bool_strings(mock_logger):
    assert cast_request_param('boolean', 'is_open', 'PIZZA') == 'PIZZA'
    assert not cast_request_param('boolean', 'is_open', 'PIZZA') is True
    assert not cast_request_param('boolean', 'is_open', 'PIZZA') is False


@patch('bravado_core.param.log')
def test_boolean_cast_failure_is_logged(mock_logger):
    cast_request_param('boolean', 'is_open', 'PIZZA')
    assert mock_logger.warn.call_count == 1


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
