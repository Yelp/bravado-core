# -*- coding: utf-8 -*-
import pytest
from jsonschema.validators import RefResolver
try:
    from unittest.mock import MagicMock, Mock
except ImportError:
    from mock import MagicMock, Mock

from bravado_core.swagger20_validator import ref_validator


@pytest.fixture
def address_target():
    return {
        'type': 'object',
        'properties': {
            'street': {
                'type': 'string',
            },
            'city': {
                'type': 'string',
            },
            'state': {
                'type': 'string',
            },
        },
        'required': ['street', 'city', 'state'],
    }


@pytest.fixture
def address_ref():
    return '#/definitions/Address'


@pytest.fixture
def address_schema(address_ref, annotated_scope):
    return {
        '$ref': address_ref,
        'x-scope': annotated_scope,
    }


@pytest.fixture
def address():
    return {
        'street': '1000 Main St',
        'city': 'Austin',
        'state': 'TX',
    }


@pytest.fixture
def original_scope():
    return ['file:///tmp/swagger.json']


@pytest.fixture
def annotated_scope():
    return [
        'file:///tmp/swagger.json',
        'file:///tmp/models.json',
    ]


@pytest.fixture
def mock_validator(original_scope):
    validator = Mock()
    validator.resolver = Mock(spec=RefResolver)
    validator.resolver._scopes_stack = original_scope
    # Make descend() return an empty list to StopIteration.
    validator.descend.return_value = [Mock()]
    return validator


def test_when_resolve_is_not_None(
    address_target, address, original_scope,
    annotated_scope, address_ref,
    address_schema, mock_validator,
):
    # Verify RefResolver._scopes_stack is replaced by the x-scope
    # annotation's scope stack during the call to RefResolver.resolve(...)

    def assert_correct_scope_and_resolve(*args, **kwargs):
        assert mock_validator.resolver._scopes_stack == annotated_scope
        return 'file:///tmp/swagger.json', address_target

    mock_validator.resolver.resolve = Mock(
        side_effect=assert_correct_scope_and_resolve,
    )

    # Force iteration over generator function
    list(
        ref_validator(
            mock_validator, ref=address_ref, instance=address,
            schema=address_schema,
        ),
    )

    assert mock_validator.resolver.resolve.call_count == 1
    assert mock_validator.resolver._scopes_stack == original_scope


def test_when_resolve_is_None(
    address_target, address, original_scope,
    annotated_scope, address_ref, address_schema,
    mock_validator,
):
    # Verify RefResolver._scopes_stack is replaced by the x-scope
    # annotation's scope stack during the call to RefResolver.resolving(...)

    def assert_correct_scope_and_resolve(*args, **kwargs):
        assert mock_validator.resolver._scopes_stack == annotated_scope
        return 'file:///tmp/swagger.json', address_target

    mock_validator.resolver.resolve = None
    mock_validator.resolver.resolving.return_value = MagicMock(
        side_effect=assert_correct_scope_and_resolve,
    )

    # Force iteration over generator function
    list(
        ref_validator(
            mock_validator, ref=address_ref, instance=address,
            schema=address_schema,
        ),
    )
    assert mock_validator.resolver.resolving.call_count == 1
    assert mock_validator.resolver._scopes_stack == original_scope
