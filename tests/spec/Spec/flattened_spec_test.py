# -*- coding: utf-8 -*-
import copy
import functools

import mock
import pytest
from six.moves.urllib.parse import urlparse
from swagger_spec_validator import validator20

from bravado_core import spec
from bravado_core.spec import CONFIG_DEFAULTS
from bravado_core.spec import Spec
from bravado_core.spec_flattening import _marshal_uri
from bravado_core.spec_flattening import _warn_if_uri_clash_on_same_marshaled_representation


@mock.patch('bravado_core.spec_flattening.warnings')
def test_no_warning_for_clashed_uris(mock_warnings):
    _warn_if_uri_clash_on_same_marshaled_representation(
        uri_schema_mappings={},
        marshal_uri=functools.partial(
            _marshal_uri,
            origin_uri=None,
        ),
    )
    assert not mock_warnings.called


@mock.patch('bravado_core.spec_flattening.warnings')
def test_warning_for_clashed_uris(mock_warnings):
    clashing_uris = ['path1', 'path2']
    marshaled_uri = 'SameString'

    _warn_if_uri_clash_on_same_marshaled_representation(
        uri_schema_mappings={urlparse(uri): mock.Mock() for uri in clashing_uris},
        marshal_uri=functools.partial(
            lambda *args, **kwargs: marshaled_uri,
            origin_uri=None,
        ),
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
    ]
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
    ]
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
    ]
)
def test_marshal_url(target, expected_marshaled_uri):
    origin_url = '/api_docs/swagger.json'
    marshaled_uri = _marshal_uri(
        target_uri=urlparse(target),
        origin_uri=urlparse(origin_url),
    )
    assert marshaled_uri == expected_marshaled_uri


@mock.patch('bravado_core.spec.build_api_serving_url')
@mock.patch('bravado_core.spec.flattened_spec')
def test_flattened_spec_raises_if_configured_to_not_validate_swagger_specs(
    mock_flattened_dict, mock_build_api_serving_url,
):
    petstore_spec = Spec(mock_flattened_dict, config=dict(CONFIG_DEFAULTS, validate_swagger_spec=False))
    with pytest.raises(RuntimeError) as excinfo:
        petstore_spec.flattened_spec
    assert 'Swagger Specs have to be validated before flattening.' == str(excinfo.value)


@mock.patch('bravado_core.spec.strip_xscope', autospec=True)
@mock.patch('bravado_core.spec.flattened_spec', autospec=True)
@pytest.mark.parametrize('pre_built_spec', [True, False])
def test_flattened_spec_build_specs_if_not_already_built(
    mock_flattened_spec, mock_strip_xscope, minimal_swagger_dict, pre_built_spec
):
    petstore_spec = Spec(minimal_swagger_dict)
    if pre_built_spec:
        petstore_spec.build()

    with mock.patch.object(petstore_spec, 'build', autospec=True) as mock_build:
        petstore_spec.flattened_spec

    if pre_built_spec:
        assert not mock_build.called
    else:
        mock_build.assert_called_once_with()

    mock_flattened_spec.assert_called_once_with(swagger_spec=petstore_spec)
    mock_strip_xscope.assert_called_once_with(mock_flattened_spec.return_value)


@pytest.mark.parametrize(
    'has_origin_url', [True, False]
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
