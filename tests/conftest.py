# -*- coding: utf-8 -*-
import base64
import os

import pytest
import simplejson as json
import yaml
from six.moves.urllib import parse as urlparse

import bravado_core.formatter
from bravado_core.spec import Spec


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})


def _read_json(json_path):
    with open(json_path) as f:
        return json.loads(f.read())


def _read_yaml(json_path):
    with open(json_path) as f:
        return yaml.safe_load(f)


def get_url(absolute_path):
    return urlparse.urljoin('file:', absolute_path)


@pytest.fixture
def my_dir():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def minimal_swagger_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/minimal_swagger/swagger.json')


@pytest.fixture
def minimal_swagger_dict(minimal_swagger_abspath):
    """Return minimal dict that respresents a swagger spec - useful as a base
    template.
    """
    return _read_json(minimal_swagger_abspath)


@pytest.fixture
def minimal_swagger_spec(minimal_swagger_dict):
    return Spec.from_dict(minimal_swagger_dict)


@pytest.fixture
def composition_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/composition/swagger.json')


@pytest.fixture
def composition_dict(composition_abspath):
    return _read_json(composition_abspath)


@pytest.fixture(params=[
    {'include_missing_properties': True},
    {'include_missing_properties': False},
])
def composition_spec(request, composition_dict, composition_abspath):
    return Spec.from_dict(composition_dict, origin_url=get_url(composition_abspath), config=request.param)


@pytest.fixture
def multi_file_recursive_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/multi-file-recursive/swagger.json')


@pytest.fixture
def multi_file_recursive_dict(multi_file_recursive_abspath):
    return _read_yaml(multi_file_recursive_abspath)


@pytest.fixture
def multi_file_recursive_spec(multi_file_recursive_dict, multi_file_recursive_abspath):
    return Spec.from_dict(multi_file_recursive_dict, origin_url=get_url(multi_file_recursive_abspath))


@pytest.fixture
def flattened_multi_file_recursive_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/multi-file-recursive/flattened-multi-file-recursive-spec.json')


@pytest.fixture
def flattened_multi_file_recursive_dict(flattened_multi_file_recursive_abspath):
    return _read_json(flattened_multi_file_recursive_abspath)


@pytest.fixture
def petstore_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/petstore/swagger.json')


@pytest.fixture
def petstore_dict(petstore_abspath):
    return _read_json(petstore_abspath)


@pytest.fixture
def petstore_spec(petstore_dict, petstore_abspath):
    return Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))


@pytest.fixture
def polymorphic_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/polymorphic_specs/swagger.json')


@pytest.fixture
def polymorphic_dict(polymorphic_abspath):
    return _read_json(polymorphic_abspath)


@pytest.fixture
def polymorphic_spec(polymorphic_dict):
    return Spec.from_dict(polymorphic_dict)


@pytest.fixture
def security_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/security/swagger.json')


@pytest.fixture
def security_dict(security_abspath):
    return _read_json(security_abspath)


@pytest.fixture
def security_spec(security_dict):
    return Spec.from_dict(security_dict)


@pytest.fixture
def multi_file_with_no_xmodel_abspath(my_dir):
    return os.path.join(my_dir, '../test-data/2.0/multi-file-specs-with-no-x-model/swagger.json')


@pytest.fixture
def multi_file_with_no_xmodel_dict(multi_file_with_no_xmodel_abspath):
    return _read_json(multi_file_with_no_xmodel_abspath)


@pytest.fixture
def multi_file_with_no_xmodel_spec(multi_file_with_no_xmodel_dict, multi_file_with_no_xmodel_abspath):
    return Spec.from_dict(multi_file_with_no_xmodel_dict, origin_url=get_url(multi_file_with_no_xmodel_abspath))


@pytest.fixture
def flattened_multi_file_with_no_xmodel_abspath(my_dir):
    return os.path.join(
        my_dir,
        '../test-data/2.0/multi-file-specs-with-no-x-model/flattened-multi-file-with-no-xmodel.json',
    )


@pytest.fixture
def flattened_multi_file_with_no_xmodel_dict(flattened_multi_file_with_no_xmodel_abspath):
    return _read_json(flattened_multi_file_with_no_xmodel_abspath)


def del_base64():
    del bravado_core.formatter.DEFAULT_FORMATS['base64']


@pytest.fixture
def base64_format():
    return bravado_core.formatter.SwaggerFormat(
        format='base64',
        to_wire=base64.b64encode,
        to_python=base64.b64decode,
        validate=base64.b64decode,
        description='Base64',
    )


@pytest.fixture(scope='function')
def register_base64_format(base64_format, request):
    request.addfinalizer(del_base64)
    bravado_core.formatter.register_format(base64_format)


@pytest.fixture
def node_spec():
    """Used in tests that have recursive $refs
    """
    return {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            },
            'child': {
                '$ref': '#/definitions/Node',
            },
        },
        'required': ['name']
    }


@pytest.fixture
def recursive_swagger_spec(minimal_swagger_dict, node_spec):
    """
    Return a swager_spec with a #/definitions/Node that is
    recursive.
    """
    minimal_swagger_dict['definitions']['Node'] = node_spec
    return Spec(minimal_swagger_dict)
