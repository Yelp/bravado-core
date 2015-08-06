import pytest

from bravado_core.response import IncomingResponse


def test_required_attr_returned():

    class CompliantIncomingResponse(IncomingResponse):

        def __init__(self):
            self.status_code = 99

    r = CompliantIncomingResponse()
    assert 99 == r.status_code


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
