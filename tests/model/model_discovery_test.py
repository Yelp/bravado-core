# -*- coding: utf-8 -*-
import mock

from bravado_core.model import _collect_models
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
def test_model_discovery_flow_with_ref_dereference_with_no_definitions(mock__run_post_processing, minimal_swagger_dict):
    spec = Spec(
        spec_dict=minimal_swagger_dict,
        config={
            'internally_dereference_refs': True,
        },
        origin_url='',
    )
    model_discovery(swagger_spec=spec)

    # _run_post_processing is called 3 times
    # 1. post processing on initial specs
    # 2. post processing on on bravado_core.spec_flattening.flattened_spec
    assert mock__run_post_processing.call_count == 2


@mock.patch('bravado_core.model._run_post_processing', autospec=True)
def test_model_discovery_flow_with_ref_dereference_with_definitions(mock__run_post_processing, minimal_swagger_dict):
    spec = Spec(
        spec_dict=dict(minimal_swagger_dict, definitions={'model': {'type': 'object'}}),
        config={
            'internally_dereference_refs': True,
        },
        origin_url='',
    )

    def _run_post_processing_side_effect(swagger_spec):
        _collect_models(
            container={
                'type': 'object',
                'x-model': 'mock_model',
            },
            json_reference='#/definitions/mock_model/x-model',
            models=spec.definitions,
            swagger_spec=swagger_spec,
        )

    # Side effect is needed to ensure that at least a model has been discovered before
    # flattening process
    mock__run_post_processing.side_effect = _run_post_processing_side_effect
    model_discovery(swagger_spec=spec)

    # _run_post_processing is called 3 times
    # 1. post processing on initial specs
    # 2. post processing on on bravado_core.spec_flattening.flattened_spec
    # 3. post processing to rebuild definitions to remove possible references in the model specs
    assert mock__run_post_processing.call_count == 3
