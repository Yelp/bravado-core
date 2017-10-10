# -*- coding: utf-8 -*-
import pytest

from bravado_core.operation import _sanitize_operation_id


def test_returns_operation_id_from_operation_spec():
    assert 'getPetById' == _sanitize_operation_id('getPetById', 'get', '/pet/{petId}')


def test_returns_generated_operation_id_when_missing_from_operation_spec():
    assert 'get_pet' == _sanitize_operation_id(None, 'get', '/pet')


def test_returns_generated_operation_id_with_path_parameters():
    assert 'get_pet_petId' == _sanitize_operation_id(None, 'get', '/pet/{petId}')


@pytest.mark.parametrize(('operation_id', 'expected'), [
    ('pet.getBy Id', 'pet_getBy_Id'),      # simple case
    ('_getPetById_', 'getPetById'),        # leading/trailing underscore
    ('get__Pet_By__Id', 'get_Pet_By_Id'),  # double underscores
    ('^&#@!$foo%+++:;"<>?/', 'foo'),       # bunch of illegal chars
    ('', 'get_pet_petId'),                 # crazy corner case 1
    (' ', 'get_pet_petId'),                # crazy corner case 2
    ('_', 'get_pet_petId')                 # crazy corner case 3
])
def test_returns_sanitized_operation_id_when_using_illegal_chars(operation_id, expected):
    assert _sanitize_operation_id(operation_id, 'get', '/pet/{petId}') == expected
