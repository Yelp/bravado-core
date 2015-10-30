from mock import patch
import pytest

from bravado_core.spec import Spec


def assert_validate_call_count(expected_call_count, config, petstore_dict):
    spec = Spec(petstore_dict, config=config)
    with patch('bravado_core.spec.validator20.validate_spec') as m_validate:
        spec.build()
    assert expected_call_count == m_validate.call_count


@pytest.mark.xfail(run=False,
                   reason='Re-enable when ssv supporte recursive refs')
def test_validate_swagger_spec(petstore_dict):
    assert_validate_call_count(
        1, {'validate_swagger_spec': True}, petstore_dict)


@pytest.mark.xfail(run=False,
                   reason='Re-enable when ssv supporte recursive refs')
def test_dont_validate_swagger_spec(petstore_dict):
    assert_validate_call_count(
        0, {'validate_swagger_spec': False}, petstore_dict)
