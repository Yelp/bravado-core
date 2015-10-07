import pytest

from jsonref import JsonRef

from bravado_core.spec import replace_jsonref_proxies_callback


@pytest.fixture
def pet_model_spec():
    return {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string'
            }
        }
    }


@pytest.fixture
def pet_proxy(pet_model_spec):
    ref_obj = {'$ref': '#/definitions/Pet'}
    pet_proxy = JsonRef(ref_obj)
    pet_proxy.__subject__ = pet_model_spec
    return pet_proxy


@pytest.fixture
def response_spec(pet_proxy):
    return {
        'description': 'A pet',
        'schema': pet_proxy
    }


@pytest.fixture
def pet_proxies(pet_proxy):
    return [pet_proxy]


def test_replaces_jsonref_proxy_in_dict(response_spec, pet_model_spec):
    assert type(response_spec['schema']) == JsonRef
    replace_jsonref_proxies_callback(response_spec, key='schema')
    assert type(response_spec['schema']) == dict
    assert response_spec['schema'] == pet_model_spec


def test_replaces_jsonref_proxy_in_list(pet_proxies, pet_model_spec):
    assert type(pet_proxies[0]) == JsonRef
    replace_jsonref_proxies_callback(pet_proxies, key=0)
    assert type(pet_proxies[0]) == dict
    assert pet_proxies[0] == pet_model_spec


def test_noop_when_not_jsonref_proxy(response_spec, pet_model_spec):
    response_spec['schema'] == pet_model_spec
    replace_jsonref_proxies_callback(response_spec, key='schema')
    assert response_spec['schema'] == pet_model_spec
