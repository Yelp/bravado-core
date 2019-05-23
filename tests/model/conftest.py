# -*- coding: utf-8 -*-
import pytest

from bravado_core.model import create_model_type
from bravado_core.spec import Spec


@pytest.fixture
def definitions_spec():
    return {
        "User": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                },
                "username": {
                    "type": "string",
                },
                "firstName": {
                    "type": "string",
                },
                "lastName": {
                    "type": "string",
                },
                "email": {
                    "type": "string",
                },
                "password": {
                    "type": "string",
                },
                "phone": {
                    "type": "string",
                },
                "userStatus": {
                    "type": "integer",
                    "format": "int32",
                    "description": "User Status",
                },
            },
            "xml": {
                "name": "User",
            },
        },
        "Category": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                },
                "name": {
                    "type": "string",
                },
            },
        },
        "Pet": {
            "required": [
                "name",
                "photoUrls",
            ],
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                },
                "category": {
                    "$ref": "#/definitions/Category",
                },
                "name": {
                    "type": "string",
                    "example": "doggie",
                },
                "photoUrls": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                },
                "tags": {
                    "type": "array",
                    "items": {
                        "$ref": "#/definitions/Tag",
                    },
                },
            },
            "x-model": "Pet",
        },
        "Cat": {
            "allOf": [
                {
                    "$ref": "#/definitions/Pet",
                },
                {
                    "type": "object",
                    "required": ["neutered"],
                    "properties": {
                        "neutered": {
                            "type": "boolean",
                        },
                    },
                },
            ],
        },
        "Tag": {
            "properties": {
                "id": {
                    "type": "integer",
                    "format": "int64",
                },
                "name": {
                    "type": "string",
                },
            },
            "xml": {
                "name": "Tag",
            },
        },
    }


@pytest.fixture
def user_spec(definitions_spec):
    return definitions_spec['User']


@pytest.fixture
def user_type(mock_spec, user_spec):
    """
    :rtype: User
    """
    return create_model_type(mock_spec, 'User', user_spec)


@pytest.fixture
def user(user_type):
    """
    :return: instance of a User
    """
    return user_type()


@pytest.fixture
def tag_model(mock_spec, definitions_spec):
    tag_spec = definitions_spec['Tag']
    return create_model_type(mock_spec, 'Tag', tag_spec)


@pytest.fixture
def pet_spec(definitions_spec):
    return definitions_spec['Pet']


@pytest.fixture
def pet_type(cat_swagger_spec, pet_spec):
    return create_model_type(cat_swagger_spec, 'Pet', pet_spec)


@pytest.fixture
def cat_spec(definitions_spec):
    return definitions_spec['Cat']


@pytest.fixture
def cat_swagger_spec(minimal_swagger_dict, definitions_spec):
    minimal_swagger_dict['definitions'] = definitions_spec
    return Spec.from_dict(minimal_swagger_dict)


@pytest.fixture
def cat_type(cat_swagger_spec, cat_spec):
    return create_model_type(cat_swagger_spec, 'Cat', cat_spec)


@pytest.fixture
def cat(cat_type):
    return cat_type()


@pytest.fixture
def cat_kwargs():
    return {
        'id': 12,
        'category': {
            'id': 42,
            'name': 'Feline',
        },
        'name': 'Oskar',
        'photoUrls': ['example.com/img1', 'example.com/img2'],
        'tags': [
            {
                'id': 1,
                'name': 'cute',
            },
        ],
        'neutered': True,
    }


@pytest.fixture
def user_kwargs():
    return {
        'firstName': 'Darwin',
        'userStatus': 9,
        'id': 999,
    }
