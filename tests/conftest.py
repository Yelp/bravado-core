# -*- coding: utf-8 -*-
import os
from copy import deepcopy
from itertools import chain

import pytest
import simplejson as json
import yaml
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from six import iteritems
from six import iterkeys
from six.moves.urllib import parse as urlparse
from six.moves.urllib.request import pathname2url
from six.moves.urllib.request import url2pathname
from swagger_spec_validator.common import SwaggerValidationWarning

from bravado_core.spec import CONFIG_DEFAULTS
from bravado_core.spec import Spec


@pytest.fixture
def mock_spec():
    m = Mock(spec=Spec)
    m.config = deepcopy(CONFIG_DEFAULTS)
    return m


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
    return urlparse.urljoin('file:', pathname2url(absolute_path))


def get_url_path(absolute_url):
    return url2pathname(urlparse.urlparse(absolute_url).path)


@pytest.fixture
def my_dir():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def minimal_swagger_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'minimal_swagger', 'swagger.json')


@pytest.fixture
def minimal_swagger_dict(minimal_swagger_abspath):
    """Return minimal dict that respresents a swagger spec - useful as a base
    template.
    """
    return _read_json(minimal_swagger_abspath)


@pytest.fixture
def minimal_swagger_spec(minimal_swagger_dict, minimal_swagger_abspath):
    return Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath))


@pytest.fixture
def composition_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'composition', 'swagger.json')


@pytest.fixture
def composition_dict(composition_abspath):
    return _read_json(composition_abspath)


@pytest.fixture(
    params=[
        {'include_missing_properties': True},
        {'include_missing_properties': False},
    ],
)
def composition_spec(request, composition_dict, composition_abspath):
    return Spec.from_dict(composition_dict, origin_url=get_url(composition_abspath), config=request.param)


@pytest.fixture
def multi_file_recursive_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'multi-file-recursive', 'swagger.json')


@pytest.fixture
def multi_file_recursive_dict(multi_file_recursive_abspath):
    return _read_yaml(multi_file_recursive_abspath)


@pytest.fixture
def multi_file_recursive_spec(multi_file_recursive_dict, multi_file_recursive_abspath):
    return Spec.from_dict(multi_file_recursive_dict, origin_url=get_url(multi_file_recursive_abspath))


@pytest.fixture
def flattened_multi_file_recursive_abspath(my_dir):
    return os.path.join(
        os.path.dirname(my_dir),
        'test-data', '2.0', 'multi-file-recursive', 'flattened-multi-file-recursive-spec.json',
    )


@pytest.fixture
def flattened_multi_file_recursive_dict(flattened_multi_file_recursive_abspath):
    return _read_json(flattened_multi_file_recursive_abspath)


@pytest.fixture
def petstore_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'petstore', 'swagger.json')


@pytest.fixture
def petstore_dict(petstore_abspath):
    return _read_json(petstore_abspath)


@pytest.fixture
def petstore_spec(petstore_dict, petstore_abspath):
    return Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))


@pytest.fixture
def getPetByIdPetstoreOperation(petstore_spec):
    return petstore_spec.resources['pet'].operations['getPetById']


@pytest.fixture
def polymorphic_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'polymorphic_specs', 'swagger.json')


@pytest.fixture
def polymorphic_dict(polymorphic_abspath):
    return _read_json(polymorphic_abspath)


@pytest.fixture
def polymorphic_spec(polymorphic_dict):
    return Spec.from_dict(polymorphic_dict)


@pytest.fixture
def security_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'security', 'swagger.json')


@pytest.fixture
def security_dict(security_abspath):
    return _read_json(security_abspath)


@pytest.fixture
def security_spec(security_dict):
    return Spec.from_dict(security_dict)


@pytest.fixture
def multi_file_with_no_xmodel_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'multi-file-specs-with-no-x-model', 'swagger.json')


@pytest.fixture
def multi_file_with_no_xmodel_dict(multi_file_with_no_xmodel_abspath):
    return _read_json(multi_file_with_no_xmodel_abspath)


@pytest.fixture
def multi_file_with_no_xmodel_spec(multi_file_with_no_xmodel_dict, multi_file_with_no_xmodel_abspath):
    return Spec.from_dict(multi_file_with_no_xmodel_dict, origin_url=get_url(multi_file_with_no_xmodel_abspath))


