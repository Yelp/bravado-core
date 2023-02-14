# -*- coding: utf-8 -*-
try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from bravado_core.model import create_model_type
from bravado_core.schema import is_ref


def test_pet_model(empty_swagger_spec, pet_spec):
    Pet = create_model_type(empty_swagger_spec, 'Pet', pet_spec)
    expected = set(['id', 'category', 'name', 'photoUrls', 'tags'])
    pet = Pet(id=1, name='Darwin')
    assert set(dir(pet)) == expected
    assert pet == Pet(id=1, name='Darwin')
    assert pet != Pet(id=2, name='Fido')
    assert "Pet(category=None, id=1, name='Darwin', photoUrls=None, tags=None)"\
           == repr(pet)


def test_no_arg_constructor(empty_swagger_spec, pet_spec):
    Pet = create_model_type(empty_swagger_spec, 'Pet', pet_spec)
    attr_names = (
        # '__doc__',  <-- will trigger docstring generation so skip for now
        '__eq__',
        '__init__',
        '__repr__',
        '__dir__',
    )
    for attr_name in attr_names:
        assert hasattr(Pet, attr_name)


@mock.patch('bravado_core.model.create_model_docstring', autospec=True)
def test_create_model_type_lazy_docstring(mock_create_docstring, empty_swagger_spec, pet_spec):
    pet_type = create_model_type(empty_swagger_spec, 'Pet', pet_spec)
    assert mock_create_docstring.call_count == 0
    assert pet_type.__doc__ == mock_create_docstring.return_value
    assert mock_create_docstring.call_count == 1


def test_marshal_and_unmarshal(petstore_spec):
    Pet = petstore_spec.definitions['Pet']
    pet_id = 1
    pet_name = 'Darwin'
    pet_photo_urls = []
    pet = Pet(id=pet_id, name=pet_name, photoUrls=pet_photo_urls)
    marshalled_model = pet._marshal()
    unmarshalled_marshalled_model = Pet._unmarshal(marshalled_model)

    assert marshalled_model == {'id': pet_id, 'name': pet_name, 'photoUrls': pet_photo_urls}
    assert isinstance(unmarshalled_marshalled_model, Pet)
    assert unmarshalled_marshalled_model.id == pet_id
    assert unmarshalled_marshalled_model.name == pet_name
    assert unmarshalled_marshalled_model.photoUrls == pet_photo_urls


@pytest.mark.filterwarnings("ignore: Model object methods are now prefixed with single underscore")
def test_deprecated_marshal_and_unmarshal(petstore_spec):
    """This test is a copy of the test above. It will be removed once we remove the deprecated
    marshal() and unmarshal() methods."""
    Pet = petstore_spec.definitions['Pet']
    pet_id = 1
    pet_name = 'Darwin'
    pet_photo_urls = []
    pet = Pet(id=pet_id, name=pet_name, photoUrls=pet_photo_urls)
    marshalled_model = pet.marshal()
    unmarshalled_marshalled_model = Pet.unmarshal(marshalled_model)

    assert marshalled_model == {'id': pet_id, 'name': pet_name, 'photoUrls': pet_photo_urls}
    assert isinstance(unmarshalled_marshalled_model, Pet)
    assert unmarshalled_marshalled_model.id == pet_id
    assert unmarshalled_marshalled_model.name == pet_name
    assert unmarshalled_marshalled_model.photoUrls == pet_photo_urls


@pytest.mark.parametrize(
    'deref_value, expected_inherits',
    [
        [{'type': 'object'}, []],
        [{'type': 'object', 'x-model': 'GenericPet'}, ['GenericPet']],
        [{'type': 'object', 'title': 'GenericPet'}, ['GenericPet']],
        [{'type': 'object', 'x-model': 'GenericPet', 'title': 'overridden'}, ['GenericPet']],
    ],
)
def test_create_model_type_properly_extracts_model_name(deref_value, expected_inherits):
    swagger_spec = mock.Mock(
        name='swagger-spec',
        deref=lambda schema: deref_value if is_ref(schema) else schema,
    )
    model_type = create_model_type(
        swagger_spec=swagger_spec,
        model_name='Dog',
        model_spec={
            'type': 'object',
            'title': 'Dog',
            'allOf': [
                {
                    '$ref': '#/definitions/GenericPet',
                },
                {
                    'properties': {
                        'birth_date': {
                            'type': 'string',
                            'format': 'date',
                        },
                    },
                    'required': ['birth_date'],
                },
            ],
        },
    )
    assert model_type._inherits_from == expected_inherits
