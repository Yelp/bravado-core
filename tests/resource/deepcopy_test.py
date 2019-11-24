# -*- coding: utf-8 -*-
import pytest

from tests.conftest import check_object_deepcopy


@pytest.fixture
def pet_resource(petstore_spec):
    return petstore_spec.resources['pet']


def test_resource_instance_is_deep_copyable(pet_resource):
    check_object_deepcopy(pet_resource)
