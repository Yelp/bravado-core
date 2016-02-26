import json
import os
import requests
import unittest
import yaml

try:
    from unittest import mock
except ImportError:
    import mock

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def _run_test(self, path, loader):
    http_handler = self._handlers['http']
    http_result = http_handler('%s/%s' % (self._base_url, path))

    expected_content_path = '%s/%s' % (self._content_path, path)
    with open(expected_content_path) as fp:
        expected_dict = loader(fp)

    assert http_result == expected_dict


def _build_http_client(content):
    mock_response = mock.Mock()
    mock_response.content = StringIO(content)
    mock_response.json.side_effect = lambda *args, **kwargs: json.loads(content)

    mock_http_client = mock.Mock()
    result_func = mock_http_client.request.return_value.result

    result_func.return_value = mock_response

    from bravado_core.spec import build_http_handlers
    handlers = build_http_handlers(mock_http_client)

    return handlers, mock_response


def test_yaml_http_handler_with_known_file_extension():
    test_dict = {"hello": 'world'}
    test_yaml = yaml.dump(test_dict)

    handlers, response = _build_http_client(test_yaml)

    http_handler = handlers['http']
    result = http_handler('http://test.test/yaml/toys.yaml')

    assert result == test_dict


def test_yaml_http_handler_with_yaml_content_type():
    test_dict = {'hello': 'world'}
    test_yaml = yaml.dump(test_dict)

    handlers, response = _build_http_client(test_yaml)
    response.headers = {'content-type': 'application/yaml'}

    http_handler = handlers['http']
    result = http_handler('https://test.test/yaml/toys')

    assert result == test_dict


def test_not_yaml_content_type():
    test_dict = {'hello': 'world'}
    test_json = json.dumps(test_dict)

    handlers, response = _build_http_client(test_json)
    response.headers = {'content-type': 'application/json'}

    http_handler = handlers['http']
    result = http_handler('https://test.test/json/test')

    assert result == test_dict


def test_not_yaml_file_name():
    test_dict = {'hello': 'world'}
    test_json = json.dumps(test_dict)

    handlers, response = _build_http_client(test_json)
    response.headers = {'content-type': 'text/plain'}

    http_handler = handlers['http']
    result = http_handler('https://test.test/json/test.json')

    assert result == test_dict


def test_http_handler_equals_https_handler():
    """
    The HTTPServer class doesn't support https. Instead of
    testing https directly, we'll just make sure that the two handlers
    are identical.
    :return:
    """

    from bravado_core.spec import build_http_handlers
    handlers = build_http_handlers(None)

    http_handler_id = id(handlers['http'])
    https_handler_id = id(handlers['https'])
    assert http_handler_id == https_handler_id
