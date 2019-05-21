# -*- coding: utf-8 -*-
from bravado_core.unmarshal import unmarshal_schema_object


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
