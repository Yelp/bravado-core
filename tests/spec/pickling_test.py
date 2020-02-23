# -*- coding: utf-8 -*-
import pytest
from six.moves.cPickle import dumps
from six.moves.cPickle import loads

from bravado_core.spec import Spec
from tests.conftest import get_url


@pytest.mark.parametrize('validate_swagger_spec', [True, False])
@pytest.mark.parametrize('internally_dereference_refs', [True, False])
def test_ensure_spec_is_pickable(petstore_dict, petstore_abspath, internally_dereference_refs, validate_swagger_spec):
    spec = Spec.from_dict(
        spec_dict=petstore_dict,
        origin_url=get_url(petstore_abspath),
        config={
            'validate_swagger_spec': validate_swagger_spec,
            'internally_dereference_refs': internally_dereference_refs,
        },
    )
    assert spec.is_equal(loads(dumps(spec)))
