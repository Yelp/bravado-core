# -*- coding: utf-8 -*-
from bravado_core.model import create_model_repr


def test_success(user, user_spec):
    expected = "User(email=None, firstName=None, id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == create_model_repr(user, user_spec)


def test_unicode(user, user_spec):
    user.firstName = 'Ümlaut'
    expected = r"User(email=None, firstName='\xc3\x9cmlaut', id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == create_model_repr(user, user_spec)
