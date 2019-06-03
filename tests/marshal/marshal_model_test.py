# -*- coding: utf-8 -*-
import copy
import datetime

import pytest

from bravado_core.exception import SwaggerMappingError
from bravado_core.marshal import marshal_model
from bravado_core.spec import Spec


def test_pet(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    Category = petstore_spec.definitions['Category']
    Tag = petstore_spec.definitions['Tag']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = Pet(
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
    result = marshal_model(petstore_spec, pet_spec, pet)

    expected = {
        'id': 1,
        'name': 'Fido',
        'status': 'sold',
        'photoUrls': [
            'wagtail.png',
            'bark.png',
        ],
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
    assert expected == result


def test_attrs_set_to_None_are_absent_from_result(petstore_dict):
    # to recap: "required": ["name","photoUrls"]
    petstore_spec = Spec.from_dict(petstore_dict)
    Pet = petstore_spec.definitions['Pet']
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    pet = Pet(
        id=1,
        name='Fido',
        status=None,
        photoUrls=['wagtail.png', 'bark.png'],
        category=None,
        tags=None,
    )
    result = marshal_model(petstore_spec, pet_spec, pet)

    expected = {
        'id': 1,
        'name': 'Fido',
        'photoUrls': [
            'wagtail.png',
            'bark.png',
        ],
    }
    assert expected == result


def test_value_is_not_dict_like_raises_error(petstore_dict):
    petstore_spec = Spec.from_dict(petstore_dict)
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    value = 'i am not a dict'
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_model(petstore_spec, pet_spec, value)
    assert "Expected type to be dict or Model to marshal value '{}' to a dict. Was {} instead.".format(
        value, type(value),
    ) in str(excinfo.value)


def test_marshal_model_with_none_model_type(petstore_spec):
    model_spec = {'x-model': 'Foobar'}
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_model(petstore_spec, model_spec, object())
    assert 'Unknown model Foobar' in str(excinfo.value)


def test_marshal_nullable_model(petstore_spec):
    pet_spec = copy.deepcopy(petstore_spec.spec_dict['definitions']['Pet'])
    pet_spec['x-nullable'] = True
    assert marshal_model(petstore_spec, pet_spec, None) is None


def test_marshal_non_nullable_model(petstore_spec):
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    with pytest.raises(SwaggerMappingError) as excinfo:
        marshal_model(petstore_spec, pet_spec, None)
    assert 'is a required value' in str(excinfo.value)


def test_marshal_model_with_with_different_specs(petstore_dict, petstore_spec):
    pet_spec = petstore_spec.spec_dict['definitions']['Pet']
    new_petstore_spec = Spec.from_dict(petstore_dict)
    model = new_petstore_spec.definitions['Pet'](
        id=1,
        name='Fido',
        status=None,
        photoUrls=['wagtail.png', 'bark.png'],
        category=None,
        tags=None,
    )

    assert marshal_model(petstore_spec, pet_spec, model) == {
        'id': 1, 'name': 'Fido', 'photoUrls': ['wagtail.png', 'bark.png'],
    }


def test_marshal_model_polymorphic_specs(polymorphic_spec):
    PetList = polymorphic_spec.definitions['PetList']
    Dog = polymorphic_spec.definitions['Dog']
    Cat = polymorphic_spec.definitions['Cat']
    list_of_pets_model = PetList(
        number_of_pets=2,
        list=[
            Dog(
                name='a dog name',
                type='Dog',
                birth_date=datetime.date(2017, 3, 9),
            ),
            Cat(
                name='a cat name',
                type='Cat',
                color='white',
            ),
        ],
    )
    polymorphic_spec.config['use_models'] = True
    pet_list = marshal_model(
        swagger_spec=polymorphic_spec,
        model_spec=polymorphic_spec.spec_dict['definitions']['PetList'],
        model_value=list_of_pets_model,
    )

    assert pet_list == {
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
