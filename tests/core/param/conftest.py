import pytest

from bravado.core.spec import Spec


@pytest.fixture
def empty_swagger_spec():
    return Spec(spec_dict={})
