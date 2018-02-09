# -*- coding: utf-8 -*-
import pytest
from mock import patch
from swagger_spec_validator.common import SwaggerValidationError

from bravado_core.spec import Spec
from tests.validate.conftest import email_address_format


def assert_validate_call_count(expected_call_count, config, petstore_dict):
    spec = Spec(petstore_dict, config=config)
    with patch('bravado_core.spec.validator20.validate_spec') as m_validate:
        spec.build()
    assert expected_call_count == m_validate.call_count


def test_validate_swagger_spec(petstore_dict):
    assert_validate_call_count(
        expected_call_count=1,
        config={'validate_swagger_spec': True},
        petstore_dict=petstore_dict,
    )


def test_dont_validate_swagger_spec(petstore_dict):
    assert_validate_call_count(
        expected_call_count=0,
        config={'validate_swagger_spec': False},
        petstore_dict=petstore_dict,
    )


def test_validate_swagger_spec_failure(petstore_dict):
    # induce failure
    del petstore_dict['swagger']
    spec = Spec(petstore_dict)
    with pytest.raises(SwaggerValidationError) as excinfo:
        spec.build()
    assert "'swagger' is a required property" in str(excinfo.value)


def test_build_with_custom_format(petstore_dict):
    assert_validate_call_count(
        expected_call_count=1,
        config={'formats': [email_address_format]},
        petstore_dict=petstore_dict,
    )


@pytest.mark.parametrize(
    'internally_dereference_refs',
    [
        True,
        False,
    ]
)
def test_build_with_internally_dereference_refs(petstore_dict, internally_dereference_refs):
    spec = Spec(
        petstore_dict,
        config={'internally_dereference_refs': internally_dereference_refs}
    )
    assert spec.deref == spec._force_deref
    spec.build()
    assert (spec.deref == spec._force_deref) == (not internally_dereference_refs)


def test_not_object_x_models_are_not_generating_models(minimal_swagger_dict):
    minimal_swagger_dict['definitions']['Pets'] = {
        'type': 'array',
        'items': {
            'type': 'string'
        },
        'x-model': 'Pets'
    }
    swagger_spec = Spec(minimal_swagger_dict)
    swagger_spec.build()
    assert not swagger_spec.definitions
