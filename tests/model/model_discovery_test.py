# -*- coding: utf-8 -*-
import mock
import pytest

from bravado_core.model import _run_post_processing
from bravado_core.model import model_discovery
from bravado_core.spec import Spec


@pytest.fixture
def wrap__run_post_processing():
    with mock.patch(
        'bravado_core.model._run_post_processing',
        wraps=_run_post_processing,
    ) as _wrap__run_post_processing:
        yield _wrap__run_post_processing


def test_model_discovery_flow_no_ref_dereference(wrap__run_post_processing, minimal_swagger_dict):
    spec = Spec(
        spec_dict=minimal_swagger_dict,
        config={
            'internally_dereference_refs': False,
        },
    )
    model_discovery(swagger_spec=spec)
    wrap__run_post_processing.assert_called_once_with(spec)


def test_model_discovery_flow_with_ref_dereference(wrap__run_post_processing, minimal_swagger_dict):
    spec = Spec(
        spec_dict=dict(minimal_swagger_dict, definitions={'model': {'type': 'object'}}),
        config={
            'internally_dereference_refs': True,
        },
        origin_url='',
    )
    model_discovery(swagger_spec=spec)

    # _run_post_processing is called 3 times
    # 1. post processing on initial specs
    # 2. post processing on on bravado_core.spec_flattening.flattened_spec
    # 3. post processing to rebuild definitions to remove possible references in the model specs
    assert wrap__run_post_processing.call_count == 3
