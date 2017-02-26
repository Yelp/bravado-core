# -*- coding: utf-8 -*-
import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.param import COLLECTION_FORMATS
from bravado_core.param import unmarshal_collection_format
from bravado_core.spec import Spec


@pytest.fixture
def array_spec():
    return {
        'name': 'biz_ids',
        'in': 'query',
        'type': 'array',
        'items': {
            'type': 'integer'
        },
        'collectionFormat': 'csv',
    }


def test_defaults_to_csv(empty_swagger_spec, array_spec):
    del array_spec['collectionFormat']
    assert [1, 2, 3] == unmarshal_collection_format(
        empty_swagger_spec, array_spec, '1,2,3')


def test_formats(empty_swagger_spec, array_spec):
    for fmt, sep in COLLECTION_FORMATS.items():
        array_spec['collectionFormat'] = fmt
        param_value = sep.join(['1', '2', '3'])
        assert [1, 2, 3] == unmarshal_collection_format(
            empty_swagger_spec, array_spec, param_value)


@pytest.mark.parametrize('format_name,separator', COLLECTION_FORMATS.items())
def test_formats_empty_list(empty_swagger_spec, array_spec, format_name, separator):
    array_spec['collectionFormat'] = format_name
    param_value = separator.join([])
    assert [] == unmarshal_collection_format(
        empty_swagger_spec,
        array_spec,
        param_value,
    )


def test_multi_no_op_because_handled_by_http_client_lib(empty_swagger_spec,
                                                        array_spec):
    array_spec['collectionFormat'] = 'multi'
    assert [1, 2, 3] == unmarshal_collection_format(
        empty_swagger_spec, array_spec, [1, 2, 3])


def test_ref(minimal_swagger_dict, array_spec):
    for fmt, sep in COLLECTION_FORMATS.items():
        array_spec['collectionFormat'] = fmt
        minimal_swagger_dict['parameters'] = {
            'BizIdsParam': array_spec
        }
        ref_spec = {'$ref': '#/parameters/BizIdsParam'}
        swagger_spec = Spec(minimal_swagger_dict)

        param_value = sep.join(['1', '2', '3'])
        assert [1, 2, 3] == unmarshal_collection_format(
            swagger_spec, ref_spec, param_value)


def test_array_is_none_and_not_required(empty_swagger_spec, array_spec):
    assert unmarshal_collection_format(empty_swagger_spec, array_spec,
                                       value=None) is None


def test_array_is_none_and_required(empty_swagger_spec, array_spec):
    array_spec['required'] = True
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_collection_format(empty_swagger_spec, array_spec, value=None)
    assert 'is a required value' in str(excinfo.value)


def test_array_is_none_and_nullable(empty_swagger_spec, array_spec):
    array_spec['required'] = True
    array_spec['x-nullable'] = True
    assert unmarshal_collection_format(empty_swagger_spec, array_spec,
                                       value=None) is None
