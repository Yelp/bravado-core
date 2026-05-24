# -*- coding: utf-8 -*-
import copy
import functools
import os

try:
    from unittest import mock
except ImportError:
    import mock
import pytest
from six.moves.urllib.parse import urlparse
from swagger_spec_validator import validator20

from bravado_core import spec
from bravado_core.spec import CONFIG_DEFAULTS
from bravado_core.spec import Spec
from bravado_core.spec_flattening import _marshal_uri
from bravado_core.spec_flattening import _SpecFlattener
from tests.conftest import _read_json
from tests.conftest import get_url


def _spec_flattener(swagger_spec):
    return _SpecFlattener(
        swagger_spec=swagger_spec,
        marshal_uri_function=functools.partial(
            _marshal_uri,
            origin_uri=None,
        ),
    )


@pytest.fixture
def spec_flattener(minimal_swagger_spec):
    return _spec_flattener(minimal_swagger_spec)


@mock.patch('bravado_core.spec_flattening.warnings')
def test_no_warning_for_clashed_uris(mock_warnings, spec_flattener):
    spec_flattener.warn_if_uri_clash_on_same_marshaled_representation({})


@mock.patch('bravado_core.spec_flattening.warnings')
def test_warning_for_clashed_uris(mock_warnings, spec_flattener):
    clashing_uris = ['path1', 'path2']
    marshaled_uri = 'SameString'
    spec_flattener.marshal_uri_function = functools.partial(
        lambda *args, **kwargs: marshaled_uri,
        origin_uri=None,
    )

    spec_flattener.warn_if_uri_clash_on_same_marshaled_representation(
        uri_schema_mappings={urlparse(uri): mock.Mock() for uri in clashing_uris},
    )

    mock_warnings.warn.assert_called_once_with(
        message='{} clashed to {}'.format(', '.join(sorted(clashing_uris)), marshaled_uri),
        category=Warning,
    )


@pytest.mark.parametrize(
    'target',
    [
        '',
        'xhttps://host/file',
    ],
)
def test_marshal_url_exceptions(target):
    with pytest.raises(ValueError) as excinfo:
        _marshal_uri(
            target_uri=urlparse(target),
            origin_uri=None,
        )

    assert 'Invalid target: \'{target}\''.format(target=target) in str(excinfo.value)


@pytest.mark.parametrize(
    'target, expected_marshaled_uri',
    [
        ('/api_docs/file_same_directory.json', 'file:......api_docs..file_same_directory.json'),
        ('file:///api_docs/file_same_directory.json', 'file:......api_docs..file_same_directory.json'),
        ('file:///file_on_previous_directory.json', 'file:......file_on_previous_directory.json'),
        ('file:///directory1/file.json', 'file:......directory1..file.json'),
        ('http://www.service.domain/swagger/specs.json', 'http:....www.service.domain..swagger..specs.json'),
        ('https://www.service.domain/swagger/specs.json', 'https:....www.service.domain..swagger..specs.json'),
        ('/api_docs/file.json#/definitions/object', 'file:......api_docs..file.json|..definitions..object'),
        ('http://host/file.json#/definitions/wired|name', 'http:....host..file.json|..definitions..wired|name'),
    ],
)
def test_marshal_url_no_origin_uri(target, expected_marshaled_uri):
    marshaled_uri = _marshal_uri(
        target_uri=urlparse(target),
        origin_uri=None,
    )
    assert marshaled_uri == expected_marshaled_uri


@pytest.mark.parametrize(
    'target, expected_marshaled_uri',
    [
        ('/api_docs/file_same_directory.json', 'lfile:file_same_directory.json'),
        ('file:///api_docs/file_same_directory.json', 'lfile:file_same_directory.json'),
        ('file:///file_on_previous_directory.json', 'lfile:....file_on_previous_directory.json'),
        ('file:///directory1/file.json', 'lfile:....directory1..file.json'),
        ('http://www.service.domain/swagger/specs.json', 'http:....www.service.domain..swagger..specs.json'),
        ('https://www.service.domain/swagger/specs.json', 'https:....www.service.domain..swagger..specs.json'),
        ('/api_docs/file.json#/definitions/object', 'lfile:file.json|..definitions..object'),
        ('http://host/file.json#/definitions/wired|name', 'http:....host..file.json|..definitions..wired|name'),
    ],
)
def test_marshal_url(target, expected_marshaled_uri):
    origin_url = '/api_docs/swagger.json'
    marshaled_uri = _marshal_uri(
        target_uri=urlparse(target),
        origin_uri=urlparse(origin_url),
    )
    assert marshaled_uri == expected_marshaled_uri


