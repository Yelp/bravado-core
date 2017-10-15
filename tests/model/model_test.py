# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import create_model_type
from bravado_core.model import Model
from bravado_core.schema import collapsed_properties
from bravado_core.unmarshal import unmarshal_model


def test_model_properties_iteration(definitions_spec, user_type, user_kwargs):
    user = user_type(**user_kwargs)
    assert set(user) == set(definitions_spec['User']['properties'].keys())


def test_model_properties_iteration_additionalProperties(definitions_spec, user_type, user_kwargs):
    user_type._model_spec['additionalProperties'] = True
    user = user_type(foo='bar', **user_kwargs)
    assert set(user) == set(definitions_spec['User']['properties'].keys()).union({'foo'})
    assert user._additional_props == {'foo'}


def test_model_properties_iteration_allOf(cat_swagger_spec, cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    assert set(cat) == set(collapsed_properties(
        cat_swagger_spec.spec_dict['definitions']['Cat'], cat_swagger_spec
    ).keys())


def test_model_delete_property(definitions_spec, user_type, user_kwargs):
    user = user_type(**user_kwargs)

    assert 'id' in user
    del user.id
    assert 'id' in user
    # deleting a property defined in the spec should set the value to None
    assert user.id is None

    assert all(
        user[property] == user_kwargs.get(property)
        for property in definitions_spec['User']['properties']
        if property != 'id'
    )


def test_model_delete_not_existing_property(user_type, user_kwargs):
    user = user_type(**user_kwargs)

    with pytest.raises(Exception) as ex:
        del user.not_existing_property
    assert ex.type == AttributeError
    assert ex.value.args[0] == 'not_existing_property'


def test_model_delete_additional_property(definitions_spec, user_type, user_kwargs):
    user_type._model_spec['additionalProperties'] = True
    user = user_type(foo='bar', **user_kwargs)

    assert 'foo' in user
    assert user._additional_props == {'foo'}
    del user.foo
    # deleting a property not defined in the spec should remove it from the available properties
    assert 'foo' not in user
    assert user._additional_props == set()
    assert hasattr(user, 'foo') is False

    assert all(
        user[property] == user_kwargs.get(property)
        for property in definitions_spec['User']['properties']
    )


def test_model_as_dict(definitions_spec, user_type, user_kwargs):
    user = user_type(**user_kwargs)
    user_dict = user._as_dict()
    assert {k: user_kwargs.get(k) for k in definitions_spec['User']['properties'].keys()} == user_dict
    assert user._asdict() == user_dict


def test_model_is_instance_same_class(user_type, user_kwargs):
    user = user_type(**user_kwargs)
    assert user_type._isinstance(user)
    assert isinstance(user, user_type)


def test_model_is_instance_inherits_from(cat_swagger_spec, pet_type, pet_spec, cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    new_pet_type = create_model_type(cat_swagger_spec, 'Pet', pet_spec)
    assert pet_type._isinstance(cat)
    assert isinstance(cat, cat_type)
    assert isinstance(cat, pet_type)
    assert isinstance(cat, new_pet_type)


@pytest.mark.parametrize(
    'recursive',
    [
        True,
        False,
    ]
)
def test_marshal_as_dict_recursive(polymorphic_spec, recursive):
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
        ]
    }
    pet_list = unmarshal_model(
        swagger_spec=polymorphic_spec,
        model_spec=polymorphic_spec.spec_dict['definitions']['PetList'],
        model_value=list_of_pets_dict,
    )

    dictionary = pet_list._as_dict(recursive=recursive)
    assert all(
        # if recursive is True the pet from the dictionary should not be a Model
        isinstance(pet, Model) is not recursive
        for pet in dictionary['list']
    )


@pytest.mark.parametrize(
    'export_additional_properties',
    [
        True,
        False,
    ]
)
def test_model_as_dict_additional_property(definitions_spec, user_type, user_kwargs, export_additional_properties):
    user_type._model_spec['additionalProperties'] = True
    user = user_type(foo='bar', **user_kwargs)
    expected_dict = {k: user_kwargs.get(k) for k in definitions_spec['User']['properties'].keys()}
    if export_additional_properties:
        expected_dict['foo'] = 'bar'
    assert expected_dict == user._as_dict(additional_properties=export_additional_properties)


@pytest.mark.parametrize(
    'instance_dict, object_type, possible_object_types',
    (
        [
            {
                'name': 'a generic pet name',
                'type': 'GenericPet',
            },
            'GenericPet',
            ['GenericPet'],
        ],
        [
            {
                'name': 'a dog name',
                'type': 'Dog',
                'birth_date': '2017-03-09',
            },
            'Dog',
            ['GenericPet', 'Dog'],
        ],
    )
)
def test_model_isinstance(polymorphic_spec, instance_dict, object_type, possible_object_types):
    model = unmarshal_model(
        swagger_spec=polymorphic_spec,
        model_spec=polymorphic_spec.spec_dict['definitions'][object_type],
        model_value=instance_dict
    )
    assert any(
        isinstance(model, polymorphic_spec.definitions[possible_object_type])
        for possible_object_type in possible_object_types
    )
