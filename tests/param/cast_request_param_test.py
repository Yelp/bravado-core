from mock import patch
import pytest

from bravado_core.param import cast_request_param
from bravado_core.param import string_to_boolean


class TestGeneralCast:

    @patch('bravado_core.param.log')
    def test_logs_cast_failure(self, mock_logger):
        cast_request_param('integer', 'gimme_int', 'not_int')
        assert mock_logger.warn.call_count == 1

    @patch('bravado_core.param.log')
    def test_cast_failures_return_untouched_value(self, mock_logger):
        initial_val = 'not_int'
        result_val = cast_request_param('integer', 'gimme_int', initial_val)
        assert result_val == initial_val

    def test_unknown_type_returns_untouched_value(self):
        assert 'abc123' == cast_request_param('unknown_type', 'blah', 'abc123')

    def test_none_returns_none(self):
        assert cast_request_param('integer', 'biz_id', None) is None

    def test_integer_cast(self):
        assert 34 == cast_request_param('integer', 'biz_id', '34')

    def test_number_cast(self):
        assert 2.34 == cast_request_param('number', 'score', '2.34')


class TestEmptyStringCast:

    def test_empty_string_becomes_none_for_type_integer(self):
        assert cast_request_param('integer', 'biz_id', '') is None

    def test_empty_string_becomes_none_for_type_number(self):
        assert cast_request_param('number', 'score', '') is None

    def test_empty_string_becomes_none_for_type_boolean(self):
        assert cast_request_param('boolean', 'is_open', '') is None

    def test_empty_string_stays_empty_string_for_type_string(self):
        assert '' == cast_request_param('string', 'address3', '')


class TestBooleanCast:

    def test_boolean_true_is_true_or_1(self):
        assert string_to_boolean('true')
        assert string_to_boolean('tRUe')
        assert string_to_boolean('1')

    def test_boolean_false_is_false_or_0(self):
        assert not string_to_boolean('false')
        assert not string_to_boolean('faLSe')
        assert not string_to_boolean('0')

    def test_boolean_cast_failure_raises_value_error(self):
        with pytest.raises(ValueError):
            string_to_boolean('PIZZA')
