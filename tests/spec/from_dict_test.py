# -*- coding: utf-8 -*-
import os

import simplejson as json
import yaml
from six.moves.urllib import parse as urlparse

from bravado_core.response import get_response_spec
from bravado_core.spec import Spec


def test_definitions_not_present(minimal_swagger_dict):
    del minimal_swagger_dict['definitions']
    spec = Spec.from_dict(minimal_swagger_dict)
    assert 0 == len(spec.definitions)


def get_spec_json_and_url(rel_url):
    my_dir = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(my_dir, rel_url)
    with open(abs_path) as f:
        return json.loads(f.read()), urlparse.urljoin('file:', abs_path)


def test_complicated_refs():
    # Split the swagger spec into a bunch of different json files and use
    # $refs all over to place to wire stuff together - see the test-data
    # files or this will make no sense whatsoever.
    file_path = '../../test-data/2.0/simple_crossref/swagger.json'
    swagger_dict, origin_url = get_spec_json_and_url(file_path)
    swagger_spec = Spec.from_dict(swagger_dict, origin_url=origin_url)

    # Verify things are 'reachable' (hence, have been ingested correctly)

    # Resource
    assert swagger_spec.resources['pingpong']

    # Operation
    op = swagger_spec.resources['pingpong'].ping
    assert op

    # Parameter
    assert swagger_spec.resources['pingpong'].ping.params['pung']

    # Parameter name
    assert swagger_spec.resources['pingpong'].ping.params['pung'].name == 'pung'

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
        my_dir,
        '../../test-data/2.0/x-model/swagger.json')

    with open(swagger_json_path) as f:
        swagger_json_content = json.loads(f.read())

    swagger_json_url = urlparse.urljoin('file:', swagger_json_path)
    spec = Spec.from_dict(swagger_json_content, swagger_json_url)
    assert 'Pet' in spec.definitions


def test_yaml_files():
    my_dir = os.path.abspath(os.path.dirname(__file__))

    swagger_yaml_path = os.path.join(
        my_dir,
        '../../test-data/2.0/yaml/swagger.yml')

    with open(swagger_yaml_path) as f:
        swagger_yaml_content = yaml.load(f)

    swagger_yaml_url = urlparse.urljoin('file:', swagger_yaml_path)
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
