import base64
import os
import simplejson as json
from six.moves.urllib import parse as urlparse

import pytest

import bravado_core.formatter
from bravado_core.spec import Spec


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})


@pytest.fixture
def minimal_swagger_dict():
    """Return minimal dict that respresents a swagger spec - useful as a base
    template.
    """
    return {
        'swagger': '2.0',
        'info': {
            'title': 'Test',
            'version': '1.0',
        },
        'paths': {
        },
        'definitions': {
        },
    }


@pytest.fixture
def minimal_swagger_spec(minimal_swagger_dict):
    return Spec.from_dict(minimal_swagger_dict)


@pytest.fixture
def simple_crossref_abspath():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(my_dir, '../test-data/2.0/simple_crossref/swagger.json')


@pytest.fixture
def simple_crossref_url(simple_crossref_abspath):
    return urlparse.urljoin('file:', simple_crossref_abspath)


@pytest.fixture
def simple_crossref_dict(simple_crossref_abspath):
    with open(simple_crossref_abspath) as f:
        return json.loads(f.read())


@pytest.fixture
def simple_crossref_spec(simple_crossref_dict, simple_crossref_url):
    return Spec.from_dict(simple_crossref_dict, origin_url=simple_crossref_url)


@pytest.fixture
def petstore_dict():
    my_dir = os.path.abspath(os.path.dirname(__file__))
    fpath = os.path.join(my_dir, '../test-data/2.0/petstore/swagger.json')
    with open(fpath) as f:
        return json.loads(f.read())


@pytest.fixture
def petstore_spec(petstore_dict):
    return Spec.from_dict(petstore_dict)


def del_base64():
    del bravado_core.formatter.DEFAULT_FORMATS['base64']


@pytest.fixture
def base64_format():
    return bravado_core.formatter.SwaggerFormat(
        format='base64',
        to_wire=base64.b64encode,
        to_python=base64.b64decode,
        validate=base64.b64decode,
        description='Base64')


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
