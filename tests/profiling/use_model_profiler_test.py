# -*- coding: utf-8 -*-
import pytest

from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_schema_object


@pytest.fixture(
    params=[True, False],
    ids=['use-models', 'use-dicts'],
)
def perf_petstore_spec(request, petstore_spec):
    return Spec.from_dict(
        spec_dict=petstore_spec.spec_dict,
        origin_url=petstore_spec.origin_url,
        config=dict(petstore_spec.config, use_models=request.param),
    )


@pytest.fixture
def findByStatusReponseSchema(perf_petstore_spec):
    parts = ['paths', '/pet/findByStatus', 'get', 'responses', '200', 'schema']
    result = perf_petstore_spec._internal_spec_dict
    for part in parts:
        result = perf_petstore_spec.deref(result[part])
    return result


def test_small_objects(
    benchmark, perf_petstore_spec, findByStatusReponseSchema, small_pets,
):
    benchmark(
        unmarshal_schema_object,
        perf_petstore_spec,
        findByStatusReponseSchema,
        small_pets,
    )


def test_large_objects(
    benchmark, perf_petstore_spec, findByStatusReponseSchema, large_pets,
):
    benchmark(
        unmarshal_schema_object,
        perf_petstore_spec,
        findByStatusReponseSchema,
        large_pets,
    )
