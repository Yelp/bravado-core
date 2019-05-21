# -*- coding: utf-8 -*-
from bravado_core.marshal import marshal_schema_object


def test_small_objects(benchmark, perf_petstore_spec, findByStatusReponseSchema, small_pets):
    small_pets_models = [
        perf_petstore_spec.definitions['Pet']._unmarshal(value)
        for value in small_pets
    ]
    benchmark(
        marshal_schema_object,
        perf_petstore_spec,
        findByStatusReponseSchema,
        small_pets_models,
    )


def test_large_objects(benchmark, perf_petstore_spec, findByStatusReponseSchema, large_pets):
    large_pets_models = [
        perf_petstore_spec.definitions['Pet']._unmarshal(value)
        for value in large_pets
    ]
    benchmark(
        marshal_schema_object,
        perf_petstore_spec,
        findByStatusReponseSchema,
        large_pets_models,
    )
