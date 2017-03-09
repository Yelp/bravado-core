# -*- coding: utf-8 -*-
import pytest

from bravado_core.response import IncomingResponse


def test_required_attr_returned():

    class CompliantIncomingResponse(IncomingResponse):

        def __init__(self):
            self.status_code = 404
            self.reason = 'Object not found'
            self.text = 'Error - not found'
            self.headers = {}

    r = CompliantIncomingResponse()
    for attr in IncomingResponse.__required_attrs__:
        assert hasattr(r, attr)


def test_missing_required_attr_throws_NotImplementedError():

    class NonCompliantIncomingResponse(IncomingResponse):
        pass

    r = NonCompliantIncomingResponse()
    with pytest.raises(NotImplementedError) as excinfo:
        r.status_code
    assert 'forgot to implement' in str(excinfo.value)


def test_any_other_attr_throws_AttributeError():

    class UnrelatedReponse(IncomingResponse):
        pass

    r = UnrelatedReponse()
    with pytest.raises(AttributeError):
        r.foo


def test_str():

    class CompliantIncomingResponse(IncomingResponse):

        def __init__(self):
            self.status_code = 200
            self.reason = 'OK'

    r = CompliantIncomingResponse()
    assert str(r) == '200 OK'
