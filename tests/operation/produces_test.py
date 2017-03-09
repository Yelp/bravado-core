# -*- coding: utf-8 -*-
from bravado_core.operation import Operation
from bravado_core.spec import Spec


def test_returns_produces_from_op(minimal_swagger_dict):
    op_spec = {'produces': ['application/json']}
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert ['application/json'] == op.produces


def test_returns_produces_from_swagger_spec_when_not_present_on_op(
        minimal_swagger_dict):
    op_spec = {
        # 'produces' left out intentionally
    }
    minimal_swagger_dict['produces'] = ['application/json']
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert ['application/json'] == op.produces


def test_produces_on_op_overrides_produces_from_swagger_spec(
        minimal_swagger_dict):
    op_spec = {'produces': ['application/xml']}
    minimal_swagger_dict['produces'] = ['application/json']
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert ['application/xml'] == op.produces


def test_produces_not_present_on_swagger_spec_returns_empty_array(
        minimal_swagger_dict):
    # The point being, None should never be returned
    op_spec = {
        # 'produces' left out intentionally
    }
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    op = Operation(minimal_swagger_spec, '/foo', 'get', op_spec)
    assert [] == op.produces
