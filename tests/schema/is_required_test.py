# -*- coding: utf-8 -*-
import pytest

from bravado_core.schema import is_required
from bravado_core.spec import Spec


@pytest.fixture
def required_true():
    return {'type': 'integer', 'required': True}


@pytest.fixture
def required_false():
    return {'type': 'integer', 'required': False}


def test_true(minimal_swagger_spec, required_true):
    assert is_required(minimal_swagger_spec, required_true)


def test_false(minimal_swagger_spec, required_false):
    assert not is_required(minimal_swagger_spec, required_false)


def test_defaults_to_false(minimal_swagger_spec):
    assert not is_required(minimal_swagger_spec, {'type': 'integer'})


def test_ref_true(minimal_swagger_dict, required_true):
    minimal_swagger_dict['definitions']['Foo'] = required_true
    swagger_spec = Spec(minimal_swagger_dict)
    assert is_required(swagger_spec, {'$ref': '#/definitions/Foo'})


def test_ref_false(minimal_swagger_dict, required_false):
    minimal_swagger_dict['definitions']['Foo'] = required_false
    swagger_spec = Spec(minimal_swagger_dict)
    assert not is_required(swagger_spec, {'$ref': '#/definitions/Foo'})


def test_ref_default_to_false(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Foo'] = {'type': 'integer'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert not is_required(swagger_spec, {'$ref': '#/definitions/Foo'})
