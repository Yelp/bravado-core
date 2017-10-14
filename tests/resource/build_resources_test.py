# -*- coding: utf-8 -*-
import pytest

from bravado_core.param import Param
from bravado_core.resource import build_resources
from bravado_core.spec import Spec


def test_empty():
    spec_dict = {'paths': {}}
    spec = Spec(spec_dict)
    assert {} == build_resources(spec)


def test_resource_with_a_single_operation_associated_by_tag(paths_spec):
    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['pet'].findPetsByStatus


def test_resource_with_a_single_operation_associated_by_path_name(paths_spec):
    # rename path so we know resource name will not be 'pet'
    paths_spec['/foo/findByStatus'] = paths_spec['/pet/findByStatus']
    del paths_spec['/pet/findByStatus']

    # remove tags on operation so path name is used to assoc with a resource
    del paths_spec['/foo/findByStatus']['get']['tags']

    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['foo'].findPetsByStatus


def test_many_resources_with_the_same_operation_cuz_multiple_tags(paths_spec):
    tags = ['foo', 'bar', 'baz', 'bing', 'boo']
    paths_spec['/pet/findByStatus']['get']['tags'] = tags
    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert len(tags) == len(resources)
    for tag in tags:
        assert resources[tag].findPetsByStatus


def test_resource_with_shared_parameters(paths_spec):
    # insert a shared parameter into the spec
    shared_parameter = {
        'name': 'filter',
        'in': 'query',
        'description': 'Filter the pets by attribute',
        'required': False,
        'type': 'string',
    }
    paths_spec['/pet/findByStatus']['parameters'] = [shared_parameter]
    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    # verify shared param associated with operation
    assert isinstance(
        resources['pet'].findPetsByStatus.params['filter'], Param)


def test_resource_with_vendor_extension(paths_spec):
    """Make sure vendor extensions are ignored."""
    paths_spec['/pet/findByStatus']['x-foo'] = 'bar'
    spec_dict = {'paths': paths_spec}
    resources = build_resources(Spec(spec_dict))
    assert 1 == len(resources)
    assert resources['pet'].findPetsByStatus


@pytest.mark.parametrize(
    'internally_dereference_refs', [True, False],
)
def test_refs(minimal_swagger_dict, paths_spec, pet_spec, internally_dereference_refs):
    minimal_swagger_dict['paths'] = paths_spec
    minimal_swagger_dict['definitions'] = {'Pet': pet_spec}
    swagger_spec = Spec(minimal_swagger_dict, config={'internally_dereference_refs': internally_dereference_refs})
    resources = build_resources(swagger_spec)
    assert len(resources) == 1
    assert 'pet' in resources
