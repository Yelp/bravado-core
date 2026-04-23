# -*- coding: utf-8 -*-
import json
from io import StringIO

try:
    from unittest import mock
except ImportError:
    import mock
import pytest
import yaml

from bravado_core.spec import build_http_handlers


def _build_http_client(content):
    mock_response = mock.Mock()
    mock_response.content = StringIO(content)
    mock_response.json.side_effect = lambda *args, **kwargs: json.loads(content)

    mock_http_client = mock.Mock()
    result_func = mock_http_client.request.return_value.result

    result_func.return_value = mock_response

    handlers = build_http_handlers(mock_http_client)

    return handlers, mock_response


@pytest.mark.parametrize('protocol', ['http', 'https'])
def test_yaml_http_handler_with_known_file_extension(protocol):
    test_dict = {"hello": 'world'}
    test_yaml = yaml.dump(test_dict)

    handlers, response = _build_http_client(test_yaml)

    http_handler = handlers[protocol]
    result = http_handler('%s://test.test/yaml/toys.yaml' % protocol)

    assert result == test_dict


@pytest.mark.parametrize('protocol', ['http', 'https'])
def test_yaml_http_handler_with_yaml_content_type(protocol):
    test_dict = {'hello': 'world'}
    test_yaml = yaml.dump(test_dict)

    handlers, response = _build_http_client(test_yaml)
    response.headers = {'content-type': 'application/yaml'}

    http_handler = handlers[protocol]
    result = http_handler('%s://test.test/yaml/toys' % protocol)

    assert result == test_dict


@pytest.mark.parametrize('protocol', ['http', 'https'])
def test_not_yaml_content_type(protocol):
    test_dict = {'hello': 'world'}
    test_json = json.dumps(test_dict)

    handlers, response = _build_http_client(test_json)
    response.headers = {'content-type': 'application/json'}

    http_handler = handlers[protocol]
    result = http_handler('%s://test.test/json/test' % protocol)

    assert result == test_dict


@pytest.mark.parametrize('protocol', ['http', 'https'])
def test_not_yaml_file_name(protocol):
    test_dict = {'hello': 'world'}
    test_json = json.dumps(test_dict)

    handlers, response = _build_http_client(test_json)
    response.headers = {'content-type': 'text/plain'}

    http_handler = handlers[protocol]
    result = http_handler('%s://test.test/json/test.json' % protocol)

    assert result == test_dict
