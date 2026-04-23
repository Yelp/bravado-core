# -*- coding: utf-8 -*-
try:
    from unittest import mock
except ImportError:
    import mock
import pytest

from bravado_core.model import _bless_models
from bravado_core.spec import Spec


@mock.patch('bravado_core.model.is_dict_like', return_value=False)
def test_bless_models_short_circuit_if_no_dict_like_container(mock_is_dict_like, minimal_swagger_dict):
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'post': {
                'responses': {
                    '200': 'not_valid',
                },
            },
        },
    }
    swagger_spec = Spec(minimal_swagger_dict)
    _bless_models(
        minimal_swagger_dict['paths']['/endpoint']['post']['responses']['200'],
        visited_models={},
        swagger_spec=swagger_spec,
        json_reference='#/paths//endpoint/post/responses/200/schema',
    )
    mock_is_dict_like.assert_called_once_with(minimal_swagger_dict['paths']['/endpoint']['post']['responses']['200'])


@pytest.mark.parametrize(
    'response_schema',
    (
        [1, 2, 3],  # is_dict_like(model_spec)
        {'type': 'string'},  # is_object(model_spec)
        {'in': 'body', 'name': 'body', 'type': 'string'},  # determine_object_type(model_spec)
        {'x-model': 'string'},  # deref(model_spec.get('x-model'))
    ),
)
@mock.patch('bravado_core.model._get_model_name')
def test_bless_models_gets_out_if_initial_pre_conditions_are_not_met(
    mock__get_model_name, minimal_swagger_dict, response_schema,
):
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'post': {
                'responses': {
                    '200': {
                        'description': 'HTTP/200',
                        'schema': response_schema,
                    },
                },
            },
        },
    }
    swagger_spec = Spec(minimal_swagger_dict)
    _bless_models(
        minimal_swagger_dict['paths']['/endpoint']['post']['responses']['200'],
        visited_models={},
        swagger_spec=swagger_spec,
        json_reference='#/paths//endpoint/post/responses/200',
    )
    assert mock__get_model_name.call_count == 0


def test_bless_model_adds_model_marker(minimal_swagger_dict):
    response_schema = {
        'type': 'object',
        'title': 'valid_response',
    }
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'post': {
                'responses': {
                    '200': {
                        'description': 'HTTP/200',
                        'schema': response_schema,
                    },
                },
            },
        },
    }
    swagger_spec = Spec(minimal_swagger_dict)
    _bless_models(
        minimal_swagger_dict['paths']['/endpoint']['post']['responses']['200'],
        visited_models={},
        swagger_spec=swagger_spec,
        json_reference='#/paths//endpoint/post/responses/200/schema',
    )
    assert response_schema.get('x-model') == response_schema['title']


def test_bless_model_does_not_generate_model_tag_if_no_title_is_set(minimal_swagger_dict):
    response_schema = {
        'type': 'object',
    }
    minimal_swagger_dict['paths'] = {
        '/endpoint': {
            'post': {
                'responses': {
                    '200': {
                        'description': 'HTTP/200',
                        'schema': response_schema,
                    },
                },
            },
        },
    }
    swagger_spec = Spec(minimal_swagger_dict)
    _bless_models(
        minimal_swagger_dict['paths']['/endpoint']['post']['responses']['200'],
        visited_models={},
        swagger_spec=swagger_spec,
        json_reference='#/paths//endpoint/post/responses/200',
    )
    assert 'x-model' not in response_schema
