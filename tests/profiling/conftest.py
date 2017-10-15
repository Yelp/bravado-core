# -*- coding: utf-8 -*-
import uuid

import pytest

from bravado_core.spec import Spec


NUMBER_OF_OBJECTS = [100, 1000, 5000]


@pytest.fixture(params=NUMBER_OF_OBJECTS, scope='module')
def small_pets(request):
    pets = []
    for i in range(request.param):
        pets.append({
            'name': str(uuid.uuid4()),
            'photoUrls': [str(uuid.uuid4())]
        })
    return pets


@pytest.fixture(params=NUMBER_OF_OBJECTS, scope='module')
def large_pets(request):
    pets = []
    for i in range(request.param):
        pets.append({
            'id': i + 1,
            'name': str(uuid.uuid4()),
            'status': 'available',
            'photoUrls': ['wagtail.png', 'bark.png'],
            'category': {
                'id': 200,
                'name': 'friendly',
            },
            'tags': [
                {
                    'id': 99,
                    'name': 'mini'
                },
                {
                    'id': 100,
                    'name': 'brown'
                },
            ],
        })
    return pets


@pytest.fixture
def perf_petstore_spec(request, petstore_spec):
    return Spec.from_dict(
        spec_dict=petstore_spec.spec_dict,
        origin_url=petstore_spec.origin_url,
        config=dict(petstore_spec.config),
    )


@pytest.fixture(
    params=[True, False],
    ids=['validate', 'not_validate'],
)
def petstore_op(request, perf_petstore_spec):
    op = perf_petstore_spec.resources['pet'].findPetsByStatus
    op.swagger_spec.config['validate_responses'] = request.param
    return op