@mock.patch('bravado_core.spec.log', autospec=True)
def test_flattened_spec_warns_if_configured_to_not_validate_swagger_specs(
    mock_log, minimal_swagger_dict,
):
    petstore_spec = Spec.from_dict(minimal_swagger_dict, '', config=dict(CONFIG_DEFAULTS, validate_swagger_spec=False))
    assert petstore_spec.flattened_spec == minimal_swagger_dict
    mock_log.warning.assert_called_once_with(
        'Flattening unvalidated specs could produce invalid specs. '
        'Use it at your risk or enable `validate_swagger_specs`',
    )


@pytest.mark.parametrize(
    'has_origin_url', [True, False],
)
@mock.patch('bravado_core.spec_flattening.warnings')
@mock.patch('bravado_core.spec.build_http_handlers')
@mock.patch('bravado_core.spec.flattened_spec', wraps=spec.flattened_spec)
def test_flattened_spec_warning_if_no_origin_url(
    wrap_flattened_spec, mock_build_http_handlers, mock_warnings, petstore_spec, has_origin_url,
):
    if not has_origin_url:
        petstore_spec.origin_url = None

    petstore_spec.flattened_spec
    wrap_flattened_spec.assert_called_once_with(swagger_spec=petstore_spec)

    if has_origin_url:
        assert not mock_warnings.warn.called
    else:
        mock_warnings.warn.assert_called_once_with(
            message='It is recommended to set origin_url to your spec before flattering it. '
                    'Doing so internal paths will be hidden, reducing the amount of exposed information.',
            category=Warning,
        )


@mock.patch('bravado_core.spec.warnings')
@mock.patch('bravado_core.spec.build_http_handlers')
@mock.patch('bravado_core.spec.flattened_spec')
def test_flattened_spec_cached_result(mock_flattened_spec, mock_build_http_handlers, mock_warnings, petstore_spec):
    petstore_spec.flattened_spec
    petstore_spec.flattened_spec
    assert mock_flattened_spec.call_count == 1


def test_flattened_spec_provide_valid_specs(
    flattened_multi_file_recursive_dict, multi_file_recursive_spec,
):
    flattened_spec = multi_file_recursive_spec.flattened_spec
    validator20.validate_spec(
        # Deep copy needed because validate_spec adds x-scope information
        spec_dict=copy.deepcopy(flattened_spec),
        spec_url='',
        http_handlers={},
    )
    assert flattened_spec == flattened_multi_file_recursive_dict


def test_flattened_specs_with_no_xmodel_tags(multi_file_with_no_xmodel_spec, flattened_multi_file_with_no_xmodel_dict):
    flattened_spec = multi_file_with_no_xmodel_spec.flattened_spec
    validator20.validate_spec(
        # Deep copy needed because validate_spec adds x-scope information
        spec_dict=copy.deepcopy(flattened_spec),
        spec_url='',
        http_handlers={},
    )
    assert flattened_spec == flattened_multi_file_with_no_xmodel_dict


@pytest.mark.parametrize(
    'spec_dict, expected_spec_dict',
    [
        [
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'x-model': 'model',
                    },
                },
            },
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'x-model': 'model',
                    },
                },
            },
        ],
        [
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'x-model': 'different-model',
                    },
                },
            },
            {
                'definitions': {
                    'different-model': {
                        'type': 'object',
                        'x-model': 'different-model',
                    },
                },
            },
        ],
        [
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'x-model': 'different-model',
                    },
                    'different-model': {
                        'type': 'string',
                    },
                },
            },
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'x-model': 'different-model',
                    },
                    'different-model': {
                        'type': 'string',
                    },
                },
            },
        ],
        [
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'properties': {
                            'mod': {
                                '$ref': '#/definitions/model',
                            },
                        },
                        'x-model': 'different-model',
                    },
                },
            },
            {
                'definitions': {
                    'different-model': {
                        'type': 'object',
                        'properties': {
                            'mod': {
                                '$ref': '#/definitions/different-model',
                            },
                        },
                        'x-model': 'different-model',
                    },
                },
            },
        ],
        [
            {
                'definitions': {
                    'model': {
                        'type': 'object',
                        'properties': {
                            'mod': {
                                '$ref': '#/definitions/second-model',
                            },
                        },
                        'x-model': 'different-model',
                    },
                    'second-model': {
                        'type': 'object',
                        'properties': {
                            'mod': {
                                '$ref': '#/definitions/model',
                            },
                        },
                        'x-model': 'second-model',
                    },
                },
            },
            {
                'definitions': {
                    'different-model': {
                        'type': 'object',
                        'properties': {
                            'mod': {
                                '$ref': '#/definitions/second-model',
                            },
                        },
                        'x-model': 'different-model',
                    },
                    'second-model': {
                        'type': 'object',
                        'properties': {
                            'mod': {
                                '$ref': '#/definitions/different-model',
                            },
                        },
                        'x-model': 'second-model',
                    },
                },
            },
        ],
    ],
)
def test_rename_definition_references(spec_flattener, spec_dict, expected_spec_dict):
    assert spec_flattener.rename_definition_references(spec_dict) == expected_spec_dict


