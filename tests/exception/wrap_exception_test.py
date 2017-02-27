# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import wrap_exception


def test_exception_gets_correctly_wrapped():
    @wrap_exception(IOError)
    def raise_assertion_error():
        raise AssertionError('bla')

    with pytest.raises(IOError) as excinfo:
        raise_assertion_error()
    assert 'bla' == str(excinfo.value)


def test_return_value_when_no_exception():
    @wrap_exception(IOError)
    def do_not_raise_exception():
        return 'bla'

    assert 'bla' == do_not_raise_exception()
