# -*- coding: utf-8 -*-
import pytest

from bravado_core.unmarshal import unmarshal_schema_object


@pytest.fixture
def findByStatusReponseSchema(perf_petstore_spec):
    result = perf_petstore_spec._internal_spec_dict

    for part in ['paths', '/pet/findByStatus', 'get', 'responses', '200', 'schema']:
        result = perf_petstore_spec.deref(result)[part]

    return result


def test_small_objects(benchmark, perf_petstore_spec, findByStatusReponseSchema, small_pets):
    benchmark(
        unmarshal_schema_object,
        perf_petstore_spec,
        findByStatusReponseSchema,
        small_pets,
    )


def test_large_objects(benchmark, perf_petstore_spec, findByStatusReponseSchema, large_pets):
    benchmark(
        unmarshal_schema_object,
        perf_petstore_spec,
        findByStatusReponseSchema,
        large_pets,
    )
