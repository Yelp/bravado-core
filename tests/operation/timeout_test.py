from mock import sentinel

from bravado_core.resource import build_resources
from bravado_core.spec import Spec


def test_no_timeout(petstore_dict):
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is None


def test_timeout_in_root(petstore_dict):
    petstore_dict['x-timeout'] = sentinel.timeout
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is sentinel.timeout


def test_timeout_in_resource(petstore_dict):
    petstore_dict['paths']['/pet/findByStatus']['x-timeout'] = sentinel.timeout
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is sentinel.timeout


def test_timeout_in_method(petstore_dict):
    petstore_dict['paths']['/pet/findByStatus']['get']['x-timeout'] = sentinel.timeout
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is sentinel.timeout


def test_timeout_in_resource_overrides_root(petstore_dict):
    petstore_dict['x-timeout'] = sentinel.timeout
    petstore_dict['paths']['/pet/findByStatus']['x-timeout'] = sentinel.another_timeout
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is sentinel.another_timeout


def test_timeout_in_method_overrides_root(petstore_dict):
    petstore_dict['x-timeout'] = sentinel.timeout
    petstore_dict['paths']['/pet/findByStatus']['get']['x-timeout'] = sentinel.another_timeout
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is sentinel.another_timeout


def test_timeout_in_method_overrides_resource_and_root(petstore_dict):
    petstore_dict['x-timeout'] = sentinel.timeout
    petstore_dict['paths']['/pet/findByStatus']['x-timeout'] = sentinel.another_timeout
    petstore_dict['paths']['/pet/findByStatus']['get']['x-timeout'] = sentinel.another_another_timeout
    resources = build_resources(Spec(petstore_dict))
    assert resources['pet'].findPetsByStatus.timeout is sentinel.another_another_timeout
