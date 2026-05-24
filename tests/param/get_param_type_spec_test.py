# -*- coding: utf-8 -*-
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation
from bravado_core.param import get_param_type_spec
from bravado_core.param import Param
from bravado_core.spec import Spec


@pytest.fixture
def body_param_spec():
    return {
        'name': 'body',
        'in': 'body',
        'description': 'pet id',
        'required': True,
        'schema': {
            'type': 'string',
        },
    }


def test_location_is_body(empty_swagger_spec, body_param_spec):
    param = Param(empty_swagger_spec, Mock(spec=Operation), body_param_spec)
    assert body_param_spec['schema'] == get_param_type_spec(param)


def test_location_is_not_body(empty_swagger_spec):
    for location in ('path', 'query', 'header', 'formData',):
        param_spec = {
            'name': 'petId',
            'in': location,
            'description': 'ID of pet that needs to be updated',
            'required': True,
            'type': 'string',
        }
        param = Param(empty_swagger_spec, Mock(spec=Operation), param_spec)
        assert param_spec == get_param_type_spec(param)


def test_location_invalid(empty_swagger_spec, body_param_spec):
    body_param_spec['in'] = 'foo'
    param = Param(empty_swagger_spec, Mock(spec=Operation), body_param_spec)

    with pytest.raises(SwaggerMappingError) as excinfo:
        get_param_type_spec(param)
    assert 'location foo' in str(excinfo.value)


def test_ref(minimal_swagger_dict, body_param_spec):
    minimal_swagger_dict['parameters'] = {
        'PetIdParam': body_param_spec,
    }
    param_ref_spec = {'$ref': '#/parameters/PetIdParam'}
    swagger_spec = Spec(minimal_swagger_dict)
    param = Param(swagger_spec, Mock(spec=Operation), param_ref_spec)
    assert {'type': 'string'} == get_param_type_spec(param)
