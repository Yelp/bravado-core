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
