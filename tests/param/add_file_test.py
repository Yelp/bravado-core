# -*- coding: utf-8 -*-
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation
from bravado_core.param import add_file
from bravado_core.param import Param


def test_single_file(empty_swagger_spec):
    request = {}
    file_contents = "I am the contents of a file"
    op = Mock(spec=Operation, consumes=['multipart/form-data'])
    param_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo',
    }
    param = Param(empty_swagger_spec, op, param_spec)
    add_file(param, file_contents, request)
    expected_request = {
        'files': [('photo', ('photo', 'I am the contents of a file'))],
    }
    assert expected_request == request


def test_single_named_file(empty_swagger_spec):
    request = {}
    file_name = "iamfile.name"
    file_contents = "I am the contents of a file"
    op = Mock(spec=Operation, consumes=['multipart/form-data'])
    param_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo',
    }
    param = Param(empty_swagger_spec, op, param_spec)
    add_file(param, (file_name, file_contents), request)
    expected_request = {
        'files': [('photo', (file_name, 'I am the contents of a file'))],
    }
    assert expected_request == request


def test_multiple_files(empty_swagger_spec):
    request = {}
    file1_contents = "I am the contents of a file1"
    file2_contents = "I am the contents of a file2"
    op = Mock(spec=Operation, consumes=['multipart/form-data'])
    param1_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo',
    }
    param2_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'headshot',
    }

    param1 = Param(empty_swagger_spec, op, param1_spec)
    param2 = Param(empty_swagger_spec, op, param2_spec)
    add_file(param1, file1_contents, request)
    add_file(param2, file2_contents, request)
    expected_request = {
        'files': [
            ('photo', ('photo', 'I am the contents of a file1')),
            ('headshot', ('headshot', 'I am the contents of a file2')),
        ],
    }
    assert expected_request == request


def test_mime_type_not_found_in_consumes(empty_swagger_spec):
    request = {}
    file_contents = "I am the contents of a file"
    op = Mock(spec=Operation, operation_id='upload_photos', consumes=[])
    param_spec = {
        'type': 'file',
        'in': 'formData',
        'name': 'photo',
    }
    param = Param(empty_swagger_spec, op, param_spec)
    with pytest.raises(SwaggerMappingError) as excinfo:
        add_file(param, file_contents, request)
    assert "not found in list of supported mime-types" in str(excinfo.value)
