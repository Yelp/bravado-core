import pytest
from six import iteritems


def test_security_definition_property_extraction(security_dict, security_spec):
    security_definitions = security_dict['securityDefinitions']
    for security_name, security_spec_dict in iteritems(security_definitions):
        security_object = security_spec.security_definitions[security_name]
        for key, value in iteritems(security_spec_dict):
            assert getattr(security_object, key if key != 'in' else 'location') == value


@pytest.mark.parametrize(
    'resource, operation, expected_scopes',
    [
        ('example1', 'get_example1', [{'apiKey1': []}, {'apiKey2': []}]),
        ('example2', 'get_example2', [{'apiKey3': []}]),
        ('example3', 'get_example3', [{'apiKey1': [], 'apiKey2': []}, {'apiKey2': []}]),
        ('example4', 'get_example4', [{'oauth2': ['write:resource']}]),
        ('example5', 'get_example5', []),
    ]
)
def test_security_scopes(security_spec, resource, operation, expected_scopes):
    def _get_operation():
        return security_spec.resources[resource].operations[operation]

    assert [
        security_requirement.security_scopes
        for security_requirement in _get_operation().security_requirements
    ] == expected_scopes
