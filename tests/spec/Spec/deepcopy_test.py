# -*- coding: utf-8 -*-
import sys

import pytest

from tests.conftest import check_object_deepcopy


@pytest.mark.xfail(
    condition=sys.version_info[:3] == (3, 5, 0),
    reason=(
        "Deepcopy of lru_cache-ed items does not work properly "
        "on Python 3.5.0. https://bugs.python.org/issue25447",
    ),
)
def test_spec_instance_is_deep_copyable(petstore_spec):
    check_object_deepcopy(petstore_spec)
