# -*- coding: utf-8 -*-
import datetime

import pytest
from dateutil.tz import tzutc

from bravado_core.exception import SwaggerMappingError
from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_model


@pytest.fixture
def pet_dict():
    return {
        'id': 1,
        'name': 'Fido',
        'status': 'sold',
        'photoUrls': ['wagtail.png', 'bark.png'],
        'category': {
            'id': 200,
            'name': 'friendly',
        },
        'tags': [
            {
                'id': 99,
                'name': 'mini',
            },
            {
                'id': 100,
                'name': 'brown',
            },
        ],
    }


@pytest.mark.parametrize(
    'releaseDate',
    (
        '1981',
        None,
    ),
)
def test_definitions_with_ref(composition_spec, releaseDate):
    PongClone = composition_spec.definitions['pongClone']
    pong_clone_spec = composition_spec.spec_dict['definitions']['pongClone']
    pong_clone_dict = {
        'pang': 'hello',
        'additionalFeature': 'new!',
        'gameSystem': 'Fatari',
    }
    if releaseDate:
        pong_clone_dict['releaseDate'] = releaseDate

    pong_clone = unmarshal_model(
        composition_spec, pong_clone_spec,
        pong_clone_dict,
    )

    assert isinstance(pong_clone, PongClone)
    assert 'hello' == pong_clone.pang
    assert 'new!' == pong_clone.additionalFeature
    assert 'Fatari' == pong_clone.gameSystem
    if releaseDate or composition_spec.config['include_missing_properties']:
        assert hasattr(pong_clone, 'releaseDate') is True
        assert releaseDate == pong_clone.releaseDate
    else:
        assert hasattr(pong_clone, 'releaseDate') is False


def test_pet(petstore_dict, pet_dict):
    # Covers:
    #   - model with primitives properties
    #   - model with an array
    #   - model with a nested model
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Category = petstore_spec.definitions['Category']
    Tag = petstore_spec.definitions['Tag']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']

    pet = unmarshal_model(petstore_spec, pet_spec, pet_dict)

    assert isinstance(pet, Pet)
    assert 1 == pet.id
    assert 'Fido' == pet.name
    assert 'sold' == pet.status
    assert ['wagtail.png', 'bark.png'] == pet.photoUrls
    assert isinstance(pet.category, Category)
    assert 200 == pet.category.id
    assert 'friendly' == pet.category.name
    assert isinstance(pet.tags, list)
    assert 2 == len(pet.tags)
    assert isinstance(pet.tags[0], Tag)
    assert 99 == pet.tags[0].id
    assert 'mini' == pet.tags[0].name
    assert isinstance(pet.tags[1], Tag)
    assert 100 == pet.tags[1].id
    assert 'brown' == pet.tags[1].name


