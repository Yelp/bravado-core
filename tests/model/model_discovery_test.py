# -*- coding: utf-8 -*-
import mock

from bravado_core.model import model_discovery
from bravado_core.spec import Spec


@mock.patch('bravado_core.model._run_post_processing', autospec=True)
def test_model_discovery_flow_no_ref_dereference(mock__run_post_processing, minimal_swagger_dict):
    spec = Spec(
        spec_dict=minimal_swagger_dict,
        config={
            'internally_dereference_refs': False,
        },
    )
    model_discovery(swagger_spec=spec)
    mock__run_post_processing.assert_called_once_with(spec)


@mock.patch('bravado_core.model._run_post_processing', autospec=True)
def test_model_discovery_flow_with_ref_dereference(mock__run_post_processing, minimal_swagger_dict):
    spec = Spec(
        spec_dict=minimal_swagger_dict,
        config={
            'internally_dereference_refs': True,
        },
    )
    model_discovery(swagger_spec=spec)

    # _run_post_processing is called 3 times
    # 1. post processing on initial specs
    # 2. post processing on on bravado_core.spec_flattening.flattened_spec
    # 3. post processing to rebuild definitions to remove possible references in the model specs
    assert mock__run_post_processing.call_count == 3
