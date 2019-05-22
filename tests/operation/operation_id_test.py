# -*- coding: utf-8 -*-
import pytest

from bravado_core.operation import Operation
from bravado_core.spec import Spec


def test_returns_operation_id_from_operation_spec():
    spec = Spec(spec_dict={})
    operation_spec = {'operationId': 'getPetById'}
    operation = Operation(spec, '/pet/{petId}', 'get', operation_spec)
    assert 'getPetById' == operation.operation_id


def test_returns_generated_operation_id_when_missing_from_operation_spec():
    spec = Spec(spec_dict={})
    operation_spec = {}
    operation = Operation(spec, '/pet', 'get', operation_spec)
    assert 'get_pet' == operation.operation_id


@pytest.mark.parametrize(
    'http_method', ['', '_'],
)
def test_operation_id_raises_when_missing_operation_id_and_possible_sanitization_results_in_empty_string(http_method):
    spec = Spec(spec_dict={})
    operation_spec = {}
    operation = Operation(spec, '/', http_method, operation_spec)
    with pytest.raises(ValueError) as excinfo:
        operation.operation_id
    assert 'empty operation id starting from operation_id=None, http_method={} and path_name=/'.format(
        http_method,
    ) in str(excinfo.value)


def test_returns_generated_operation_id_with_path_parameters():
    spec = Spec(spec_dict={})
    operation_spec = {}
    operation = Operation(spec, '/pet/{petId}', 'get', operation_spec)
    assert 'get_pet_petId' == operation.operation_id


@pytest.mark.parametrize(
    ('input', 'expected'), [
        ('pet.getBy Id', 'pet_getBy_Id'),      # simple case
        ('_getPetById_', 'getPetById'),        # leading/trailing underscore
        ('get__Pet_By__Id', 'get_Pet_By_Id'),  # double underscores
        ('^&#@!$foo%+++:;"<>?/', 'foo'),       # bunch of illegal chars
        ('', 'get_pet_petId'),                 # crazy corner case 1
        (' ', 'get_pet_petId'),                # crazy corner case 2
        ('_', 'get_pet_petId'),                 # crazy corner case 3
    ],
)
def test_returns_sanitized_operation_id_when_using_illegal_chars(input, expected):
    spec = Spec(spec_dict={})
    operation_spec = {'operationId': input}
    operation = Operation(spec, '/pet/{petId}', 'get', operation_spec)
    assert expected == operation.operation_id
