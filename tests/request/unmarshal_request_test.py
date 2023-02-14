# -*- coding: utf-8 -*-
import pytest
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from bravado_core.exception import SwaggerMappingError
from bravado_core.operation import Operation
from bravado_core.request import IncomingRequest
from bravado_core.request import unmarshal_request


def test_request_with_path_parameter(getPetByIdPetstoreOperation):
    request = Mock(
        spec=IncomingRequest,
        path={'petId': '1234'},
        headers={'api-key': 'key1'},
    )
    # /pet/{pet_id} fits the bill
    request_data = unmarshal_request(request, getPetByIdPetstoreOperation)
    assert request_data['petId'] == 1234
    assert request_data['api-key'] == 'key1'


def test_request_with_no_parameters(petstore_spec):
    request = Mock(spec=IncomingRequest)
    # /user/logout conveniently has no params
    op = petstore_spec.resources['user'].operations['logoutUser']
    request_data = unmarshal_request(request, op)
    assert 0 == len(request_data)


def test_request_with_no_json_and_required_body_parameter(petstore_spec):
    request = Mock(
        spec=IncomingRequest, path={'petId': '1234'},
        json=Mock(side_effect=ValueError("No json here bub")),
    )
    op = petstore_spec.resources['pet'].operations['updatePet']
    with pytest.raises(SwaggerMappingError) as excinfo:
        unmarshal_request(request, op)
    assert "Error reading request body JSON" in str(excinfo.value)


def test_request_with_no_json_and_optional_body_parameter(petstore_spec):
    request = Mock(
        spec=IncomingRequest, path={'petId': '1234'},
        json=Mock(side_effect=ValueError("No json here bub")),
    )
    op = petstore_spec.resources['pet'].operations['updatePet']
    op.op_spec['parameters'][0]['required'] = False
    op = Operation.from_spec(
        swagger_spec=petstore_spec,
        path_name=op.path_name,
        http_method=op.http_method,
        op_spec=op.op_spec,
    )
    assert unmarshal_request(request, op) == {'body': None}
