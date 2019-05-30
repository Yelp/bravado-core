# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import is_object
from bravado_core.spec import Spec


# deref = swagger_spec.deref
# default_type = 'object' if not no_default_type and swagger_spec.config['default_type_to_object'] else None
# object_type = deref(object_spec.get('type', default_type))
# return object_type == 'object' or (object_type is None and 'allOf' in object_spec)


@pytest.mark.parametrize(
    'object_spec, config_override',
    [
        [{'type': 'object'}, {}],
        [{}, {'default_type_to_object': True}],
        [{'allOf': []}, {}],
    ],
)
def test_true(minimal_swagger_spec, object_spec, config_override):
    minimal_swagger_spec.config.update(config_override)
    assert is_object(minimal_swagger_spec, object_spec)


@pytest.mark.parametrize(
    'object_spec, config_override',
    [
        [{'type': 'string'}, {}],
        [{'type': 'string', 'allOf': []}, {}],
    ],
)
def test_false(minimal_swagger_spec, object_spec, config_override):
    minimal_swagger_spec.config.update(config_override)
    assert not is_object(
        minimal_swagger_spec, object_spec,
    )


def test_ref(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Foo'] = {'type': 'object'}
    minimal_swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert is_object(minimal_swagger_spec, {'$ref': '#/definitions/Foo'})

#
# def test_x_model_not_string(minimal_swagger_dict):
#     minimal_swagger_dict['definitions']['Foo'] = {
#         'x-model': {'x-vendor': 'Address'},
#     }
#     swagger_spec = Spec(minimal_swagger_dict)
#     assert not is_model(swagger_spec, minimal_swagger_dict['definitions']['Foo'])
