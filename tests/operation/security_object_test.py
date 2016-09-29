from mock import Mock
import pytest
from six import iteritems

from bravado_core.exception import SwaggerSchemaError
from bravado_core.request import IncomingRequest, unmarshal_request
from bravado_core.resource import build_resources
from bravado_core.spec import Spec
from jsonschema import ValidationError


def test_op_with_security_in_op_without_security_defs(
        specs_with_security_obj_in_op_and_no_security_specs,
):
    with pytest.raises(SwaggerSchemaError):
        build_resources(Spec(
            specs_with_security_obj_in_op_and_no_security_specs,
        ))


def test_op_with_security_in_root_without_security_defs(
        specs_with_security_obj_in_root_and_no_security_specs,
):
    with pytest.raises(SwaggerSchemaError):
        build_resources(Spec(
            specs_with_security_obj_in_root_and_no_security_specs,
        ))


def _validate_resources(resources, security_definitions_spec):
    resource = resources.get('pet')
    assert resource is not None
    for security_option, security_obj in iteritems(security_definitions_spec):
        operation = getattr(resource, 'findPetsByStatus')
        assert operation is not None
        assert security_obj in operation.security_objects
        if security_option == 'apiKey':
            assert len(operation.params) == 2
            assert security_obj['name'] in operation.params
        else:
            assert len(operation.params) == 1


def test_op_with_security_in_op_with_security_defs(
        specs_with_security_obj_in_op_and_security_specs,
):
    security_definitions_spec = \
        specs_with_security_obj_in_op_and_security_specs['securityDefinitions']
    _validate_resources(
        resources=build_resources(Spec(
            specs_with_security_obj_in_op_and_security_specs,
        )),
        security_definitions_spec=security_definitions_spec,
    )


def test_op_with_security_in_root_with_security_defs(
        specs_with_security_obj_in_root_and_security_specs,
):
    security_definitions_spec = \
        specs_with_security_obj_in_root_and_security_specs['securityDefinitions']  # noqa
    _validate_resources(
        resources=build_resources(Spec(
            specs_with_security_obj_in_root_and_security_specs,
        )),
        security_definitions_spec=security_definitions_spec,
    )


def test_op_with_security_in_root_with_empty_security_spec(
        specs_with_security_obj_in_root_and_empty_security_spec,
):
    resources = build_resources(Spec(
            specs_with_security_obj_in_root_and_empty_security_spec,
    ))

    resource = resources.get('pet')
    assert resource is not None

    operation = getattr(resource, 'findPetsByStatus')
    assert operation is not None
    assert len(operation.security_objects) == 0


def test_correct_request_with_apiKey_security(petstore_spec):
    request = Mock(
        spec=IncomingRequest,
        path={'petId': '1234'},
        headers={'api_key': 'key1'},
    )
    op = petstore_spec.resources['pet'].operations['getPetById']
    unmarshal_request(request, op)


def test_wrong_request_with_apiKey_security(petstore_spec):
    request = Mock(
        spec=IncomingRequest,
        path={'petId': '1234'},
        headers={},
    )
    op = petstore_spec.resources['pet'].operations['getPetById']
    with pytest.raises(ValidationError):
        unmarshal_request(request, op)
