# -*- coding: utf-8 -*-
from bravado_core.spec import Spec
from tests.conftest import get_url


def test_equality_of_the_same_object_returns_True(petstore_spec):
    assert petstore_spec == petstore_spec


def test_equality_of_different_instances_returns_True_if_the_specs_are_the_same(petstore_spec, petstore_dict, petstore_abspath):
    other_petstore_spec_instance = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    assert petstore_spec == other_petstore_spec_instance


def test_equality_of_different_instances_returns_False_if_the_specs_are_the_different(petstore_spec, polymorphic_spec):
    assert petstore_spec != polymorphic_spec
