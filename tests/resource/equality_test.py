# -*- coding: utf-8 -*-
import pytest

from bravado_core.spec import Spec
from tests.conftest import get_url


@pytest.fixture
def petPetstoreResource(petstore_spec):
    return petstore_spec.resources['pet']


def test_equality_of_the_same_object_returns_True(petPetstoreResource):
    assert petPetstoreResource == petPetstoreResource


def test_equality_of_different_instances_returns_True_if_the_specs_are_the_same(
    petPetstoreResource, petstore_dict, petstore_abspath,
):
    other_petstore_spec = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    other_petPetstoreResource = other_petstore_spec.resources['pet']
    assert petPetstoreResource == other_petPetstoreResource


def test_equality_of_different_instances_returns_False_if_the_specs_are_the_different(petstore_spec, petPetstoreResource):
    assert petPetstoreResource != petstore_spec.resources['user']