@pytest.fixture
def flattened_multi_file_with_no_xmodel_abspath(my_dir):
    return os.path.join(
        os.path.dirname(my_dir),
        'test-data', '2.0', 'multi-file-specs-with-no-x-model', 'flattened-multi-file-with-no-xmodel.json',
    )


@pytest.fixture
def flattened_multi_file_with_no_xmodel_dict(flattened_multi_file_with_no_xmodel_abspath):
    return _read_json(flattened_multi_file_with_no_xmodel_abspath)


@pytest.fixture
def simple_crossfer_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'simple_crossref', 'swagger.json')


@pytest.fixture
def simple_crossfer_dict(simple_crossfer_abspath):
    return _read_json(simple_crossfer_abspath)


@pytest.fixture
def simple_crossfer_spec(simple_crossfer_dict, simple_crossfer_abspath):
    return Spec.from_dict(simple_crossfer_dict, origin_url=get_url(simple_crossfer_abspath))


@pytest.fixture
def specs_with_none_in_ref_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'specs-with-None-in-ref', 'swagger.json')


@pytest.fixture
def specs_with_none_in_ref_dict(specs_with_none_in_ref_abspath):
    return _read_json(specs_with_none_in_ref_abspath)


@pytest.fixture
def specs_with_none_in_ref_spec(specs_with_none_in_ref_dict, specs_with_none_in_ref_abspath):
    with pytest.warns(SwaggerValidationWarning):
        return Spec.from_dict(specs_with_none_in_ref_dict, origin_url=get_url(specs_with_none_in_ref_abspath))


@pytest.fixture
def flattened_specs_with_none_in_ref_abspath(my_dir):
    return os.path.join(os.path.dirname(my_dir), 'test-data', '2.0', 'specs-with-None-in-ref', 'flattened.json')


@pytest.fixture
def flattened_specs_with_none_in_ref_dict(flattened_specs_with_none_in_ref_abspath):
    return _read_json(flattened_specs_with_none_in_ref_abspath)


@pytest.fixture
def node_spec():
    """Used in tests that have recursive $refs
    """
    return {
        'type': 'object',
        'properties': {
            'date': {
                'type': 'string',
                'format': 'date',
            },
            'name': {
                'type': 'string',
            },
            'child': {
                '$ref': '#/definitions/Node',
            },
        },
        'required': ['name'],
    }


@pytest.fixture
def recursive_swagger_spec(minimal_swagger_dict, node_spec):
    """
    Return a swager_spec with a #/definitions/Node that is
    recursive.
    """
    minimal_swagger_dict['definitions']['Node'] = node_spec
    return Spec(minimal_swagger_dict)


def check_object_deepcopy(obj):
    """
    This is an helper method that ensures that the deepcopy of the input object does actually returns
    an equivalent instance (via equality, __eq__) and that the copied object and related properties are
    pointing to different objects (different ids).

    NOTE: This method does work not really work well for all the possible types (ie. passing `str` in here would cause issue)
          but it's good enough to check deep-copyability of custom object types (ie. class Something(object): ...)

    :returns: deepcopy ob obj
    """

    obj_copy = deepcopy(obj)

    assert isinstance(obj_copy, obj.__class__)
    assert obj.is_equal(obj_copy)

    # Ideally, if we deep copied properly an object we should have
    # * different memory allocation of the object
    # * different memory allocation of all the object attributes
    # NOTE: A deep copy can map to the same memory location in case the type is immutable (ie. NoneType, str, tuple)
    assert id(obj) != id(obj_copy)
    attributes_with_same_id = {
        attr_name: getattr(obj_copy, attr_name, None)
        for attr_name in set(
            chain(
                iterkeys(obj.__dict__),
                iterkeys(obj_copy.__dict__),
            ),
        )
        if id(getattr(obj, attr_name, None)) == id(getattr(obj_copy, attr_name, None))
    }
    assert not any(
        # If `attr_name: attr_value` is in attributes_with_same_id then attr_value id did not change
        # after deepcopy. As immutable types do not create new instances for deepcopy we need to ensure
        # that all the occurrences of "same-id" are related to immutable types.
        not isinstance(attr_value, (type(None), str, tuple))
        for attr_name, attr_value in iteritems(attributes_with_same_id)
    )

    return obj_copy
