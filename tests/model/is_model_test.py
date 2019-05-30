# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import is_model
from bravado_core.spec import Spec


@pytest.fixture
def model_spec():
    return {
        'type': 'object',
        'x-model': 'Address',
        'additionalProperties': True,
    }


@pytest.fixture
def object_spec():
    return {
        'type': 'object',
        'additionalProperties': True,
    }


def test_true(minimal_swagger_spec, model_spec):
    assert is_model(minimal_swagger_spec, model_spec)


def test_false(minimal_swagger_spec, object_spec):
    assert not is_model(minimal_swagger_spec, object_spec)


def test_ref(minimal_swagger_dict, model_spec):
    minimal_swagger_dict['definitions']['Foo'] = model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    assert is_model(swagger_spec, {'$ref': '#/definitions/Foo'})


def test_x_model_not_string(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Foo'] = {
        'x-model': {'x-vendor': 'Address'},
    }
    swagger_spec = Spec(minimal_swagger_dict)
    assert not is_model(swagger_spec, minimal_swagger_dict['definitions']['Foo'])
