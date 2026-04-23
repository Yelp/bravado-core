# -*- coding: utf-8 -*-
import datetime
from copy import deepcopy

import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from six import add_metaclass

from bravado_core.content_type import APP_JSON
from bravado_core.model import Model
from bravado_core.model import ModelMeta
from bravado_core.response import IncomingResponse
from bravado_core.response import unmarshal_response
from bravado_core.schema import collapsed_properties
from bravado_core.schema import is_ref
from bravado_core.spec import Spec
from bravado_core.unmarshal import unmarshal_model


@add_metaclass(ModelMeta)
class WrongModelClass(object):
    """
    This class is a class that mimics Model class.
    It is created for testing that ModelMeta __isinstancecheck__
    does properly its job.
    """
    pass


class ModelFromWrongModelClass(WrongModelClass):
    pass


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
    assert set(cat) == set(
        collapsed_properties(
            cat_swagger_spec.spec_dict['definitions']['Cat'], cat_swagger_spec,
        ).keys(),
    )


def test_model_delete_property(definitions_spec, user_type, user_kwargs):
    user = user_type(**user_kwargs)

    assert 'id' in user
    del user.id
    assert 'id' in user
    # deleting a property defined in the spec should set the value to None
    assert user.id is None

    properties_with_not_matching_values = {
        prop_name
        for prop_name in definitions_spec['User']['properties']
        if prop_name != 'id' and user[prop_name] != user_kwargs.get(prop_name)
    }
    assert not properties_with_not_matching_values


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


@pytest.mark.filterwarnings('ignore:_isinstance is deprecated')
@pytest.mark.filterwarnings('ignore:Model object methods are now prefixed')
def test_model_isinstance_same_class(user_type, user_kwargs):
    user = user_type(**user_kwargs)
    assert user_type._isinstance(user)
    assert user_type.isinstance(user)
    assert isinstance(user, user_type)


def test_model_issubclass_same_class(user_type):
    assert issubclass(user_type, user_type)
    assert issubclass(user_type, Model)


@pytest.mark.filterwarnings('ignore:_isinstance is deprecated')
@pytest.mark.filterwarnings('ignore:Model object methods are now prefixed')
def test_model_isinstance_inherits_from(cat_swagger_spec, pet_type, pet_spec, cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    assert pet_type._isinstance(cat)
    assert pet_type.isinstance(cat)
    assert isinstance(cat, cat_type)
    assert isinstance(cat, pet_type)


def test_model_issubclass_inherits_from(pet_type, cat_type):
    assert issubclass(cat_type, pet_type)


def test_model_isinstance_model_class_generated_by_different_Spec_object(cat_swagger_spec, cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    new_cat_spec = Spec.from_dict(cat_swagger_spec.client_spec_dict)
    assert isinstance(cat, new_cat_spec.definitions['Cat'])


def test_model_equality_if_model_class_generated_by_different_Spec_object(cat_swagger_spec, cat_type, cat_kwargs):
    cat = cat_type(**cat_kwargs)
    new_cat_spec = Spec.from_dict(cat_swagger_spec.client_spec_dict)
    new_cat_type = new_cat_spec.definitions['Cat']
    new_cat = new_cat_type(**cat_kwargs)
    assert cat == new_cat


def test_model_deepcopy(user_type, user_kwargs):
    user = user_type(**user_kwargs)
    user_copy = deepcopy(user)

    assert isinstance(user_copy, user_type)
    assert user == user_copy
    assert user._as_dict() == user_copy._as_dict()


@pytest.mark.parametrize(
    'recursive',
    [
        True,
        False,
    ],
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
        ],
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
    ],
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
    ),
)
def test_model_isinstance(polymorphic_spec, instance_dict, object_type, possible_object_types):
    model = unmarshal_model(
        swagger_spec=polymorphic_spec,
        model_spec=polymorphic_spec.spec_dict['definitions'][object_type],
        model_value=instance_dict,
    )
    assert not any(
        not isinstance(model, polymorphic_spec.definitions[possible_object_type])
        for possible_object_type in possible_object_types
    )


