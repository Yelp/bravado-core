# -*- coding: utf-8 -*-
from bravado_core.schema import has_format
from bravado_core.spec import Spec


def test_true(minimal_swagger_spec):
    int_spec = {'type': 'integer', 'format': 'int32'}
    assert has_format(minimal_swagger_spec, int_spec)


def test_false(minimal_swagger_spec):
    int_spec = {'type': 'integer'}
    assert not has_format(minimal_swagger_spec, int_spec)


def test_ref_true(minimal_swagger_dict):
    int32_spec = {'type': 'integer', 'format': 'int32'}
    minimal_swagger_dict['definitions']['Int32'] = int32_spec
    ref_spec = {'$ref': '#/definitions/Int32'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert has_format(swagger_spec, ref_spec)


def test_ref_false(minimal_swagger_dict):
    int_spec = {'type': 'integer'}
    minimal_swagger_dict['definitions']['Int'] = int_spec
    ref_spec = {'$ref': '#/definitions/Int'}
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert not has_format(swagger_spec, ref_spec)
