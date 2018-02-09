# -*- coding: utf-8 -*-
from bravado_core.response import IncomingResponse
from bravado_core.response import unmarshal_response


class FakeJsonResponse(IncomingResponse):

    def __init__(
        self,
        text,
        status_code=200,
        reason='OK',
        headers=None
    ):
        self.text = text
        self.status_code = 200
        self.reason = 'OK'
        self.headers = {'content-type': 'application/json'}
        if headers:
            self.headers = headers

    def json(self, **kwargs):
        return self.text


def test_small_objects(benchmark, petstore_op, small_pets):
    resp = FakeJsonResponse(small_pets)
    benchmark(unmarshal_response, resp, petstore_op)


def test_large_objects(benchmark, petstore_op, large_pets):
    resp = FakeJsonResponse(large_pets)
    benchmark(unmarshal_response, resp, petstore_op)
