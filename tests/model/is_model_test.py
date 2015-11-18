import pytest

from bravado_core.model import is_model
from bravado_core.schema import is_required
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
    assert not is_required(minimal_swagger_spec, object_spec)


def test_ref(minimal_swagger_dict, model_spec):
    minimal_swagger_dict['definitions']['Foo'] = model_spec
    swagger_spec = Spec(minimal_swagger_dict)
    assert is_model(swagger_spec, {'$ref': '#/definitions/Foo'})
