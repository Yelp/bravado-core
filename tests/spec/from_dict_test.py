# -*- coding: utf-8 -*-
import os

import pytest
import simplejson as json
import yaml

from bravado_core.response import get_response_spec
from bravado_core.spec import Spec
from tests.conftest import _read_json
from tests.conftest import get_url


def test_definitions_not_present(minimal_swagger_dict):
    del minimal_swagger_dict['definitions']
    spec = Spec.from_dict(minimal_swagger_dict)
    assert 0 == len(spec.definitions)


def test_complicated_refs(simple_crossfer_spec):
    # Split the swagger spec into a bunch of different json files and use
    # $refs all over to place to wire stuff together - see the test-data
    # files or this will make no sense whatsoever.

    # Verify things are 'reachable' (hence, have been ingested correctly)

    # Resource
    assert simple_crossfer_spec.resources['pingpong']

    # Operation
    op = simple_crossfer_spec.resources['pingpong'].ping
    assert op

    # Parameter
    assert simple_crossfer_spec.resources['pingpong'].ping.params['pung']

    # Parameter name
    assert simple_crossfer_spec.resources['pingpong'].ping.params['pung'].name == 'pung'

    # Response
    response = get_response_spec(200, op)
    assert response['description'] == 'pong'


def test_ref_to_external_path_with_ref_to_local_model():
    # Test that an an external ref to a path (in swagger.json) which contains
    # a local ref to a model (in pet.json) works as expected:
    # - model type for Pet is created
    # - de-reffed spec_dict contains 'x-model' annotations
    #
    # This is really a test for `tag_models`. Migrate over there
    #
    # swagger.json
    #   paths:
    #     /pet:
    #       $ref: pet.json#/paths/pet   (1)
    #
    # pet.json
    #   definitions:
    #     Pet: ...                      (4)
    #   paths:                          (2)
    #      ...
    #      $ref: #/definitions/Pet      (3)
    #
    my_dir = os.path.abspath(os.path.dirname(__file__))

    swagger_json_path = os.path.join(
        os.path.dirname(os.path.dirname(my_dir)),
        'test-data', '2.0', 'x-model', 'swagger.json')

    with open(swagger_json_path) as f:
        swagger_json_content = json.loads(f.read())

    swagger_json_url = get_url(swagger_json_path)
    spec = Spec.from_dict(swagger_json_content, swagger_json_url)
    assert 'Pet' in spec.definitions


def test_yaml_files(my_dir):
    swagger_yaml_path = os.path.join(
        os.path.dirname(my_dir),
        'test-data', '2.0', 'yaml', 'swagger.yml',
    )

    with open(swagger_yaml_path) as f:
        swagger_yaml_content = yaml.load(f)

    swagger_yaml_url = get_url(swagger_yaml_path)
    spec = Spec.from_dict(swagger_yaml_content, swagger_yaml_url)
    assert 'Pet' in spec.definitions


def test_spec_with_dereffed_and_tagged_models_works(minimal_swagger_dict):
    # In cases where the Swagger spec being ingested has already been de-reffed
    # and had models tagged with 'x-model', we still need to be able to
    # detect them and make them available as model types. For example, a spec
    # ingested via http from pyramid_swagger contains de-reffed models.
    pet_path_spec = {
        'get': {
            'responses': {
                '200': {
                    'description': 'Returns a Pet',
                    'schema': {
                        'x-model': 'Pet',
                        'type': 'object',
                        'properties': {
                            'name': {
                                'type': 'string'
                            }
                        }
                    }
                }
            }
        }
    }
    minimal_swagger_dict['paths']['/pet'] = pet_path_spec
    spec = Spec.from_dict(minimal_swagger_dict)
    assert spec.definitions['Pet']


@pytest.fixture
def multi_file_multi_directory_abspath(my_dir):
    return os.path.join(
        os.path.dirname(my_dir),
        'test-data', '2.0', 'multi-file-multi-directory-spec', 'swagger.yaml',
    )


@pytest.fixture
def multi_file_multi_directory_dict(multi_file_multi_directory_abspath):
    with open(multi_file_multi_directory_abspath) as f:
        return yaml.safe_load(f)


@pytest.fixture
def flattened_multi_file_multi_directory_abspath(my_dir):
    return os.path.join(
        os.path.dirname(my_dir),
        'test-data', '2.0', 'multi-file-multi-directory-spec', 'flattened-multi-file-multi-directory-spec.json',
    )


@pytest.fixture
def flattened_multi_file_multi_directory_dict(flattened_multi_file_multi_directory_abspath):
    return _read_json(flattened_multi_file_multi_directory_abspath)


@pytest.fixture(
    params=[False, True],
    ids=['with-references', 'fully-dereferenced'],
)
def multi_file_multi_directory_spec(request, multi_file_multi_directory_dict, multi_file_multi_directory_abspath):
    return Spec.from_dict(
        multi_file_multi_directory_dict,
        origin_url=get_url(multi_file_multi_directory_abspath),
        config={'internally_dereference_refs': request.param},
    )


def test_flattened_multi_file_multi_directory_specs(
    multi_file_multi_directory_spec, flattened_multi_file_multi_directory_dict,
):
    assert multi_file_multi_directory_spec.flattened_spec == flattened_multi_file_multi_directory_dict

    # Ensure that flattened_spec is a valid swagger spec
    try:
        Spec.from_dict(multi_file_multi_directory_spec.flattened_spec)
    except Exception as e:
        pytest.fail('Unexpected exception: {e}'.format(e=e), e.__traceback__)


def test_swagger_spec_in_operation_is_the_swagger_spec_that_contains_the_operation(multi_file_multi_directory_spec):
    """
    The objective of this test is to guarantee that bravado_core.spec.Spec object referenced by
    operation objects is the same object that contains the resources that points to the operation

    Referencing to the same object means that they share the same memory space

    More details about the issue that we want to prevent with this tests are available on
    https://github.com/Yelp/bravado-core/issues/275
    """
    def first(_iterable):
        return next(iter(_iterable))
    resource = first(multi_file_multi_directory_spec.resources.values())
    operation = first(resource.operations.values())
    assert id(operation.swagger_spec) == id(multi_file_multi_directory_spec)
