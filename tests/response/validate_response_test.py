# -*- coding: utf-8 -*-
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from bravado_core.operation import Operation
from bravado_core.response import OutgoingResponse
from bravado_core.response import validate_response
from bravado_core.spec import Spec


@patch('bravado_core.response.validate_response_headers')
@patch('bravado_core.response.validate_response_body')
def test_skip_when_configured_to_not_validate(mock_validate_response_body, mock_validate_response_headers):
    swagger_spec = Mock(spec=Spec, config={'validate_responses': False})
    op = Mock(spec=Operation, swagger_spec=swagger_spec)
    response = Mock(spec=OutgoingResponse)
    validate_response({'description': 'blah'}, op, response)
    assert mock_validate_response_body.call_count == 0
    assert mock_validate_response_headers.call_count == 0


@patch('bravado_core.response.validate_response_headers')
@patch('bravado_core.response.validate_response_body')
def test_validate_when_configured_validate(mock_validate_response_body, mock_validate_response_headers):
    swagger_spec = Mock(spec=Spec, config={'validate_responses': True})
    op = Mock(spec=Operation, swagger_spec=swagger_spec)
    response = Mock(spec=OutgoingResponse)
    validate_response({'description': 'blah'}, op, response)
    assert mock_validate_response_body.call_count == 1
    assert mock_validate_response_headers.call_count == 1
