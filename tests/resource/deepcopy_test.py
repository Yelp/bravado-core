# -*- coding: utf-8 -*-
import sys

import pytest

from tests.conftest import check_object_deepcopy


@pytest.fixture
def pet_resource(petstore_spec):
    return petstore_spec.resources['pet']


@pytest.mark.xfail(
    condition=sys.version_info[:3] == (3, 5, 0),
    reason=(
        "Deepcopy of lru_cache-ed items does not work properly "
        "on Python 3.5.0. https://bugs.python.org/issue25447",
    ),
)
def test_resource_instance_is_deep_copyable(pet_resource):
    check_object_deepcopy(pet_resource)
