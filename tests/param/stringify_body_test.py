# -*- coding: utf-8 -*-
import datetime
import json

from bravado_core.param import stringify_body


def test_stringify_body_converts_dict_to_str():
    body = {'foo': 'bar', 'bar': 42}
    body_str = stringify_body(body)
    assert body == json.loads(body_str)


def test_stringify_body_ignores_data_if_already_str():
    assert 'foo' == stringify_body('foo')


def test_stringify_body_handles_date():
    now = datetime.date.today()
    now_str = '{"now": "' + now.isoformat() + '"}'
    body = {'now': now}
    body_str = stringify_body(body)
    assert body_str == now_str


def test_stringify_body_handles_datetime():
    now = datetime.datetime.utcnow()
    now_str = '{"now": "' + now.isoformat() + '"}'
    body = {'now': now}
    body_str = stringify_body(body)
    assert body_str == now_str
