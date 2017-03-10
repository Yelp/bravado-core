# -*- coding: utf-8 -*-
import functools

from mock import Mock

from bravado_core.spec import post_process_spec
from bravado_core.spec import Spec


def test_empty():
    swagger_spec = Spec({})
    callback = Mock()
    post_process_spec(swagger_spec, [callback])
    assert callback.call_count == 0


def test_single_key():
    spec_dict = {'definitions': {}}
    swagger_spec = Spec(spec_dict)
    callback = Mock()
    post_process_spec(swagger_spec, [callback])
    assert callback.call_count == 1
    callback.assert_called_once_with(spec_dict, 'definitions', ['definitions'])


def test_visits_refs_only_once():
    # bar should only be de-reffed once even though there are two refs to it
    spec_dict = {
        'ref_one': {'$ref': '#/bar'},
        'ref_two': {'$ref': '#/bar'},
        'bar': 'baz'
    }
    swagger_spec = Spec(spec_dict)

    # Yech! mock doesn't make this easy
    mutable = {'cnt': 0}

    def callback(container, key, path, mutable):
        # Bump the mutable counter every time bar is de-reffed
        if key == 'bar':
            mutable['cnt'] += 1

    post_process_spec(
        swagger_spec,
        [functools.partial(callback, mutable=mutable)])

    assert mutable['cnt'] == 1
