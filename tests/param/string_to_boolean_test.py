# -*- coding: utf-8 -*-
import pytest

from bravado_core.param import string_to_boolean


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
