# -*- coding: utf-8 -*-
import pytest
from jsonschema.exceptions import RefResolutionError

from bravado_core.spec import Spec


def test_none(minimal_swagger_spec):
    assert minimal_swagger_spec.deref(None) is None


def test_not_dict(minimal_swagger_spec):
    assert minimal_swagger_spec.deref('foo') == 'foo'


def test_is_dict_but_not_ref(minimal_swagger_spec):
    assert minimal_swagger_spec.deref({'foo': 'bar'}) == {'foo': 'bar'}


def test_ref(minimal_swagger_dict):
    foo_spec = {
        'type': 'object'
    }
    minimal_swagger_dict['definitions']['Foo'] = foo_spec
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert swagger_spec.deref({'$ref': '#/definitions/Foo'}) == foo_spec


def test_ref_not_found(minimal_swagger_dict):
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    with pytest.raises(RefResolutionError) as excinfo:
        swagger_spec.deref({'$ref': '#/definitions/Foo'})
    assert 'Unresolvable JSON pointer' in str(excinfo.value)
