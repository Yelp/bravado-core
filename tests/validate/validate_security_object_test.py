import pytest

from bravado_core.exception import SwaggerValidationError
from bravado_core.validate import validate_security_object


@pytest.mark.parametrize(
    'resource, operation, request_data',
    [
        ('example1', 'get_example1', {'apiKey1': 'key'}),
        ('example1', 'get_example1', {'apiKey2': 'key'}),
        ('example2', 'get_example2', {'apiKey3': 'key'}),
        ('example3', 'get_example3', {'apiKey1': 'key', 'apiKey2': 'key'}),
        ('example3', 'get_example3', {'apiKey2': 'key'}),
        ('example4', 'get_example4', {}),
        ('example5', 'get_example5', {}),
    ]
)
def test_validate_correct_security_objects(security_spec, resource, operation, request_data):
    op = security_spec.resources[resource].operations[operation]
    validate_security_object(op, request_data)


@pytest.mark.parametrize(
    'resource, operation, request_data',
    [
        ('example1', 'get_example1', {}),
        ('example1', 'get_example1', {'apiKey1': 'key', 'apiKey2': 'key'}),
        ('example3', 'get_example3', {'apiKey1': 'key', 'apiKey3': 'key'}),
    ]
)
def test_validate_incorrect_security_objects(security_spec, resource, operation, request_data):
    op = security_spec.resources[resource].operations[operation]
    with pytest.raises(SwaggerValidationError):
        validate_security_object(op, request_data)
