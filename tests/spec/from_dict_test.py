import os

import mock
import simplejson as json
from six.moves.urllib import parse as urlparse

from bravado_core.spec import Spec


def test_definitions_not_present(minimal_swagger_dict):
    del minimal_swagger_dict['definitions']
    spec = Spec.from_dict(minimal_swagger_dict)
    assert 0 == len(spec.definitions)


@mock.patch('jsonref.JsonRef')
@mock.patch('bravado_core.spec.replace_jsonref_proxies')
@mock.patch.object(Spec, 'build')
def test_origin_uri_gets_passed_to_jsonref(mock_build, mock_prox, mock_ref,
                                           minimal_swagger_dict):
    Spec.from_dict(minimal_swagger_dict, origin_url='file:///foo')
    mock_ref.replace_refs.assert_called_once_with(
        minimal_swagger_dict, base_uri='file:///foo')


def get_spec_json_and_url(rel_url):
    my_dir = os.path.abspath(os.path.dirname(__file__))
    abs_path = os.path.join(my_dir, rel_url)
    with open(abs_path) as f:
        return json.loads(f.read()), urlparse.urljoin('file:', abs_path)


def test_relative_ref_spec():
    expected_raw_dict, _ = get_spec_json_and_url(
        '../../test-data/2.0/simple/swagger.json')
    expected_dict = Spec.from_dict(expected_raw_dict).spec_dict

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
    delete_key_from_dict(expected_dict, 'x-model')
    assert expected_dict == json.loads(json.dumps(resultant_spec.spec_dict))


def test_ref_to_external_path_with_ref_to_local_model():
    # Test that an an external ref to a path (in swagger.json) which contains
    # a local ref to a model (in pet.json) works as expected:
    # - model type for Pet is created
    # - de-reffed spec_dict contains 'x-model' annotations
    my_dir = os.path.abspath(os.path.dirname(__file__))

    swagger_json_path = os.path.join(
        my_dir,
        '../../test-data/2.0/x-model/swagger.json')

    with open(swagger_json_path) as f:
        swagger_json_content = json.loads(f.read())

    swagger_json_url = urlparse.urljoin('file:', swagger_json_path)
    spec = Spec.from_dict(swagger_json_content, swagger_json_url)

    assert spec.definitions['Pet']
    assert spec.spec_dict['paths']['/pet']['get']['responses']['200'][
        'schema']['x-model'] == 'Pet'
