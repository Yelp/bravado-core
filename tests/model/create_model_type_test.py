# -*- coding: utf-8 -*-
import mock

from bravado_core.model import create_model_type
from tests.model.conftest import \
    definitions_spec as definitions_spec_fixture
from tests.model.conftest import pet_spec as pet_spec_fixture


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
def test_create_model_type_lazy_docstring(mock_create_docstring,
                                          empty_swagger_spec):
    # NOTE: some sort of weird interaction with pytest, pytest-mock and mock
    #       made using the 'mocker' fixture here a no-go.
    definitions_spec = definitions_spec_fixture()
    pet_spec = pet_spec_fixture(definitions_spec)
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
