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
