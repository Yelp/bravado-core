# -*- coding: utf-8 -*-
import pytest

from bravado_core.spec import Spec
from tests.conftest import get_url


def test_equality_of_the_same_object_returns_True(getPetByIdPetstoreOperation):
    assert getPetByIdPetstoreOperation.is_equal(getPetByIdPetstoreOperation)


def test_equality_of_different_instances_returns_True_if_the_specs_are_the_same(
    getPetByIdPetstoreOperation, petstore_dict, petstore_abspath,
):
    other_petstore_spec = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    other_getPetByIdPetstoreOperation = other_petstore_spec.resources['pet'].operations['getPetById']
    assert getPetByIdPetstoreOperation.is_equal(other_getPetByIdPetstoreOperation)


def test_equality_of_different_instances_returns_False_if_the_specs_are_the_different(petstore_spec, getPetByIdPetstoreOperation):
    assert not getPetByIdPetstoreOperation.is_equal(petstore_spec.resources['pet'].operations['addPet'])


def test_equality_of_different_instances_returns_False_if_different_types(getPetByIdPetstoreOperation):
    assert not getPetByIdPetstoreOperation.is_equal(None)


def test_operation_hashability(getPetByIdPetstoreOperation):
    # The test wants to ensure that a Operation instance is hashable.
    # If calling hash does not throw an exception than we've validated the assumption
    hash(getPetByIdPetstoreOperation)


@pytest.mark.parametrize('ignore_swagger_spec', [True, False])
def test_equality_honors_ignore_swagger_spec_parameters(
    getPetByIdPetstoreOperation, petstore_dict, petstore_abspath, ignore_swagger_spec,
):
    other_petstore_spec = Spec.from_dict(petstore_dict, origin_url=get_url(petstore_abspath))
    other_getPetByIdPetstoreOperation = other_petstore_spec.resources['pet'].operations['getPetById']
    other_getPetByIdPetstoreOperation.swagger_spec = None
    assert getPetByIdPetstoreOperation.is_equal(
        other_getPetByIdPetstoreOperation, ignore_swagger_spec=ignore_swagger_spec,
    ) is ignore_swagger_spec
