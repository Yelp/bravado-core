# -*- coding: utf-8 -*-
try:
    from unittest import mock
except ImportError:
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


@pytest.mark.parametrize(
    'model_dict',
    [
        {
            'properties': {
                'allOf': {
                    'type': 'string',
                },
                'title': {'type': 'string'},
                'type': {'type': 'string'},
            },
            'type': 'object',
        },
    ],
)
def test_model_discovery_for_models_with_not_string_title_x_model(minimal_swagger_dict, model_dict):
    # This test case has been extracted from the Kubernetes Swagger specs
    # https://raw.githubusercontent.com/kubernetes/kubernetes/release-1.15/api/openapi-spec/swagger.json#/definitions/io.k8s.apiextensions-apiserver.pkg.apis.apiextensions.v1beta1.JSONSchemaProps
    spec = Spec.from_dict(spec_dict=dict(minimal_swagger_dict, definitions={'Model': model_dict}))
    assert set(spec.definitions) == {'Model'}
