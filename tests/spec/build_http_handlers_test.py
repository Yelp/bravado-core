import json
import os
import requests
import unittest
import yaml


class TestHttpClients(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            from unittest import mock
        except ImportError:
            import mock

        my_path = os.path.abspath(os.path.dirname(__file__))
        content_path = os.path.join(
            my_path, '../../test-data/2.0/',
        )

        def get_request(req):
            url, method = req['url'], req['method']

            http_response = requests.request(method, url)
            assert http_response.status_code == 200, "Failed to get %s" % url

            response = mock.Mock()
            response.result.return_value = http_response

            return response

        http_client = mock.Mock()
        http_client.request.side_effect = get_request

        try:
            from http.server import HTTPServer, SimpleHTTPRequestHandler
        except ImportError:
            from BaseHTTPServer import HTTPServer
            from SimpleHTTPServer import SimpleHTTPRequestHandler

        ext_map = SimpleHTTPRequestHandler.extensions_map
        for file_extension in ('.yaml', '.yml', '.yiml'):
            ext_map[file_extension] = 'application/x-yaml'

        listen_address = ('127.0.0.1', 19283)

        server = HTTPServer(
            listen_address,
            SimpleHTTPRequestHandler,
        )

        import threading
        server_thread = threading.Thread(
            target=server.serve_forever,
        )
        server_thread.daemon = True
        server_thread.start()

        from bravado_core.spec import build_http_handlers
        http_handlers = build_http_handlers(http_client)

        cls._content_path = content_path
        cls._base_url = 'http://%s:%s/test-data/2.0/' % (
            listen_address[0], listen_address[1],
        )
        cls._server = server
        cls._handlers = http_handlers

    def _run_test(self, path, loader):
        http_handler = self._handlers['http']
        http_result = http_handler('%s/%s' % (self._base_url, path))

        expected_content_path = '%s/%s' % (self._content_path, path)
        with open(expected_content_path) as fp:
            expected_dict = loader(fp)

        assert http_result == expected_dict

    def test_yaml_http_handler(self):
        self._run_test('yaml/toys.yaml', yaml.load)

    def test_yml_http_handler(self):
        self._run_test('yaml/swagger.yml', yaml.load)

    def test_yaml_content_type(self):
        self._run_test('weird-extensions/fake.yiml', yaml.load)

    def test_not_yaml_content_type(self):
        self._run_test('weird-extensions/fake.justin', json.load)

    def test_not_yaml_file_name(self):
        self._run_test('x-model/pet.json', json.load)

    def test_http_handler_equals_https_handler(self):
        """
        The HTTPServer class doesn't support https. Instead of
        testing https directly, we'll just make sure that the two handlers
        are identical.
        :return:
        """
        http_handler_id = id(self._handlers['http'])
        https_handler_id = id(self._handlers['https'])
        assert http_handler_id == https_handler_id

    @classmethod
    def tearDownClass(cls):
        cls._server.shutdown()
