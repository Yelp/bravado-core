# -*- coding: utf-8 -*-
import pytest


@pytest.fixture
def pet_spec():
    # The '#/definitions' dict from spec
    return {
        'properties': {
            'name': {
                'type': 'string'
            },
        },
        'required': [
            'name'
        ],
        'type': 'object',
    }


@pytest.fixture
def paths_spec():
    # The '#/paths' dict from a spec
    return {
        "/pet/findByStatus": {
            "get": {
                "tags": [
                    "pet"
                ],
                "summary": "Finds Pets by status",
                "description": "Multiple status values can be provided with comma seperated strings",  # noqa
                "operationId": "findPetsByStatus",
                "produces": [
                    "application/json",
                    "application/xml"
                ],
                "parameters": [
                    {
                        "name": "status",
                        "in": "query",
                        "description": "Status values that need to be considered for filter",  # noqa
                        "required": False,
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "collectionFormat": "multi",
                        "default": "available"
                    }
                ],
                "responses": {
                    "200": {
                        "description": "successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/Pet"
                            }
                        }
                    },
                    "400": {
                        "description": "Invalid status value"
                    }
                }
            }
        },
    }


@pytest.fixture
def find_by_status_path_spec(paths_spec):
    return paths_spec['/pet/findByStatus']