@pytest.mark.parametrize('internally_dereference_refs', [True, False])
@pytest.mark.parametrize('use_models', [True, False])
@pytest.mark.parametrize('validate_responses', [True, False])
def test_ensure_polymorphic_objects_are_correctly_build_in_case_of_fully_dereferenced_specs(
    polymorphic_dict, validate_responses, use_models, internally_dereference_refs,
):
    raw_response = {
        'number_of_pets': 1,
        'list': [{'name': 'name', 'type': 'Dog', 'birth_date': '2017-11-02'}],
    }
    spec = Spec.from_dict(
        spec_dict=polymorphic_dict,
        config={
            'validate_responses': validate_responses,
            'use_models': use_models,
            'internally_dereference_refs': internally_dereference_refs,
        },
        origin_url='',
    )

    response = Mock(
        spec=IncomingResponse,
        status_code=200,
        headers={'content-type': APP_JSON},
        json=Mock(return_value=raw_response),
    )
    unmarshaled_response = unmarshal_response(response, spec.resources['pets'].get_pets)

    pet_list_model_type = spec.definitions['PetList'] if use_models else dict
    dog_model_type = spec.definitions['Dog'] if use_models else dict
    expected_response = pet_list_model_type(
        number_of_pets=1,
        list=[
            dog_model_type(birth_date=datetime.date(2017, 11, 2), name='name', type='Dog'),
        ],
    )
    assert expected_response == unmarshaled_response


def test_ensure_model_spec_contains_reference_if_fully_dereference_is_not_enabled(polymorphic_dict):
    spec = Spec.from_dict(
        spec_dict=polymorphic_dict,
        config={'internally_dereference_refs': False},
        origin_url='',
    )

    # Ensure that Dog model has reference to GenericPet
    assert any(
        is_ref(all_of_item) and all_of_item['$ref'] == '#/definitions/GenericPet'
        for all_of_item in spec.definitions['Dog']._model_spec['allOf']
    )


def test_ensure_model_spec_does_not_contain_references_if_fully_dereference_is_enabled(polymorphic_dict):
    spec = Spec.from_dict(
        spec_dict=polymorphic_dict,
        config={'internally_dereference_refs': True},
        origin_url='',
    )

    # Ensure that no reference are present
    assert all(
        not is_ref(all_of_item)
        for all_of_item in spec.definitions['Dog']._model_spec['allOf']
    )

    # Ensure that GenericPet is part of the allOf items of Dog
    assert any(
        all_of_item == spec.definitions['GenericPet']._model_spec
        for all_of_item in spec.definitions['Dog']._model_spec['allOf']
    )


def test_isinstance_wrong_model_class_is_not_confused_with_model():
    assert isinstance(ModelFromWrongModelClass(), Model) is False
    assert isinstance(ModelFromWrongModelClass(), WrongModelClass) is True


def test_isinstance_model_instance_is_recognized_properly(user_type, user_kwargs, cat_type):
    assert isinstance(user_type(**user_kwargs), WrongModelClass) is False
    assert isinstance(user_type(**user_kwargs), Model) is True
    assert isinstance(user_type(**user_kwargs), user_type) is True
    assert isinstance(user_type(**user_kwargs), cat_type) is False


def test_isinstance_works_in_case_of_inheritance(polymorphic_spec):
    dog = polymorphic_spec.definitions['Dog']._unmarshal({'name': 'name', 'type': 'Dog', 'birth_date': '2017-11-02'})
    assert isinstance(dog, polymorphic_spec.definitions['Dog']) is True
    assert isinstance(dog, polymorphic_spec.definitions['Cat']) is False
    assert isinstance(dog, polymorphic_spec.definitions['GenericPet']) is True


def test_ensure_that_tricking_abc_attributes_do_not_alter_results(polymorphic_spec):
    Cat = polymorphic_spec.definitions['Cat']
    Dog = polymorphic_spec.definitions['Dog']
    dog = Dog._unmarshal({'name': 'name', 'type': 'Dog', 'birth_date': '2017-11-02'})
    assert isinstance(dog, Dog)
    assert isinstance(dog, Dog)
    assert isinstance(dog, Cat) is False
    assert isinstance(dog, Cat) is False
