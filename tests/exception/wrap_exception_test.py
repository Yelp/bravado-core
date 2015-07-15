import pytest

from bravado_core.exception import wrap_exception


def test_exception_gets_correctly_wrapped():
    @wrap_exception(IOError)
    def raise_assertion_error():
        raise AssertionError('bla')

    with pytest.raises(IOError) as e:
        raise_assertion_error()
        assert 'bla' == e.message