def test_referenced_and_discovered_models_are_not_lost_after_flattening(simple_crossfer_spec):
    assert simple_crossfer_spec.flattened_spec['definitions']['pong']['x-model'] == 'pong'


def test_specs_with_none_in_ref_spec(specs_with_none_in_ref_spec, flattened_specs_with_none_in_ref_dict):
    assert specs_with_none_in_ref_spec.flattened_spec == flattened_specs_with_none_in_ref_dict


def test_include_root_definition(minimal_swagger_dict, minimal_swagger_abspath):
    minimal_swagger_dict['definitions'] = {
        'not_used_model': {
            'type': 'object',
        },
    }
    spec_flattener = _spec_flattener(Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath)))

    spec_flattener.include_root_definition()

    fragment_uri = '{}#/definitions/not_used_model'.format(get_url(minimal_swagger_abspath))
    assert spec_flattener.known_mappings['definitions'] == {
        urlparse(fragment_uri): minimal_swagger_dict['definitions']['not_used_model'],
    }


def test_include_discriminated_models(minimal_swagger_dict, minimal_swagger_abspath):
    minimal_swagger_dict['definitions'] = {
        'base': {
            'type': 'object',
            'properties': {
                'discriminator_field': {'type': 'string'},
            },
            'discriminator': 'discriminator_field',
            'required': ['discriminator_field'],
        },
        'not_used_extend_base': {
            'allOf': [
                {'$ref': '#/definitions/base'},
                {
                    'properties': {
                        'text': {'type': 'string'},
                    },
                },
            ],
        },
    }
    spec_flattener = _spec_flattener(Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath)))

    base_fragment_uri = '{}#/definitions/base'.format(get_url(minimal_swagger_abspath))
    spec_flattener.known_mappings['definitions'] = {
        urlparse(base_fragment_uri): minimal_swagger_dict['definitions']['base'],
    }

    spec_flattener.include_discriminated_models()

    not_used_extend_base_fragment_uri = '{}#/definitions/not_used_extend_base'.format(get_url(minimal_swagger_abspath))

    assert spec_flattener.known_mappings['definitions'] == {
        urlparse(base_fragment_uri): minimal_swagger_dict['definitions']['base'],
        urlparse(not_used_extend_base_fragment_uri): {
            'allOf': [
                mock.ANY,  # not checking the exact content as it contains a marshaled reference and x-scope
                minimal_swagger_dict['definitions']['not_used_extend_base']['allOf'][1],
            ],
            'x-model': 'not_used_extend_base',
        },
    }


@pytest.fixture
def models_referenced_by_polymorphic_models_abspath(my_dir):
    return os.path.join(
        os.path.dirname(my_dir),
        'test-data', '2.0', 'models_referenced_by_polymorphic_models', 'swagger.json',
    )


@pytest.fixture
def models_referenced_by_polymorphic_models_dict(models_referenced_by_polymorphic_models_abspath):
    return _read_json(models_referenced_by_polymorphic_models_abspath)


def test_include_discriminated_models_does_recursively_add_new_models(
    models_referenced_by_polymorphic_models_abspath,
    models_referenced_by_polymorphic_models_dict,
):
    spec = Spec.from_dict(
        models_referenced_by_polymorphic_models_dict,
        origin_url=get_url(models_referenced_by_polymorphic_models_abspath),
        config={'internally_dereference_refs': True},
    )
    assert set(spec.definitions) == {
        'Container1', 'Content1',
        'GenericContainer', 'GenericContent',
        'ReferencedFromContainer1', 'ReferencedFromContent1',
    }
