# -*- coding: utf-8 -*-
import mock
import pytest

from bravado_core.spec import CONFIG_DEFAULTS
from bravado_core.spec import Spec
from tests.conftest import get_url


@pytest.mark.parametrize(
    'config',
    [
        {},
        CONFIG_DEFAULTS,
        dict(CONFIG_DEFAULTS, validate_swagger_spec=True),
    ]
)
def test_validate_config_succeed(minimal_swagger_dict, minimal_swagger_abspath, config):
    spec = Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath), config=config)
    assert spec.config == dict(CONFIG_DEFAULTS, **config)


@pytest.mark.parametrize(
    'config, expected_warnings_call',
    [
        (
            {'this_is_an_extra_key': True},
            'config this_is_an_extra_key is been removed because is not a recognized config key',
        ),
        (
            {'validate_swagger_spec': False, 'internally_dereference_refs': True},
            'config disabled internally_dereference_refs because validate_swagger_spec has to be enabled',
        ),
    ]
)
@mock.patch('bravado_core.spec.warnings')
def test_validate_config_fail(
    mock_warnings, minimal_swagger_dict, minimal_swagger_abspath, config, expected_warnings_call,
):
    spec = Spec.from_dict(minimal_swagger_dict, origin_url=get_url(minimal_swagger_abspath), config=config)
    assert spec.config != dict(CONFIG_DEFAULTS, **config)
    mock_warnings.warn.assert_called_once_with(message=expected_warnings_call, category=Warning)
