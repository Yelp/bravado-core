# -*- coding: utf-8 -*-
import pytest
import six

from bravado_core.model import create_model_repr


def test_success(user, user_spec):
    expected = "User(email=None, firstName=None, id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == create_model_repr(user, user_spec)


@pytest.mark.skipif(six.PY3, reason="py2 has ascii default strings")
def test_unicode_py2(user, user_spec):
    user.firstName = 'Ümlaut'
    expected = r"User(email=None, firstName='\xc3\x9cmlaut', id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == create_model_repr(user, user_spec)


@pytest.mark.skipif(six.PY2, reason="py3 has unicode default strings")
def test_unicode_py3(user, user_spec):
    user.firstName = 'Ümlaut'
    expected = "User(email=None, firstName='Ümlaut', id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == create_model_repr(user, user_spec)
