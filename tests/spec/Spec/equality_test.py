# -*- coding: utf-8 -*-
import pytest

from bravado_core.spec import Spec
from tests.conftest import get_url


def test_equality_of_the_same_object_returns_True(petstore_spec):
    assert petstore_spec.is_equal(petstore_spec)


def test_equality_of_different_instances_returns_True_if_the_specs_are_the_same(petstore_spec, petstore_dict, petstore_abspath):
    other_petstore_spec_instance = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    assert petstore_spec.is_equal(other_petstore_spec_instance)


@pytest.mark.parametrize('attribute_value', [None, 42])
def test_equality_of_different_instances_returns_False_if_attributes_are_not_matching(
    petstore_spec, petstore_dict, petstore_abspath, attribute_value,
):
    other_petstore_spec_instance = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    setattr(other_petstore_spec_instance, 'a-new-attribute', attribute_value)
    assert not petstore_spec.is_equal(other_petstore_spec_instance)


def test_equality_of_different_instances_returns_False_if_the_specs_are_the_different(petstore_spec, polymorphic_spec):
    assert not petstore_spec.is_equal(polymorphic_spec)


def test_spec_hashability(petstore_spec):
    # The test wants to ensure that a Spec instance is hashable.
    # If calling hash does not throw an exception than we've validated the assumption
    hash(petstore_spec)


def test_equality_checks_for_definitions(petstore_spec, petstore_dict, petstore_abspath):
    petstore_dict['definitions']['new_model'] = {'type': 'object'}
    other_petstore_spec_instance = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    assert not petstore_spec.is_equal(other_petstore_spec_instance)


def test_equality_checks_for_resources(petstore_spec, petstore_dict, petstore_abspath):
    petstore_dict['paths']['/new/path'] = {
        'get': {
            'responses': {
                'default': {'description': ''},
            },
        },
    }
    other_petstore_spec_instance = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    assert not petstore_spec.is_equal(other_petstore_spec_instance)


@pytest.mark.parametrize('internally_dereference_refs', [True, False])
def test_equality_of_specs_with_recursive_definition(minimal_swagger_dict, minimal_swagger_abspath, internally_dereference_refs):
    minimal_swagger_dict['definitions']['recursive_definition'] = {
        'type': 'object',
        'properties': {
            'property': {
                '$ref': '#/definitions/recursive_definition',
            },
        },
    }

    def new_spec():
        return Spec.from_dict(
            spec_dict=minimal_swagger_dict,
            origin_url=get_url(minimal_swagger_abspath),
            config={'internally_dereference_refs': internally_dereference_refs},
        )

    assert new_spec().is_equal(new_spec())


@pytest.mark.parametrize(
    '__dict__',
    [
        {'resources': []},
        {'resources': {'tag': None}},
        {'definitions': []},
        {'definitions': {'model': Exception}},
    ],
)
def test_equality_early_exit(
    minimal_swagger_dict, minimal_swagger_abspath, __dict__,
):
    # This test is mostly meant to ensure that early exit points of Spec.is_equal are triggered during tests.
    minimal_swagger_dict['definitions'] = {'model': {'type': 'object'}}
    minimal_swagger_dict['paths']['/new/path'] = {
        'get': {
            'responses': {
                'default': {'description': ''},
            },
            'tags': ['tag'],
        },
    }
    spec = Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath))
    other_spec = Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath))
    other_spec.__dict__.update(__dict__)
    assert not spec.is_equal(other_spec)
