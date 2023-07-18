# -*- coding: utf-8 -*-
def test_success(user):
    expected = "User(email=None, firstName=None, id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == repr(user)


def test_allOf(cat, cat_spec, cat_swagger_spec):
    expected = "Cat(category=None, id=None, name=None, neutered=None, photoUrls=None, tags=None)"  # noqa
    assert expected == repr(cat)


def test_unicode(user):
    user.firstName = 'Ümlaut'
    expected = "User(email=None, firstName='Ümlaut', id=None, lastName=None, password=None, phone=None, userStatus=None, username=None)"  # noqa
    assert expected == repr(user)
