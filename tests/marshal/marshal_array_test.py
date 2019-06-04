# -*- coding: utf-8 -*-
import copy

import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.marshal import marshal_array
from bravado_core.spec import Spec


@pytest.fixture
def int_array_spec():
    return {
        'type': 'array',
        'items': {
            'type': 'integer',
        },
    }


def test_primitive_array(empty_swagger_spec, int_array_spec):
    result = marshal_array(empty_swagger_spec, int_array_spec, [1, 2, 3])
    assert [1, 2, 3] == result


def test_tuple(empty_swagger_spec, int_array_spec):
    result = marshal_array(empty_swagger_spec, int_array_spec, (1, 2, 3))
    assert [1, 2, 3] == result


def test_empty_array(empty_swagger_spec, int_array_spec):
    result = marshal_array(empty_swagger_spec, int_array_spec, [])
    assert [] == result


def test_with_no_items_schema_defined(empty_swagger_spec):
    value = [1, 2.3, '4', ['5'], {'6': 7}]
    result = marshal_array(
        empty_swagger_spec,
        {
            'type': 'array',
        },
        value,
    )
    assert result == value


def test_array_of_array(empty_swagger_spec):
    array_of_array_spec = {
        'type': 'array',
        'items': {
            'type': 'array',
            'items': {
                'type': 'string',
            },
        },
    }
    input = [
        ['one'],
        ['two', 'three'],
        ['four', 'five', 'six'],
    ]
    expected = copy.deepcopy(input)
    result = marshal_array(empty_swagger_spec, array_of_array_spec, input)
    assert expected == result


def test_array_of_objects(empty_swagger_spec):
    array_of_addresses_spec = {
        'type': 'array',
        'items': {
            'type': 'object',
            'properties': {
                'number': {
                    'type': 'number',
                },
                'street_name': {
                    'type': 'string',
                },
                'street_type': {
                    'type': 'string',
                    'enum': [
                        'Street',
                        'Avenue',
                        'Boulevard',
                    ],
                },
            },
        },
    }
    input = [
        {
            'number': 1600,
            'street_name': 'Pennsylvania',
            'street_type': 'Avenue',
        },
        {
            'number': 1700,
            'street_name': 'Main',
            'street_type': 'Street',
        },
        {
            'number': 1800,
            'street_name': 'Yelpy',
            'street_type': 'Boulevard',
        },
    ]
    expected = copy.deepcopy(input)
    result = marshal_array(empty_swagger_spec, array_of_addresses_spec, input)
    assert expected == result


def test_array_of_models(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Category = petstore_spec.definitions['Category']
    Tag = petstore_spec.definitions['Tag']

    array_of_pets_spec = {
        'type': 'array',
        'items': petstore_spec.spec_dict['definitions']['Pet'],
    }

    fido = Pet(
        id=1,
        name='Fido',
        status='sold',
        photoUrls=['wagtail.png', 'bark.png'],
        category=Category(id=200, name='friendly'),
        tags=[
            Tag(id=99, name='mini'),
            Tag(id=100, name='brown'),
        ],
    )

    darwin = Pet(
        id=2,
        name='Darwin',
        status='pending',
        photoUrls=['snausages.png', 'bacon.png'],
        category=Category(id=300, name='mascot'),
        tags=[],
    )

    sumi = Pet(
        id=3,
        name='Sumi',
        status='available',
        photoUrls=['puggies.png', 'bumblebee.png'],
        category=Category(id=400, name='pugly'),
        tags=[
            Tag(id=101, name='sumiwoo'),
        ],
    )

    pets = [fido, darwin, sumi]
    result = marshal_array(petstore_spec, array_of_pets_spec, pets)

    for i, expected in enumerate(pets):
        actual = result[i]
        assert expected.name == actual['name']
        assert expected.id == actual['id']
        assert expected.photoUrls == actual['photoUrls']
        assert expected.status == actual['status']

        for j, expected_tag in enumerate(expected.tags):
            actual_tag = actual['tags'][j]
            assert expected_tag.id == actual_tag['id']
            assert expected_tag.name == actual_tag['name']

        assert expected.category.id == actual['category']['id']
        assert expected.category.name == actual['category']['name']


def test_non_list_like_type_throws_error(empty_swagger_spec, int_array_spec):
    i_am_not_a_list = dict()
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_array(empty_swagger_spec, int_array_spec, i_am_not_a_list)
    assert 'Expected list like type' in str(excinfo.value)


def test_ref(minimal_swagger_dict, int_array_spec):
    minimal_swagger_dict['definitions']['IntArray'] = int_array_spec
    ref_spec = {'$ref': '#/definitions/IntArray'}
    swagger_spec = Spec(minimal_swagger_dict)
    result = marshal_array(swagger_spec, ref_spec, [1, 2, 3])
    assert [1, 2, 3] == result


def test_nullable_array(empty_swagger_spec, int_array_spec):
    int_array_spec['x-nullable'] = True
    result = marshal_array(empty_swagger_spec, int_array_spec, None)
    assert result is None


def test_non_nullable_array(empty_swagger_spec, int_array_spec):
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_array(empty_swagger_spec, int_array_spec, None)
    assert 'is a required value' in str(excinfo.value)
