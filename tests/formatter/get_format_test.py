
from bravado_core.formatter import _formatters, get_format


def test_returns_format_if_present():
    assert get_format('int32') == _formatters['int32']


def test_returns_none_if_format_not_present():
    assert get_format('foo') is None
