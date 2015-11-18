import pytest

from bravado_core.schema import get_format
from bravado_core.spec import Spec


@pytest.fixture
def int32_spec():
    return {'type': 'integer', 'format': 'int32'}


@pytest.fixture
def int_spec():
    return {'type': 'integer'}


def test_found(minimal_swagger_spec, int32_spec):
    assert 'int32' == get_format(minimal_swagger_spec, int32_spec)


def test_not_found(minimal_swagger_spec, int_spec):
    assert get_format(minimal_swagger_spec, int_spec) is None


def test_ref_found(minimal_swagger_dict, int32_spec):
    minimal_swagger_dict['definitions']['Int32'] = int32_spec
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert 'int32' == get_format(swagger_spec, {'$ref': '#/definitions/Int32'})


def test_ref_not_found(minimal_swagger_dict, int_spec):
    minimal_swagger_dict['definitions']['Int'] = int_spec
    swagger_spec = Spec.from_dict(minimal_swagger_dict)
    assert get_format(swagger_spec, {'$ref': '#/definitions/Int'}) is None
