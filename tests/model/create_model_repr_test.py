# -*- coding: utf-8 -*-
import pytest
import six


def test_success(user):
    expected = "User(email=None, firstName=None, id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == repr(user)


def test_allOf(cat, cat_spec, cat_swagger_spec):
    expected = "Cat(category=None, id=None, name=None, neutered=None, photoUrls=None, tags=None)"  # noqa
    assert expected == repr(cat)


@pytest.mark.skipif(six.PY3, reason="py2 has ascii default strings")
def test_unicode_py2(user):
    user.firstName = 'Ümlaut'
    expected = r"User(email=None, firstName='\xc3\x9cmlaut', id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == repr(user)


@pytest.mark.skipif(six.PY2, reason="py3 has unicode default strings")
def test_unicode_py3(user):
    user.firstName = 'Ümlaut'
    expected = "User(email=None, firstName='Ümlaut', id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == repr(user)