def test_Nones_are_reintroduced_for_declared_properties_that_are_not_present(petstore_dict, pet_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Tag = petstore_spec.definitions['Tag']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']

    # Deleting "status" and "category" from pet_dict means that should still be
    # attrs on Pet with a None value after unmarshaling
    del pet_dict['status']
    del pet_dict['category']

    pet = unmarshal_model(petstore_spec, pet_spec, pet_dict)

    assert isinstance(pet, Pet)
    assert 1 == pet.id
    assert 'Fido' == pet.name
    assert pet.status is None
    assert ['wagtail.png', 'bark.png'] == pet.photoUrls
    assert pet.category is None
    assert isinstance(pet.tags, list)
    assert 2 == len(pet.tags)
    assert isinstance(pet.tags[0], Tag)
    assert 99 == pet.tags[0].id
    assert 'mini' == pet.tags[0].name
    assert isinstance(pet.tags[1], Tag)
    assert 100 == pet.tags[1].id
    assert 'brown' == pet.tags[1].name


def test_value_is_not_dict_like_raises_error(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']

    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_model(petstore_spec, pet_spec, 'i am not a dict')

    assert 'Expected type to be dict' in str(excinfo.value)


@pytest.mark.filterwarnings("ignore:.*with siblings that will be overwritten")
def test_nullable_object_properties(petstore_dict, pet_dict):
    pet_spec_dict = petstore_dict['definitions']['Pet']
    pet_spec_dict['required'].append('category')
    pet_spec_dict['properties']['category']['x-nullable'] = True
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet_dict['category'] = None

    pet = unmarshal_model(petstore_spec, pet_spec, pet_dict)

    assert isinstance(pet, Pet)
    assert pet.category is None


def test_non_nullable_object_properties(petstore_dict, pet_dict):
    pet_spec_dict = petstore_dict['definitions']['Pet']
    pet_spec_dict['required'].append('category')
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet_dict['category'] = None

    with pytest.raises(SwaggerMappingError):
        unmarshal_model(petstore_spec, pet_spec, pet_dict)


def test_nullable_array_properties(petstore_dict, pet_dict):
    pet_spec_dict = petstore_dict['definitions']['Pet']
    pet_spec_dict['properties']['tags']['x-nullable'] = True
    pet_spec_dict['required'].append('tags')
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet_dict['tags'] = None

    pet = unmarshal_model(petstore_spec, pet_spec, pet_dict)

    assert isinstance(pet, Pet)
    assert pet.tags is None


def test_non_nullable_array_properties(petstore_dict, pet_dict):
    pet_spec_dict = petstore_dict['definitions']['Pet']
    pet_spec_dict['required'].append('tags')
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet_dict['tags'] = None

    with pytest.raises(SwaggerMappingError):
        unmarshal_model(petstore_spec, pet_spec, pet_dict)


def test_unmarshal_model_with_none_model_type(petstore_spec):
    model_spec = {'x-model': 'Foobar'}

    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_model(petstore_spec, model_spec, {})

    assert 'Unknown model Foobar' in str(excinfo.value)


def test_unmarshal_model_polymorphic_specs(polymorphic_spec):
    list_of_pets_dict = {
        'number_of_pets': 2,
        'list': [
            {
                'name': 'a dog name',
                'type': 'Dog',
                'birth_date': '2017-03-09',
            },
            {
                'name': 'a cat name',
                'type': 'Cat',
                'color': 'white',
            },
        ],
    }
    pet_list = unmarshal_model(
        swagger_spec=polymorphic_spec,
        model_spec=polymorphic_spec.spec_dict['definitions']['PetList'],
        model_value=list_of_pets_dict,
    )

    assert isinstance(pet_list, polymorphic_spec.definitions['PetList'])

    assert pet_list.number_of_pets == list_of_pets_dict['number_of_pets']
    assert len(pet_list.list) == len(list_of_pets_dict['list'])

    for list_item_model, list_item_dict in zip(pet_list.list, list_of_pets_dict['list']):
        assert isinstance(list_item_model, polymorphic_spec.definitions[list_item_dict['type']])
        assert list_item_model._marshal() == list_item_dict


@pytest.mark.parametrize(
    'additionalProperties, value, expected',
    [
        (
            None,
            {},
            {'property': None},
        ),
        (
            None,
            {'property': '2018-05-21T00:00:00+00:00'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc())},
        ),
        (
            {},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
        ),
        (
            True,
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
        ),
        (
            False,
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            # Unmarshaling does not do validation
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': '2018-05-21'},
        ),
        (
            {'type': 'string', 'format': 'date'},
            {'property': '2018-05-21T00:00:00+00:00', 'other': '2018-05-21'},
            {'property': datetime.datetime(2018, 5, 21, tzinfo=tzutc()), 'other': datetime.date(2018, 5, 21)},
        ),
    ],
)
def test_unmarshal_model_with_additional_properties(minimal_swagger_dict, additionalProperties, value, expected):
    MyModel_spec = {
        'properties': {
            'property': {
                'type': 'string',
                'format': 'date-time',
            },
        },
        'type': 'object',
        'x-model': 'MyModel',
    }
    if additionalProperties is not None:
        MyModel_spec['additionalProperties'] = additionalProperties
    minimal_swagger_dict['definitions']['MyModel'] = MyModel_spec
    spec = Spec.from_dict(minimal_swagger_dict)
    assert unmarshal_model(spec, MyModel_spec, value)._as_dict() == expected
