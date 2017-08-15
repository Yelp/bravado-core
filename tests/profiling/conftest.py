# -*- coding: utf-8 -*-
import uuid

import pytest

from bravado_core.operation import Operation


@pytest.fixture(params=[100, 1000, 5000])
def small_pets(request, scope="module"):
    pets = []
    for i in range(request.param):
        pets.append({
            'name': str(uuid.uuid4()),
            'photoUrls': [str(uuid.uuid4())]
        })
    return pets


@pytest.fixture(params=[100, 1000, 5000])
def large_pets(request, scope="module"):
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


@pytest.fixture(params=[True, False])
def petstore_op(request, petstore_spec):
    spec_dict = petstore_spec.spec_dict['paths']['/pet/findByTags']['get']
    op = Operation(petstore_spec, '/pet/findByStatus', 'get', spec_dict)
    op.swagger_spec.config['validate_responses'] = request.param
    return op
