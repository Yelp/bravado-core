# -*- coding: utf-8 -*-
try:
    from unittest import mock
except ImportError:
    import mock
import pytest
from six.moves.cPickle import dumps
from six.moves.cPickle import loads

from bravado_core.spec import Spec
from tests.conftest import get_url


@pytest.mark.parametrize('validate_swagger_spec', [True, False])
@pytest.mark.parametrize('internally_dereference_refs', [True, False])
def test_ensure_spec_is_pickleable(petstore_dict, petstore_abspath, internally_dereference_refs, validate_swagger_spec):
    spec = Spec.from_dict(
        spec_dict=petstore_dict,
        origin_url=get_url(petstore_abspath),
        config={
            'validate_swagger_spec': validate_swagger_spec,
            'internally_dereference_refs': internally_dereference_refs,
        },
    )
    assert spec.is_equal(loads(dumps(spec)))


def test_ensure_warning_presence_in_case_of_version_mismatch(petstore_spec):
    with mock.patch('bravado_core.spec._version', '0.0.0'):
        petstore_pickle = dumps(petstore_spec)

    with pytest.warns(UserWarning, match='different bravado-core version.*created by version 0.0.0, current version'):
        restored_petstore_spec = loads(petstore_pickle)
    assert petstore_spec.is_equal(restored_petstore_spec)
