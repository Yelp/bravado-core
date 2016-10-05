from mock import Mock
import pytest
from six import iteritems

from bravado_core.exception import SwaggerSchemaError, SwaggerSecurityValidationError
from bravado_core.request import IncomingRequest, unmarshal_request
from bravado_core.resource import build_resources
from bravado_core.spec import Spec


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
        assert len(operation.security_requirements) == len(security_definitions_spec)
        assert operation.security_requirements[0].security_definitions
        if security_option == 'apiKey':
            assert len(operation.params) == 2
            assert security_obj['name'] in operation.params
            assert len(operation.security_parameters) == 1
        else:
            assert len(operation.params) == 1
            assert len(operation.security_parameters) == 0


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
    assert len(operation.security_requirements) == 0


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
    with pytest.raises(SwaggerSecurityValidationError):
        unmarshal_request(request, op)


@pytest.mark.parametrize(
    'resource, operation, expected_combinations',
    [
        ('example1', 'get_example1', (('apiKey1',), ('apiKey2',))),
        ('example2', 'get_example2', (('apiKey3',),)),
        ('example3', 'get_example3', (('apiKey1', 'apiKey2',), ('apiKey2',))),
        ('example4', 'get_example4', ()),
    ]
)
def test_security_parameters_selection(
        security_spec,
        resource,
        operation,
        expected_combinations,
):
    op = security_spec.resources[resource].operations[operation]
    assert set(map(tuple, op.acceptable_security_definition_combinations)) == set(expected_combinations)


def test_security_parameter_cannot_override_path_or_operation_parameter(
        security_dict,
):
    security_dict['paths']['/example1']['get']['parameters'] = [{
        'description': 'sec1 as query parameter',
        'required': True,
        'in': 'query',
        'type': 'integer',
        'name': 'apiKey1',
    }]

    with pytest.raises(SwaggerSchemaError):
        Spec.from_dict(security_dict)


@pytest.mark.parametrize(
    'resource, operation, headers, expect_to_raise',
    [
        ('example1', 'get_example1', {'sec1': 'sec1', 'sec2': 'sec2'}, True),
        ('example2', 'get_example2', {}, True),
        ('example3', 'get_example3', {'sec1': 'sec1', 'sec2': 'sec2'}, False),
    ]
)
def test_only_one_security_definition_in_use_at_time(
        security_spec,
        resource,
        operation,
        headers,
        expect_to_raise,
):
    request = Mock(
        spec=IncomingRequest,
        headers=headers,
    )

    op = security_spec.resources[resource].operations[operation]
    try:
        with pytest.raises(SwaggerSecurityValidationError):
            unmarshal_request(request, op)
    except:
        if expect_to_raise:
            raise
