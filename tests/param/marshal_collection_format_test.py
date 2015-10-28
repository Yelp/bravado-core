import pytest

from bravado_core.param import marshal_collection_format, COLLECTION_FORMATS
from bravado_core.spec import Spec


@pytest.fixture
def param_spec():
    return {
        'name': 'foo',
        'in': 'query',
        'type': 'array',
        'items': {
            'type': 'integer'
        }
    }


def test_defaults_to_csv(empty_swagger_spec, param_spec):
    assert '1,2,3' == marshal_collection_format(empty_swagger_spec,
                                                param_spec, [1, 2, 3])


def test_formats(empty_swagger_spec, param_spec):
    for fmt, sep in COLLECTION_FORMATS.items():
        param_spec['collectionFormat'] = fmt
        result = marshal_collection_format(empty_swagger_spec,
                                           param_spec, [1, 2, 3])
        assert sep.join(['1', '2', '3']) == result


def test_multi_no_op_because_handled_by_http_client_lib(empty_swagger_spec,
                                                        param_spec):
    param_spec['collectionFormat'] = 'multi'
    assert [1, 2, 3] == marshal_collection_format(empty_swagger_spec,
                                                  param_spec, [1, 2, 3])


def test_ref(minimal_swagger_dict, param_spec):
    minimal_swagger_dict['parameters'] = {
        'FooParam': param_spec
    }
    ref_spec = {'$ref': '#/parameters/FooParam'}
    swagger_spec = Spec(minimal_swagger_dict)
    result = marshal_collection_format(swagger_spec, ref_spec, [1, 2, 3])
    assert result == '1,2,3'
