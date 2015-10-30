import os

import mock
import simplejson as json
from six.moves.urllib import parse as urlparse

from bravado_core.model import MODEL_MARKER
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


def test_relative_ref_spec():
    #expected_raw_dict, _ = get_spec_json_and_url(
    #    '../../test-data/2.0/simple/swagger.json')
    #expected_dict = Spec.from_dict(expected_raw_dict).spec_dict

    relative_crossref_url = '../../test-data/2.0/simple_crossref/swagger.json'
    crossref_dict, crossref_url = get_spec_json_and_url(relative_crossref_url)
    resultant_spec = Spec.from_dict(crossref_dict, origin_url=crossref_url)

    def delete_key_from_dict(dict_del, key):
        dict_del.pop(key, None)

        for v in dict_del.values():
            if isinstance(v, dict):
                delete_key_from_dict(v, key)
        return dict_del

    # TODO: Make the behavior of x-model consitent for both the specs. Currently
    # it gets populated only for the former. Hence, removing that key from dict
    #delete_key_from_dict(expected_dict, MODEL_MARKER)
    #assert expected_dict == json.loads(json.dumps(resultant_spec.spec_dict))
    print json.dumps(resultant_spec.spec_dict, indent=2)
    # TODO: poke around and verify the dom


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
                        MODEL_MARKER: 'Pet',
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
